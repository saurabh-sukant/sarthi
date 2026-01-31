from app.agents.guardrail_agent import GuardrailAgent

class GuardrailService:
    def __init__(self):
        self.agent = GuardrailAgent()

    async def validate_input(self, content: str):
        return await self.agent.validate_input(content)

    async def validate_output(self, content: str):
        return await self.agent.validate_output(content)

    async def should_escalate(self, content: str, context=None):
        return await self.agent.should_escalate(content, context)