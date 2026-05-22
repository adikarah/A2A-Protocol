# =============================================================================
# agents/trip_planner/task_manager.py
# =============================================================================
# Purpose:
# Connects TripPlannerAgent to A2A protocol.
# Handles:
# - Receiving tasks
# - Calling TripPlannerAgent
# - Returning structured response
# =============================================================================

import logging

from version_3_multi_agent.server.task_manager import InMemoryTaskManager
from version_3_multi_agent.models.request import SendTaskRequest, SendTaskResponse
from version_3_multi_agent.models.task import Message, TaskStatus, TaskState, TextPart

from version_3_multi_agent.agents.trip_planner.agent import TripPlannerAgent

logger = logging.getLogger(__name__)


class TripPlannerTaskManager(InMemoryTaskManager):
    """
    Adapter layer between A2A protocol and TripPlannerAgent logic.
    """

    def __init__(self, agent: TripPlannerAgent):
        super().__init__()
        self.agent = agent

    def _get_user_text(self, request: SendTaskRequest) -> str:
        """
        Extract user message text from request.
        """
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Main handler for incoming tasks.
        """

        logger.info(f"TripPlannerTaskManager received task {request.params.id}")

        # Step 1: Store task
        task = await self.upsert_task(request.params)

        # Step 2: Extract input
        user_text = self._get_user_text(request)

        # Step 3: Call agent
        result = await self.agent.invoke(
            user_text,
            request.params.sessionId
        )

        # Step 4: Wrap response
        reply = Message(
            role="agent",
            parts=[TextPart(text=result)]
        )

        # Step 5: Update task
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(reply)

        # Step 6: Return response
        return SendTaskResponse(id=request.id, result=task)