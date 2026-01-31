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
        graph.add_node("reasoning", self._reasoning)
        graph.add_node("generation", self._generation)
        graph.add_node("output_guardrail", self._output_guardrail)

        # Define edges
        graph.set_entry_point("input_guardrail")
        graph.add_edge("input_guardrail", "retrieval")
        graph.add_edge("retrieval", "reasoning")
        graph.add_edge("reasoning", "generation")
        graph.add_edge("generation", "output_guardrail")
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
                "reasoning_summary": ""
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

    async def _reasoning(self, state: OrchestratorState) -> OrchestratorState:
        execution_id = state["execution_id"]
        query = state.get("masked_query", state.get("query"))
        docs = state.get("retrieved_docs", {})
        memory = state.get("retrieved_memory", {})
        log_observability_event(datetime.utcnow(), "agent_started", "ReasoningAgent", "Starting reasoning", execution_id=execution_id)

        context = self._combine_context(docs, memory)
        reasoning_prompt = f"Query: {query}\nContext: {context[:2000]}\nProvide a brief reasoning summary."

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
        except AttributeError:
             # Fallback to sync call (older OpenAI)
             response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": reasoning_prompt}],
                max_tokens=300
             )
             state["reasoning_summary"] = response.choices[0].message.content

        log_observability_event(datetime.utcnow(), "agent_completed", "ReasoningAgent", "Reasoning completed", execution_id=execution_id)
        return state

    async def _generation(self, state: OrchestratorState) -> OrchestratorState:
        execution_id = state["execution_id"]
        query = state.get("masked_query", state.get("query"))
        reasoning = state.get("reasoning_summary", "")
        log_observability_event(datetime.utcnow(), "agent_started", "GeneratorAgent", "Generating response", execution_id=execution_id)

        generation_prompt = f"Query: {query}\nReasoning: {reasoning}\nGenerate a helpful response."

        try:
             client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
             response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": generation_prompt}],
                max_tokens=500
             )
             state["final_response"] = response.choices[0].message.content
        except AttributeError:
             response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": generation_prompt}],
                max_tokens=500
             )
             state["final_response"] = response.choices[0].message.content

        log_observability_event(datetime.utcnow(), "agent_completed", "GeneratorAgent", "Response generation completed", execution_id=execution_id)
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

    def _combine_context(self, docs: Dict, memory: Dict) -> str:
        """Combine retrieved documents and memory into context string."""
        context_parts = []
        # Ensure docs/memory are dicts before accessing
        if isinstance(docs, dict) and docs.get("documents"):
            for i, doc in enumerate(docs["documents"][0]):
                context_parts.append(f"Document {i+1}: {doc}")
        if isinstance(memory, dict) and memory.get("documents"):
            for i, mem in enumerate(memory["documents"][0]):
                context_parts.append(f"Memory {i+1}: {mem}")
        return "\n".join(context_parts)