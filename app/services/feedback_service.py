from app.db.sqlite_client import get_memory_items
from app.agents.memory_agent import MemoryAgent
import openai
from app.config import settings

class FeedbackService:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.memory_agent = MemoryAgent()

    async def process_feedback(self, execution_id: str, rating: str, comment: str = None):
        """Process user feedback and update learning."""
        # Log feedback
        print(f"Feedback for {execution_id}: {rating} - {comment}")

        # If negative feedback, analyze and update memory
        if rating == "down" and comment:
            await self._learn_from_feedback(execution_id, comment)

    async def _learn_from_feedback(self, execution_id: str, comment: str):
        """Extract learning from negative feedback."""
        # Use LLM to analyze feedback and create learning
        analysis_prompt = f"""
        User feedback: {comment}
        Execution ID: {execution_id}

        Analyze this feedback and suggest what the system should learn or remember to avoid similar issues in the future.
        Provide a concise learning point.
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=150
        )

        learning_point = response.choices[0].message.content.strip()

        # Store as episodic memory
        await self.memory_agent.write_memory(
            content=f"Learning from feedback: {learning_point}",
            memory_type="EPISODIC",
            source=f"feedback_{execution_id}"
        )