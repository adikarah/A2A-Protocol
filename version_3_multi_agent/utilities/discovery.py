# =============================================================================
# utilities/discovery.py
# =============================================================================
# Purpose:
# A shared utility module for discovering Agent-to-Agent (A2A) servers.
# It reads a registry of agent base URLs (from a JSON file) and fetches
# each agent's metadata (AgentCard) from the standard discovery endpoint.
# This allows any client or agent to dynamically learn about available agents.
#
# Enhancements:
# - Added informative logging for demo visibility
# - Added safety check when no agents are discovered
# =============================================================================

import os
import json
import logging
from typing import List

import httpx
from version_3_multi_agent.models.agent import AgentCard

logger = logging.getLogger(__name__)


class DiscoveryClient:
    """
    Discovers A2A agents by reading a registry file of URLs and querying
    each one's /.well-known/agent.json endpoint to retrieve an AgentCard.
    """

    def __init__(self, registry_file: str = None):
        """
        Initialize the DiscoveryClient.

        Args:
            registry_file (str, optional): Path to the registry JSON.
        """

        if registry_file:
            self.registry_file = registry_file
        else:
            self.registry_file = os.path.join(
                os.path.dirname(__file__),
                "agent_registry.json"
            )

        # 🔥 NEW: Log which registry is being used
        logger.info(f"Using registry file: {self.registry_file}")

        self.base_urls = self._load_registry()

    def _load_registry(self) -> List[str]:
        """
        Load and parse the registry JSON file into a list of URLs.
        """
        try:
            with open(self.registry_file, "r") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Registry file must contain a JSON list of URLs.")

            # 🔥 NEW: Log loaded URLs
            logger.info(f"Loaded {len(data)} agent URLs from registry")

            return data

        except FileNotFoundError:
            logger.warning(f"Registry file not found: {self.registry_file}")
            return []

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing registry file: {e}")
            return []

    async def list_agent_cards(self) -> List[AgentCard]:
        """
        Fetch AgentCards from all registered agents.
        """
        cards: List[AgentCard] = []

        async with httpx.AsyncClient() as client:
            for base in self.base_urls:
                url = base.rstrip("/") + "/.well-known/agent.json"

                try:
                    response = await client.get(url, timeout=5.0)
                    response.raise_for_status()

                    card = AgentCard.model_validate(response.json())
                    cards.append(card)

                    # Log each discovered agent (VERY useful for demo)
                    logger.info(f"Discovered agent: {card.name} at {base}")

                except Exception as e:
                    logger.warning(f"Failed to discover agent at {url}: {e}")

        # Warn if no agents found
        if not cards:
            logger.warning("No agents discovered. Check registry or running services.")

        return cards