# =============================================================================
# agents/google_adk/agent.py
# =============================================================================
# Purpose:
# This file defines a very simple AI agent called TellTimeAgent.
# It uses Google's ADK (Agent Development Kit) and Gemini model to respond with the current time.
# =============================================================================


# -----------------------------------------------------------------------------
# Built-in & External Library Imports
# -----------------------------------------------------------------------------

from datetime import datetime
import traceback  # Used to get the current system time

# Gemini-based AI agent provided by Google's ADK
from google.adk.agents.llm_agent import LlmAgent

# ADK services for session, memory, and file-like "artifacts"
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService

# The "Runner" connects the agent, session, memory, and files into a complete system
from google.adk.runners import Runner

# Gemini-compatible types for formatting input/output messages
from google.genai import types

# Load environment variables (like API keys) from a `.env` file
from dotenv import load_dotenv
load_dotenv()  # Load variables like GOOGLE_API_KEY into the system
# This allows you to keep sensitive data out of your code.


# -----------------------------------------------------------------------------
# ExplainAgent: Your AI agent that explain concepts using LLM
# -----------------------------------------------------------------------------

class ExplainAgent:
    # This agent only supports plain text input/output
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        Initialize the TellTimeAgent:
        - Creates the LLM agent (powered by Gemini)
        - Sets up session handling, memory, and a runner to execute tasks
        """
        self._agent = self._build_agent()  # Set up the Gemini agent
        self._user_id = "explain_agent_user"  # Use a fixed user ID for simplicity

        # The Runner is what actually manages the agent and its environment
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),  # For files (not used here)
            session_service=InMemorySessionService(),    # Keeps track of conversations
            memory_service=InMemoryMemoryService(),      # Optional: remembers past messages
        )

    def _build_agent(self) -> LlmAgent:
        """
        Creates and returns a Gemini agent with basic settings.

        Returns:
            LlmAgent: An agent object from Google's ADK
        """
        return LlmAgent(
            model="gemini-3-flash-preview",         # Gemini model version
            name="explain_agent",                  # Name of the agent
            description="Explains concepts, answers questions, and provides detailed responses",    # Description for metadata
            instruction="""
            You are a helpful AI assistant.
            Your job is to:
                - Explain technical concepts clearly
                - Answer user questions in a simple and structured way
                - Provide examples when helpful
            Keep responses concise but informative.
            """  # System prompt
        )

    async def invoke(self, query: str, session_id: str) -> str:
        try:
            query_lower = query.lower()

            # ---------------------------------------
            # 1. Deterministic handling (NO LLM)
            # ---------------------------------------
            if "time" in query_lower:
                return f"The current time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            if "date" in query_lower:
                return f"Today's date is: {datetime.now().strftime('%Y-%m-%d')}"

            # ---------------------------------------
            # 2. LLM handling (Gemini)
            # ---------------------------------------

            # Get or create session
            session = await self._runner.session_service.get_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id
            )

            if session is None:
                session = await self._runner.session_service.create_session(
                    app_name=self._agent.name,
                    user_id=self._user_id,
                    session_id=session_id,
                    state={}
                )

            # Prepare message for LLM
            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=query)]
            )

            # Run LLM
            last_event = None
            async for event in self._runner.run_async(
                    user_id=self._user_id,
                    session_id=session.id,
                    new_message=content
            ):
                last_event = event

            if not last_event or not last_event.content or not last_event.content.parts:
                return "I couldn't generate a response."

            return "\n".join([p.text for p in last_event.content.parts if p.text])

        except Exception as e:
            print(f"Error in ExplainAgent.invoke: {e}")
            traceback.print_exc()

            # ---------------------------------------
            # 3. Fallback (VERY IMPORTANT)
            # ---------------------------------------
            return "LLM is currently unavailable. Please try again."

    async def stream(self, query: str, session_id: str):
        """
        Simulates a "streaming" agent that returns a single reply.
        This is here just to demonstrate that streaming is possible.

        Yields:
            dict: Response payload that says the task is complete and gives the time
        """
        result = await self.invoke(query, session_id)

        yield {
            "is_task_complete": True,
            "content": result
        }
