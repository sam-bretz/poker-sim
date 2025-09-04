"""
Math and Odds Agent - Expert in poker mathematics, pot odds, and expected value.
"""

from typing import Dict, Any
from .base_agent import BasePokerAgent


class MathAgent(BasePokerAgent):
    """Agent specializing in poker mathematics and probability calculations"""

    def __init__(self, llm_config: Dict[str, Any]):
        system_message = """
You are the Mathematics and Odds Expert for No Limit Texas Hold'em poker.

Your expertise includes:
- Pot odds and implied odds calculations
- Expected value (EV) analysis
- Probability calculations
- Equity calculations
- Break-even analysis
- Risk-reward ratios

KEY MATHEMATICAL CONCEPTS:

POT ODDS:
- Pot odds = Amount to call / (Pot size + Amount to call)
- Convert to percentage: (Amount to call / Total pot after call) × 100
- Compare to hand equity to determine if call is profitable

EQUITY:
- Your chance of winning the hand at showdown
- Pre-flop equity depends on hole cards vs opponent ranges
- Post-flop equity depends on outs and board texture

OUTS AND ODDS:
- Outs = cards that improve your hand to likely winner
- Rough odds: (Outs × 2) = % chance to improve on next card
- Precise odds use combinatorics and remaining deck

EXPECTED VALUE:
- EV = (Win Probability × Win Amount) - (Lose Probability × Lose Amount)
- Positive EV = profitable long-term decision
- Compare EV of different actions (fold, call, raise)

BETTING MATH:
- Minimum defense frequency = Bet size / (Pot size + Bet size)
- Bluff frequency should make opponent indifferent
- Bet sizing affects required success rate
        """

        super().__init__(
            name="MathAgent",
            system_message=system_message,
            specialty="Mathematics and Probability",
            llm_config=llm_config,
        )

    def calculate_pot_odds(self, pot_size: float, bet_to_call: float) -> Dict[str, Any]:
        """Calculate pot odds and required equity"""
        if bet_to_call <= 0:
            return {"error": "No bet to call"}

        total_pot_after_call = pot_size + bet_to_call
        pot_odds_ratio = bet_to_call / total_pot_after_call
        pot_odds_percentage = pot_odds_ratio * 100

        # Traditional ratio format (e.g., 3:1)
        if pot_odds_ratio != 0:
            ratio = (1 / pot_odds_ratio) - 1
            ratio_string = f"{ratio:.1f}:1"
        else:
            ratio_string = "N/A"

        return {
            "pot_odds_percentage": round(pot_odds_percentage, 1),
            "pot_odds_ratio": ratio_string,
            "required_equity": round(pot_odds_percentage, 1),
            "call_amount": bet_to_call,
            "pot_after_call": total_pot_after_call,
            "getting_odds": f"{ratio_string} odds",
        }

    def calculate_implied_odds(
        self,
        pot_size: float,
        bet_to_call: float,
        implied_winnings: float,
        equity: float,
    ) -> Dict[str, Any]:
        """Calculate implied odds including future winnings"""

        total_potential_winnings = pot_size + implied_winnings
        implied_odds_ratio = bet_to_call / total_potential_winnings
        implied_odds_percentage = implied_odds_ratio * 100

        # Compare to current equity
        profitable = equity > implied_odds_percentage

        return {
            "implied_odds_percentage": round(implied_odds_percentage, 1),
            "total_potential_winnings": total_potential_winnings,
            "current_equity_needed": round(implied_odds_percentage, 1),
            "actual_equity": equity,
            "is_profitable": profitable,
            "equity_surplus": round(equity - implied_odds_percentage, 1),
        }

    def calculate_expected_value(self, actions: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate EV for different actions"""
        evs = {}

        for action, data in actions.items():
            win_prob = data.get("win_probability", 0) / 100
            win_amount = data.get("win_amount", 0)
            lose_prob = 1 - win_prob
            lose_amount = data.get("lose_amount", 0)

            ev = (win_prob * win_amount) - (lose_prob * lose_amount)
            evs[action] = round(ev, 2)

        return evs

    def calculate_breakeven_percentage(self, pot_size: float, bet_size: float) -> float:
        """Calculate breakeven percentage for a bet"""
        return round((bet_size / (pot_size + bet_size)) * 100, 1)

    def estimate_hand_equity(
        self, hole_cards: str, board: str = "", opponents: int = 1
    ) -> Dict[str, Any]:
        """Estimate hand equity (simplified calculation)"""
        # This is a simplified version - real implementation would use Monte Carlo simulation

        equity_estimate = 50.0  # Default
        confidence = "low"

        if not board:  # Pre-flop
            preflop_equities = {
                # Premium hands
                "AA": 85,
                "KK": 82,
                "QQ": 80,
                "JJ": 78,
                "TT": 75,
                "AK": 65,
                "AQ": 60,
                "AJ": 58,
                "AT": 55,
                "KQ": 58,
                "KJ": 55,
                "KT": 52,
                "QJ": 55,
                "QT": 52,
                "JT": 55,
                # Pairs
                "99": 72,
                "88": 69,
                "77": 66,
                "66": 63,
                "55": 60,
                "44": 57,
                "33": 54,
                "22": 51,
                # Suited connectors (approximate)
                "suited_connectors": 45,
                "offsuit_connectors": 40,
            }

            equity_estimate = preflop_equities.get(hole_cards.upper(), 45)
            confidence = "medium"

            # Adjust for number of opponents
            if opponents > 1:
                equity_estimate *= 0.8 ** (opponents - 1)

        else:  # Post-flop - very simplified
            if "pair" in hole_cards.lower():
                equity_estimate = 65  # Rough estimate for made hands
            else:
                equity_estimate = 35  # Drawing hands
            confidence = "low"  # Would need proper calculation

        return {
            "equity_percentage": round(equity_estimate, 1),
            "confidence": confidence,
            "opponents": opponents,
            "board": board or "preflop",
        }

    def analyze_betting_decision(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive mathematical analysis of a betting decision"""

        pot_size = situation.get("pot_size", 0)
        bet_to_call = situation.get("bet_to_call", 0)
        hole_cards = situation.get("hole_cards", "")
        board = situation.get("board", "")
        opponents = situation.get("opponents", 1)

        analysis = {}

        # Calculate pot odds
        if bet_to_call > 0:
            pot_odds = self.calculate_pot_odds(pot_size, bet_to_call)
            analysis["pot_odds"] = pot_odds

        # Estimate equity
        equity_data = self.estimate_hand_equity(hole_cards, board, opponents)
        analysis["equity"] = equity_data

        # EV calculation for fold/call/raise
        if bet_to_call > 0:
            equity_pct = equity_data["equity_percentage"]

            # Simplified EV calculations
            ev_fold = 0  # Always 0

            # EV of calling
            total_pot_after_call = pot_size + bet_to_call
            ev_call = (equity_pct / 100 * total_pot_after_call) - bet_to_call

            # EV of raising (simplified - assumes fold equity)
            fold_equity = 0.3  # Assume 30% fold equity
            ev_raise = (fold_equity * pot_size) + ((1 - fold_equity) * ev_call)

            analysis["expected_values"] = {
                "fold": round(ev_fold, 2),
                "call": round(ev_call, 2),
                "raise": round(ev_raise, 2),
            }

        return analysis

    def get_recommendation(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Get math-based recommendation"""

        analysis = self.analyze_betting_decision(situation)

        recommendation = "Insufficient data for calculation"
        confidence = 0.5
        reasoning_parts = []

        # Pot odds analysis
        if "pot_odds" in analysis:
            pot_odds = analysis["pot_odds"]
            equity = analysis["equity"]["equity_percentage"]
            required_equity = pot_odds["required_equity"]

            reasoning_parts.append(
                f"Pot odds: {pot_odds['getting_odds']} ({required_equity}% equity needed)"
            )
            reasoning_parts.append(f"Estimated equity: {equity}%")

            if equity > required_equity:
                recommendation = (
                    f"CALL - Equity ({equity}%) > Required ({required_equity}%)"
                )
                confidence = 0.8
                reasoning_parts.append("✓ Profitable call based on pot odds")
            else:
                recommendation = (
                    f"FOLD - Equity ({equity}%) < Required ({required_equity}%)"
                )
                confidence = 0.8
                reasoning_parts.append("✗ Unprofitable call based on pot odds")

        # EV analysis
        if "expected_values" in analysis:
            evs = analysis["expected_values"]
            best_action = max(evs.items(), key=lambda x: x[1])

            reasoning_parts.append(f"Expected Values: {evs}")
            reasoning_parts.append(
                f"Best EV action: {best_action[0]} (+{best_action[1]})"
            )

            if best_action[1] > 0:
                recommendation = (
                    f"{best_action[0].upper()} - Best EV (+{best_action[1]})"
                )
                confidence = 0.7

        reasoning = (
            "\n".join(reasoning_parts)
            if reasoning_parts
            else "Mathematical analysis incomplete"
        )

        return {
            "agent": self.name,
            "specialty": self.specialty,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": reasoning,
            "calculations": analysis,
        }
