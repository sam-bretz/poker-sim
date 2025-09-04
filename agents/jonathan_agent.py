"""
Jonathan Little Strategy Agent - RAG-enabled agent with access to WPH knowledge base.
"""

from typing import Dict, Any
from .base_agent import BasePokerAgent
import logging

logger = logging.getLogger(__name__)


class JonathanAgent(BasePokerAgent):
    """Agent with access to Jonathan Little's strategies from Weekly Poker Hand episodes"""

    def __init__(self, llm_config: Dict[str, Any], knowledge_base=None):
        system_message = """
You are the Jonathan Little Strategy Expert, with access to analysis from 100+ Weekly Poker Hand episodes.

Your expertise includes:
- Jonathan Little's strategic concepts and frameworks
- Specific hand examples from the WPH series
- Tournament and cash game strategy distinctions
- GTO concepts explained in practical terms
- Exploitative adjustments to GTO play

When analyzing situations:
1. Reference relevant WPH episodes when available
2. Apply Jonathan's strategic frameworks
3. Consider both GTO and exploitative elements
4. Explain concepts in practical, applicable terms
5. Cite specific examples from the knowledge base

Key Jonathan Little Concepts:
- Hand ranges and polarization
- Bet sizing for value and bluffs
- Position-based strategy adjustments
- Reading opponents and making exploitative plays
- Tournament ICM considerations
- Cash game dynamics
- Mental game and decision-making

Always provide context from the knowledge base when available, and explain how the strategic concepts apply to the current situation.
        """

        super().__init__(
            name="JonathanAgent",
            system_message=system_message,
            specialty="Jonathan Little's Strategies",
            llm_config=llm_config,
        )

        self.knowledge_base = knowledge_base
        self.confidence_level = 0.8

    def search_relevant_strategies(self, situation: Dict[str, Any]) -> str:
        """Search the knowledge base for relevant strategies"""
        if not self.knowledge_base:
            return "Knowledge base not available"

        try:
            # Build search query from situation
            query_parts = []

            if situation.get("hole_cards"):
                query_parts.append(situation["hole_cards"])

            if situation.get("position"):
                query_parts.append(f"position {situation['position']}")

            if situation.get("board"):
                query_parts.append(f"board {situation['board']}")

            if situation.get("action_history"):
                if "raise" in situation["action_history"].lower():
                    query_parts.append("facing raise")
                elif "call" in situation["action_history"].lower():
                    query_parts.append("multiway pot")

            # Add general strategic terms
            query_parts.extend(["strategy", "decision", "analysis"])

            query = " ".join(query_parts)

            # Get context from knowledge base
            context = self.knowledge_base.get_context_for_situation(
                situation=query,
                position=situation.get("position", ""),
                stacks=situation.get("stack_size", ""),
                pot_odds=str(situation.get("pot_size", "")),
            )

            return context

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return "Error accessing strategic knowledge"

    def apply_jonathan_framework(
        self, situation: Dict[str, Any], context: str
    ) -> Dict[str, str]:
        """Apply Jonathan Little's strategic framework to the situation"""

        framework_analysis = {
            "range_analysis": "Analyzing hand ranges based on position and action",
            "bet_sizing": "Optimal bet sizing for value and bluffs",
            "opponent_tendencies": "Reading opponent patterns and adjustments",
            "gto_vs_exploitative": "Balancing theoretical optimal play with exploitative adjustments",
        }

        # Analyze based on situation components
        position = situation.get("position", "").lower()

        # Range analysis
        if position in ["btn", "button", "co", "cutoff"]:
            framework_analysis["range_analysis"] = (
                "Late position allows for wider opening ranges and more bluffing opportunities"
            )
        elif position in ["utg", "ep"]:
            framework_analysis["range_analysis"] = (
                "Early position requires tight ranges and strong hands"
            )
        elif position in ["bb", "sb"]:
            framework_analysis["range_analysis"] = (
                "Blind positions require careful defense frequency calculations"
            )

        # Bet sizing analysis
        if situation.get("pot_size", 0) > 0:
            pot_size = situation["pot_size"]
            if situation.get("bet_to_call", 0) > 0:
                bet_size = situation["bet_to_call"]
                bet_ratio = bet_size / pot_size

                if bet_ratio < 0.5:
                    framework_analysis["bet_sizing"] = (
                        "Small bet size suggests value betting or pot control"
                    )
                elif bet_ratio > 1.0:
                    framework_analysis["bet_sizing"] = (
                        "Large bet size indicates strong hand or big bluff"
                    )
                else:
                    framework_analysis["bet_sizing"] = (
                        "Standard bet sizing, analyze based on range and position"
                    )

        # GTO vs Exploitative decision
        if "aggressive" in context.lower() or "loose" in context.lower():
            framework_analysis["gto_vs_exploitative"] = (
                "Opponent appears loose/aggressive - tighten up and value bet more"
            )
        elif "tight" in context.lower() or "passive" in context.lower():
            framework_analysis["gto_vs_exploitative"] = (
                "Opponent appears tight/passive - can bluff more and value bet thinner"
            )

        return framework_analysis

    def get_recommendation(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendation based on Jonathan Little's strategies"""

        # Search for relevant strategies
        strategic_context = self.search_relevant_strategies(situation)

        # Apply Jonathan's framework
        framework = self.apply_jonathan_framework(situation, strategic_context)

        # Generate recommendation based on context and framework
        recommendation = "Apply balanced GTO approach with exploitative adjustments"
        confidence = 0.7

        # Analyze specific situation elements
        reasoning_parts = []

        if strategic_context and len(strategic_context) > 50:
            reasoning_parts.append("=== Relevant WPH Insights ===")
            reasoning_parts.append(
                strategic_context[:400] + "..."
                if len(strategic_context) > 400
                else strategic_context
            )
            confidence = 0.8

        reasoning_parts.append("\n=== Jonathan Little Framework Analysis ===")
        for aspect, analysis in framework.items():
            reasoning_parts.append(f"{aspect.replace('_', ' ').title()}: {analysis}")

        # Specific recommendations based on situation
        if situation.get("hole_cards") and situation.get("position"):
            hole_cards = situation["hole_cards"]
            position = situation["position"].lower()

            if hole_cards.upper() in ["AA", "KK", "QQ", "AK"]:
                recommendation = (
                    f"Premium hand ({hole_cards}) - bet for value, build pot"
                )
                confidence = 0.9
            elif "btn" in position or "co" in position:
                recommendation = (
                    f"In position with {hole_cards} - can play more aggressively"
                )
                confidence = 0.8
            elif position in ["utg", "ep"] and hole_cards.upper() not in [
                "AA",
                "KK",
                "QQ",
                "JJ",
                "AK",
            ]:
                recommendation = (
                    f"Early position with {hole_cards} - consider tighter play"
                )
                confidence = 0.8

        # Check if we have betting action
        if situation.get("bet_to_call", 0) > 0:
            pot_odds_needed = (
                situation["bet_to_call"]
                / (situation.get("pot_size", 0) + situation["bet_to_call"])
                * 100
            )
            reasoning_parts.append(
                f"\nFacing bet - need {pot_odds_needed:.1f}% equity to call"
            )

        reasoning = "\n".join(reasoning_parts)

        return {
            "agent": self.name,
            "specialty": self.specialty,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": reasoning,
            "strategic_context": strategic_context[:200] + "..."
            if len(strategic_context) > 200
            else strategic_context,
            "framework_analysis": framework,
        }
