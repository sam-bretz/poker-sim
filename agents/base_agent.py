"""
Base poker agent with common functionality for all specialized agents.
"""

from autogen import ConversableAgent  # type: ignore
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BasePokerAgent(ConversableAgent):
    """Base class for all poker agents with common functionality"""

    def __init__(
        self,
        name: str,
        system_message: str,
        specialty: str,
        llm_config: Dict[str, Any],
        **kwargs,
    ):
        # Enhanced system message with poker context
        enhanced_system_message = f"""
{system_message}

IMPORTANT: You are part of a team of poker experts analyzing hands and providing strategic advice.
Your specialty is: {specialty}

When responding:
1. Stay focused on your area of expertise
2. Provide specific, actionable advice
3. Reference concrete examples when possible
4. Be concise but thorough
5. If asked for a recommendation, provide a clear decision with reasoning

Your responses should be professional and focused on helping the human make better poker decisions.
"""

        super().__init__(
            name=name,
            system_message=enhanced_system_message,
            llm_config=llm_config,
            human_input_mode="NEVER",
            **kwargs,
        )

        self.specialty = specialty
        self.confidence_level = 0.8  # Default confidence

    def analyze_situation(self, situation: Dict[str, Any]) -> str:
        """Analyze a poker situation from this agent's perspective"""
        # To be implemented by subclasses
        return f"{self.name} analyzing situation..."

    def get_recommendation(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Get a structured recommendation from this agent"""
        return {
            "agent": self.name,
            "specialty": self.specialty,
            "recommendation": "No specific recommendation",
            "confidence": self.confidence_level,
            "reasoning": "Base agent - should be overridden",
        }

    def format_poker_context(self, situation: Dict[str, Any]) -> str:
        """Format poker situation for the agent"""
        context_parts = []

        if "position" in situation:
            context_parts.append(f"Position: {situation['position']}")

        if "hole_cards" in situation:
            context_parts.append(f"Hole Cards: {situation['hole_cards']}")

        if "board" in situation:
            context_parts.append(f"Board: {situation['board']}")

        if "pot_size" in situation:
            context_parts.append(f"Pot Size: {situation['pot_size']}")

        if "stack_size" in situation:
            context_parts.append(f"Stack Size: {situation['stack_size']}")

        if "opponents" in situation:
            context_parts.append(f"Opponents: {situation['opponents']}")

        if "action_history" in situation:
            context_parts.append(f"Action: {situation['action_history']}")

        if "bet_to_call" in situation:
            context_parts.append(f"Bet to Call: {situation['bet_to_call']}")

        # Add hand progression history if available
        if "hand_history" in situation and situation["hand_history"]:
            context_parts.append("\nHAND PROGRESSION HISTORY:")
            history = situation["hand_history"]
            for i, state in enumerate(history[:-1], 1):  # Exclude current state
                street = state.get('street', 'unknown').upper()
                action = state.get('action', 'No action recorded')
                pot = state.get('pot_size', 0)
                bet = state.get('bet_to_call', 0)
                board = state.get('board', '')
                
                context_parts.append(f"{i}. {street}: {action}")
                if board:
                    context_parts.append(f"   Board: {board} | Pot: ${pot:.1f} | Bet: ${bet:.1f}")
                else:
                    context_parts.append(f"   Pot: ${pot:.1f} | Bet: ${bet:.1f}")

        return "\n".join(context_parts)
