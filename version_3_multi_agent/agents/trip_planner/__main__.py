# =============================================================================
# agents/trip_planner/__main__.py
# =============================================================================
# Purpose:
# Starts the TripPlannerAgent as an Agent-to-Agent (A2A) server.
# - Defines the agent’s metadata (AgentCard)
# - Wraps the TripPlannerAgent logic in a TripPlannerTaskManager
# - Listens for incoming tasks on a configurable host and port
# =============================================================================

import logging
import click

# Generic A2A server
from version_3_multi_agent.server.server import A2AServer

# Agent metadata models
from version_3_multi_agent.models.agent import (
    AgentCard,
    AgentCapabilities,
    AgentSkill
)

# Our Trip Planner logic + adapter
from version_3_multi_agent.agents.trip_planner.task_manager import TripPlannerTaskManager
from version_3_multi_agent.agents.trip_planner.agent import TripPlannerAgent


# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------------
@click.command()
@click.option("--host", default="localhost", help="Host to bind TripPlannerAgent server to")
@click.option("--port", default=10001, help="Port for TripPlannerAgent server")
def main(host: str, port: int):
    """
    Launches the TripPlannerAgent A2A server.
    """

    print(f"\n Starting TripPlannerAgent on http://{host}:{port}/\n")

    # -------------------------------------------------------------------------
    # 1) Define capabilities
    # -------------------------------------------------------------------------
    capabilities = AgentCapabilities(streaming=False)

    # -------------------------------------------------------------------------
    # 2) Define skill metadata
    # -------------------------------------------------------------------------
    skill = AgentSkill(
        id="trip_planning",
        name="Trip Planner Tool",
        description="Creates structured travel plans including itinerary and budget",
        tags=["travel", "trip", "itinerary"],
        examples=[
            "Plan a trip to Goa",
            "2-day trip to Manali under 10k"
        ]
    )

    # -------------------------------------------------------------------------
    # 3) AgentCard (Discovery metadata)
    # -------------------------------------------------------------------------
    agent_card = AgentCard(
        name="TripPlannerAgent",
        description="Plans trips with itinerary, budget, and recommendations",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[skill]
    )

    # -------------------------------------------------------------------------
    # 4) Initialize agent + task manager
    # -------------------------------------------------------------------------
    agent = TripPlannerAgent()
    task_manager = TripPlannerTaskManager(agent=agent)

    # -------------------------------------------------------------------------
    # 5) Start A2A server
    # -------------------------------------------------------------------------
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )

    server.start()


if __name__ == "__main__":
    main()