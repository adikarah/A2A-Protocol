# =============================================================================
# agents/trip_planner/agent.py
# =============================================================================
# Purpose:
#   A Gemini-powered Trip Planner Agent that:
#     - Accepts user travel queries
#     - Generates structured itineraries
#     - Provides budget breakdown and recommendations
# =============================================================================

import logging
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# Google ADK imports
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner

from google.genai import types

logger = logging.getLogger(__name__)


class TripPlannerAgent:
    """
    A standalone LLM-based agent responsible for travel planning.

    Unlike GreetingAgent:
    - This agent does NOT orchestrate other agents
    - It directly uses Gemini LLM to generate output
    """

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        Initialize the Trip Planner agent:
        - Build LLM agent
        - Setup runner (sessions, memory)
        """

        self._agent = self._build_agent()

        self._user_id = "trip_planner_user"

        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    # -------------------------------------------------------------------------
    # Build LLM Agent
    # -------------------------------------------------------------------------
    def _build_agent(self) -> LlmAgent:
        """
        Create the Gemini-powered agent with instructions.
        """

        return LlmAgent(
            model="gemini-3-flash-preview",  # stable model
            name="trip_planner_agent",
            description="Generates travel itineraries and trip plans",
            instruction=self._system_instruction
        )

    def _system_instruction(self, context) -> str:
        """
        System prompt for the LLM.
        Defines how the agent should respond.
        """

        return (
            "You are a professional travel planner.\n\n"
            "For every request:\n"
            "1. Provide a day-wise itinerary\n"
            "2. Include budget estimation\n"
            "3. Suggest places to visit\n"
            "4. Recommend food and travel tips\n\n"
            "Keep response structured and easy to read."
        )

    # -------------------------------------------------------------------------
    # Main execution method
    # -------------------------------------------------------------------------
    async def invoke(self, query: str, session_id: str) -> str:
        """
        Process user query and return trip plan.

        Steps:
        1. Get or create session
        2. Send query to LLM
        3. Collect response
        4. Return final text
        """

        # Step 1: Get session
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id
        )

        # Step 2: Create if not exists
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id,
                state={}
            )

        # Step 3: Wrap input
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )

        # Step 4: Run agent
        last_event = None
        async for event in self._runner.run_async(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        ):
            last_event = event

        # Step 5: Extract response
        if not last_event or not last_event.content:
            return ""

        return "\n".join([p.text for p in last_event.content.parts if p.text])