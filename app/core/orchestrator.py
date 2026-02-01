import uuid
import inspect
from typing import Dict, Any, TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END
from app.agents.guardrail_agent import GuardrailAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.memory_agent import MemoryAgent
from app.db.sqlite_client import create_execution, update_execution_status, log_observability_event
import openai
from app.config import settings

class OrchestratorState(TypedDict):
    query: str
    execution_id: str
    attachments: list
    mode: str
    guardrail_result: Dict[str, Any]
    retrieval_result: Dict[str, Any]
    reasoning_result: Dict[str, Any]
    generation_result: Dict[str, Any]
    final_response: str
    # Internal keys
    masked_query: str
    retrieved_docs: Any
    retrieved_memory: Any
    reasoning_summary: str
    correlated_memories: list

class Orchestrator:
    def __init__(self):
        self.graph = self._build_graph()
        openai.api_key = settings.openai_api_key

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        graph = StateGraph(OrchestratorState)

        # Add nodes
        graph.add_node("input_guardrail", self._input_guardrail)
        graph.add_node("retrieval", self._retrieval)
        graph.add_node("memory_correlation", self._memory_correlation)
        graph.add_node("reasoning", self._reasoning)
        graph.add_node("generation", self._generation)
        graph.add_node("memory_persistence", self._memory_persistence)
        graph.add_node("output_guardrail", self._output_guardrail)

        # Define edges
        graph.set_entry_point("input_guardrail")
        graph.add_edge("input_guardrail", "retrieval")
        graph.add_edge("retrieval", "memory_correlation")
        graph.add_edge("memory_correlation", "reasoning")
        graph.add_edge("reasoning", "generation")
        graph.add_edge("generation", "memory_persistence")
        graph.add_edge("memory_persistence", "output_guardrail")
        graph.add_edge("output_guardrail", END)

        return graph

    async def run_query(self, query: str, attachments: list, mode: str) -> Dict[str, Any]:
        """Run the orchestration workflow asynchronously."""
        execution_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())

        # Create execution record (Sync DB call is fine here)
        create_execution(execution_id=execution_id, conversation_id=conversation_id, query=query)

        # Log start
        log_observability_event(datetime.utcnow(), "agent_started", "Orchestrator", "Starting orchestration", execution_id=execution_id)

        try:
            # Prepare initial state with defaults for all keys
            initial_state: OrchestratorState = {
                "query": query,
                "execution_id": execution_id,
                "attachments": attachments,
                "mode": mode,
                "guardrail_result": {},
                "retrieval_result": {},
                "reasoning_result": {},
                "generation_result": {},
                "final_response": "",
                "masked_query": query,
                "retrieved_docs": {},
                "retrieved_memory": {},
                "reasoning_summary": "",
                "correlated_memories": []
            }

            # FIX 1: Use ainvoke (Async Invoke) and await it
            # This ensures 'result' is a Dictionary, not a Coroutine
            result = await self.graph.compile().ainvoke(initial_state)

            # Update execution status
            update_execution_status(execution_id, "completed", result.get("final_response") if isinstance(result, dict) else None)

            return {
                "conversation_id": conversation_id,
                "execution_id": execution_id,
                "result": result
            }

        except Exception as e:
            # Capture errors
            update_execution_status(execution_id, "failed", str(e))
            raise e

    # FIX 2: All nodes must be 'async def' to handle async agents properly
    
    async def _input_guardrail(self, state: OrchestratorState) -> OrchestratorState:
        execution_id = state["execution_id"]
        query = state["query"]
        log_observability_event(datetime.utcnow(), "agent_started", "GuardrailAgent", "Validating input", execution_id=execution_id)

        guardrail = GuardrailAgent()
        
        # Check if validation is async
        if inspect.iscoroutinefunction(guardrail.validate_input):
            validation = await guardrail.validate_input(query)
        else:
            validation = guardrail.validate_input(query)

        if not validation["valid"]:
            raise ValueError(f"Input validation failed: {validation['issues']}")

        state["masked_query"] = validation["masked_content"]
        log_observability_event(datetime.utcnow(), "agent_completed", "GuardrailAgent", "Input validation completed", execution_id=execution_id)
        return state

    async def _retrieval(self, state: OrchestratorState) -> OrchestratorState:
        execution_id = state["execution_id"]
        query = state.get("masked_query", state.get("query"))
        log_observability_event(datetime.utcnow(), "agent_started", "RetrievalAgent", "Retrieving documents", execution_id=execution_id)

        retrieval = RetrievalAgent(execution_id)
        
        # FIX 3: Await the retrieval agent (since it uses async DB)
        if inspect.iscoroutinefunction(retrieval.retrieve):
            results = await retrieval.retrieve(query)
        else:
            results = retrieval.retrieve(query)

        state["retrieved_docs"] = results.get("documents", {})
        state["retrieved_memory"] = results.get("memory", {})

        log_observability_event(datetime.utcnow(), "agent_completed", "RetrievalAgent", "Retrieval completed", execution_id=execution_id)
        return state

    async def _memory_correlation(self, state: OrchestratorState) -> OrchestratorState:
        """Read and correlate past memories with retrieved documents."""
        execution_id = state["execution_id"]
        query = state.get("masked_query", state.get("query"))
        
        log_observability_event(datetime.utcnow(), "agent_started", "MemoryAgent", "Correlating memories with retrieved data", execution_id=execution_id)

        memory_agent = MemoryAgent()
        
        # Read memories related to the query using semantic search
        # This will return episodic, semantic, AND conversation memories
        correlated_memories = await memory_agent.read_memory(query=query, top_k=5)
        
        state["correlated_memories"] = correlated_memories
        
        log_observability_event(datetime.utcnow(), "agent_completed", "MemoryAgent", f"Correlated {len(correlated_memories)} memories", execution_id=execution_id)
        return state

    async def _reasoning(self, state: OrchestratorState) -> OrchestratorState:
        execution_id = state["execution_id"]
        query = state.get("masked_query", state.get("query"))
        docs = state.get("retrieved_docs", {})
        memory = state.get("retrieved_memory", {})
        correlated_memories = state.get("correlated_memories", [])
        log_observability_event(datetime.utcnow(), "agent_started", "ReasoningAgent", "Starting reasoning", execution_id=execution_id)

        context = self._combine_context(docs, memory, correlated_memories)
        
        # DEBUG: Log what context was built
        if correlated_memories:
            print(f"\n[DEBUG] Correlated {len(correlated_memories)} memories for context")
            for mem in correlated_memories[:2]:
                print(f"  - Type: {mem.get('type')}, Content: {mem.get('content', '')[:100]}")
        
        # Enhanced reasoning prompt that explicitly considers conversation history
        reasoning_prompt = f"""Query: {query}

Context from documents, memories, and conversation history:
{context[:2000]}

Please provide a brief reasoning summary. Consider:
1. Any information from the documents
2. Any relevant memories from past interactions
3. Any information about the user from the conversation history

Provide your reasoning based on ALL available context, including past conversation history."""

        # Use async OpenAI call if available, or wrap in executor if blocking
        try:
             # Try async call (OpenAI v1+)
             client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
             response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": reasoning_prompt}],
                max_tokens=300
             )
             state["reasoning_summary"] = response.choices[0].message.content
        except (AttributeError, Exception) as e:
             # Fallback: simple reasoning from context if LLM fails
             print(f"LLM reasoning failed ({e}), using context-based fallback")
             
             # Extract key info from context
             docs = state.get("retrieved_docs", {})
             docs_list = docs.get('documents', [[]])[0] if docs.get('documents') else []
             
             if docs_list:
                 context_summary = " ".join([doc[:100] if doc else "" for doc in docs_list[:3]])
                 state["reasoning_summary"] = f"Based on retrieved information: {context_summary}"
             else:
                 state["reasoning_summary"] = "The query was received and processed."

        log_observability_event(datetime.utcnow(), "agent_completed", "ReasoningAgent", "Reasoning completed", execution_id=execution_id)
        return state

    async def _generation(self, state: OrchestratorState) -> OrchestratorState:
        execution_id = state["execution_id"]
        query = state.get("masked_query", state.get("query"))
        reasoning = state.get("reasoning_summary", "")
        correlated_memories = state.get("correlated_memories", [])
        retrieved_docs = state.get("retrieved_docs", {})
        log_observability_event(datetime.utcnow(), "agent_started", "GeneratorAgent", "Generating response", execution_id=execution_id)

        # Detect if user is asking for elaboration
        elaboration_keywords = ["explain", "elaborate", "more details", "tell me more", "describe", "how does", "why", "detailed", "break down", "step by step"]
        wants_elaboration = any(keyword in query.lower() for keyword in elaboration_keywords)

        # Include conversation history in the generation prompt
        memory_context = ""
        if correlated_memories:
            memory_lines = []
            for mem in correlated_memories[:3]:
                memory_lines.append(f"- {mem.get('content', '')[:150]}")
            if memory_lines:
                memory_context = "\n\nConversation History:\n" + "\n".join(memory_lines)

        # Adjust max_tokens and tone based on elaboration request
        max_tokens = 800 if wants_elaboration else 300
        conciseness_instruction = "Keep the response concise and direct." if not wants_elaboration else "Provide detailed explanations as requested."

        generation_prompt = f"""User Query: {query}

Reasoning: {reasoning}
{memory_context}

Generate a helpful, personalized response. Use the reasoning and conversation history to provide accurate information.
{conciseness_instruction}

IMPORTANT GUIDELINES:
- Never use placeholders like [Your Name] or [Customer Name]
- Do NOT include signature lines with placeholders
- If you don't know the user's name, address them naturally without a placeholder
- Be natural and conversational
- If the user has told you information about themselves (like their name), use it naturally in the response"""

        try:
             client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
             response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": generation_prompt}],
                max_tokens=max_tokens
             )
             final_response = response.choices[0].message.content
        except (AttributeError, Exception) as e:
            # Fallback: generate response from retrieved documents if LLM fails
            print(f"LLM generation failed ({e}), using document-based fallback")
            
            # Extract relevant info from retrieved documents
            docs_list = retrieved_docs.get('documents', [[]])[0] if retrieved_docs.get('documents') else []
            
            if docs_list:
                # Build response from documents
                doc_summary = " ".join([doc[:200] if doc else "" for doc in docs_list[:2]])
                final_response = f"Based on available information: {doc_summary[:400]}..."
            else:
                final_response = "I'm currently unable to provide a detailed response due to system limitations, but your query has been logged."

        # Clean up response: remove placeholder patterns and excessive formatting
        final_response = self._cleanup_response(final_response)
        state["final_response"] = final_response

        log_observability_event(datetime.utcnow(), "agent_completed", "GeneratorAgent", "Response generation completed", execution_id=execution_id)
        return state

    async def _memory_persistence(self, state: OrchestratorState) -> OrchestratorState:
        """Store insights and learnings from the interaction as memories."""
        execution_id = state["execution_id"]
        query = state.get("masked_query", state.get("query"))
        reasoning = state.get("reasoning_summary", "")
        generation = state.get("final_response", "")
        
        log_observability_event(datetime.utcnow(), "agent_started", "MemoryAgent", "Persisting interaction to memory", execution_id=execution_id)
        
        memory_agent = MemoryAgent()
        
        # Store the reasoning as semantic memory
        if reasoning:
            try:
                reasoning_memory = f"Query: {query[:100]}...\nReasoning: {reasoning[:200]}"
                await memory_agent.write_memory(
                    content=reasoning_memory,
                    memory_type="semantic",
                    source="orchestrator_reasoning"
                )
            except Exception as e:
                log_observability_event(datetime.utcnow(), "agent_error", "MemoryAgent", f"Failed to store reasoning: {str(e)}", execution_id=execution_id)
        
        # Store the final response as episodic memory
        if generation:
            try:
                episodic_memory = f"Query: {query}\nResponse: {generation[:200]}"
                await memory_agent.write_memory(
                    content=episodic_memory,
                    memory_type="episodic",
                    source="orchestrator_generation"
                )
            except Exception as e:
                log_observability_event(datetime.utcnow(), "agent_error", "MemoryAgent", f"Failed to store episodic memory: {str(e)}", execution_id=execution_id)
        
        log_observability_event(datetime.utcnow(), "agent_completed", "MemoryAgent", "Interaction persisted to memory", execution_id=execution_id)
        return state

    async def _output_guardrail(self, state: OrchestratorState) -> OrchestratorState:
        execution_id = state["execution_id"]
        response = state.get("final_response", "")
        log_observability_event(datetime.utcnow(), "agent_started", "GuardrailAgent", "Validating output", execution_id=execution_id)

        guardrail = GuardrailAgent()
        
        if inspect.iscoroutinefunction(guardrail.validate_output):
             validation = await guardrail.validate_output(response)
        else:
             validation = guardrail.validate_output(response)

        if not validation["valid"]:
            state["final_response"] = "I apologize, but I cannot provide a response to this query due to safety concerns."

        log_observability_event(datetime.utcnow(), "agent_completed", "GuardrailAgent", "Output validation completed", execution_id=execution_id)
        return state

    def _cleanup_response(self, response: str) -> str:
        """Clean up response by removing placeholders and excessive formatting."""
        import re
        
        # Remove placeholder patterns like [Your Name], [Customer Name], [Name], etc.
        response = re.sub(r'\[Your\s+\w+\]', '', response)
        response = re.sub(r'\[(?:Customer|User)\s+\w+\]', '', response)
        response = re.sub(r'\[\w+\]', '', response)
        
        # Remove common signature patterns with placeholders
        response = re.sub(r'Best regards,\s*\n\s*(?:\[.*?\]|$)', '', response, flags=re.IGNORECASE)
        response = re.sub(r'Sincerely,\s*\n\s*(?:\[.*?\]|$)', '', response, flags=re.IGNORECASE)
        response = re.sub(r'Thank you,\s*\n\s*(?:\[.*?\]|$)', '', response, flags=re.IGNORECASE)
        
        # Clean up excessive whitespace
        response = re.sub(r'\n\s*\n\s*\n+', '\n\n', response)  # Remove excessive blank lines
        response = response.strip()
        
        return response

    def _combine_context(self, docs: Dict, memory: Dict, correlated_memories: list = None) -> str:
        """Combine retrieved documents, memory, and correlated historical memories into context string."""
        context_parts = []
        
        # Add retrieved documents
        if isinstance(docs, dict) and docs.get("documents"):
            for i, doc in enumerate(docs["documents"][0]):
                context_parts.append(f"Document {i+1}: {doc}")
        
        # Add retrieved memory
        if isinstance(memory, dict) and memory.get("documents"):
            for i, mem in enumerate(memory["documents"][0]):
                context_parts.append(f"Memory {i+1}: {mem}")
        
        # Add correlated historical memories
        if correlated_memories:
            for i, mem in enumerate(correlated_memories):
                content = mem.get("content") if isinstance(mem, dict) else mem
                context_parts.append(f"Historical Memory {i+1}: {content}")
        
        return "\n".join(context_parts)