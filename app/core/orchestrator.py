import uuid
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

    def run_query(self, query: str, attachments: list, mode: str) -> Dict[str, Any]:
        """Run the orchestration workflow."""
        execution_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())

        # Create execution record
        create_execution()

        # Log start
        log_observability_event(datetime.utcnow(), "agent_started", "Orchestrator", "Starting orchestration", execution_id=execution_id)

        try:
            # Run the graph
            initial_state: OrchestratorState = {
                "query": query,
                "execution_id": execution_id,
                "attachments": attachments,
                "mode": mode,
                "guardrail_result": {},
                "retrieval_result": {},
                "reasoning_result": {},
                "generation_result": {},
                "final_response": ""
            }

            result = self.graph.invoke(initial_state)

            # Update execution status
            update_execution_status(execution_id, "completed", result.get("final_response"))

            return {
                "conversation_id": conversation_id,
                "execution_id": execution_id,
                "result": result
            }

        except Exception as e:
            update_execution_status(execution_id, "failed", str(e))
            raise e

    def _input_guardrail(self, state: OrchestratorState) -> OrchestratorState:
        """Input validation and guardrails."""
        execution_id = state["execution_id"]
        query = state["query"]

        log_observability_event(datetime.utcnow(), "agent_started", "GuardrailAgent", "Validating input", execution_id=execution_id)

        guardrail = GuardrailAgent()
        validation = guardrail.validate_input(query)

        if not validation["valid"]:
            raise ValueError(f"Input validation failed: {validation['issues']}")

        state["masked_query"] = validation["masked_content"]
        log_observability_event(datetime.utcnow(), "agent_completed", "GuardrailAgent", "Input validation completed", execution_id=execution_id)
        return state

    def _retrieval(self, state: OrchestratorState) -> OrchestratorState:
        """Retrieve relevant documents and memory."""
        execution_id = state["execution_id"]
        query = state["masked_query"]

        log_observability_event(datetime.utcnow(), "agent_started", "RetrievalAgent", "Retrieving documents and memory", execution_id=execution_id)

        retrieval = RetrievalAgent(execution_id)
        results = retrieval.retrieve(query)

        state["retrieved_docs"] = results["documents"]
        state["retrieved_memory"] = results["memory"]

        log_observability_event(datetime.utcnow(), "agent_completed", "RetrievalAgent", "Retrieval completed", execution_id=execution_id)
        return state

    def _reasoning(self, state: OrchestratorState) -> OrchestratorState:
        """Reason over retrieved information."""
        execution_id = state["execution_id"]
        query = state["masked_query"]
        docs = state["retrieved_docs"]
        memory = state["retrieved_memory"]

        log_observability_event(datetime.utcnow(), "agent_started", "ReasoningAgent", "Starting reasoning", execution_id=execution_id)

        # Simple reasoning: combine docs and memory
        context = self._combine_context(docs, memory)

        # Generate reasoning summary
        reasoning_prompt = f"""
        Query: {query}
        Context: {context[:2000]}  # Truncate for token limits

        Provide a brief reasoning summary about how to answer this query based on the context.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": reasoning_prompt}],
            max_tokens=300
        )

        state["reasoning_summary"] = response.choices[0].message.content
        log_observability_event(datetime.utcnow(), "agent_completed", "ReasoningAgent", "Reasoning completed", execution_id=execution_id)
        return state

    def _generation(self, state: OrchestratorState) -> OrchestratorState:
        """Generate final response."""
        execution_id = state["execution_id"]
        query = state["masked_query"]
        reasoning = state["reasoning_summary"]
        docs = state["retrieved_docs"]

        log_observability_event(datetime.utcnow(), "agent_started", "GeneratorAgent", "Generating response", execution_id=execution_id)

        # Generate response with citations
        generation_prompt = f"""
        Query: {query}
        Reasoning: {reasoning}

        Generate a helpful response with citations to the source documents.
        Include specific references to incidents or documents where relevant.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": generation_prompt}],
            max_tokens=500
        )

        state["final_response"] = response.choices[0].message.content
        log_observability_event(datetime.utcnow(), "agent_completed", "GeneratorAgent", "Response generation completed", execution_id=execution_id)
        return state

    def _output_guardrail(self, state: OrchestratorState) -> OrchestratorState:
        """Final output validation."""
        execution_id = state["execution_id"]
        response = state["final_response"]

        log_observability_event(datetime.utcnow(), "agent_started", "GuardrailAgent", "Validating output", execution_id=execution_id)

        guardrail = GuardrailAgent()
        validation = guardrail.validate_output(response)

        if not validation["valid"]:
            # Could modify response or escalate
            state["final_response"] = "I apologize, but I cannot provide a response to this query due to safety concerns."

        log_observability_event(datetime.utcnow(), "agent_completed", "GuardrailAgent", "Output validation completed", execution_id=execution_id)
        return state

    def _combine_context(self, docs: Dict, memory: Dict) -> str:
        """Combine retrieved documents and memory into context string."""
        context_parts = []

        # Add documents
        if docs.get("documents"):
            for i, doc in enumerate(docs["documents"][0]):
                context_parts.append(f"Document {i+1}: {doc}")

        # Add memory
        if memory.get("documents"):
            for i, mem in enumerate(memory["documents"][0]):
                context_parts.append(f"Memory {i+1}: {mem}")

        return "\n".join(context_parts)