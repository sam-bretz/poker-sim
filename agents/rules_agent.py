"""
Rules and Mechanics Agent - Expert in No Limit Texas Hold'em rules and game mechanics.
"""

from typing import Dict, Any
from .base_agent import BasePokerAgent

class RulesAgent(BasePokerAgent):
    """Agent specializing in poker rules, hand rankings, and game mechanics"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        system_message = """
You are the Rules and Mechanics Expert for No Limit Texas Hold'em poker.

Your expertise includes:
- All poker rules and hand rankings
- Betting structures and action validation
- Tournament vs cash game differences
- Proper game flow and etiquette
- Legal actions in any situation

HAND RANKINGS (from highest to lowest):
1. Royal Flush (A-K-Q-J-10 all same suit)
2. Straight Flush (5 consecutive cards, same suit)
3. Four of a Kind (four cards of same rank)
4. Full House (three of a kind + pair)
5. Flush (5 cards same suit, not consecutive)
6. Straight (5 consecutive cards, mixed suits)
7. Three of a Kind (three cards of same rank)
8. Two Pair (two pairs)
9. One Pair (one pair)
10. High Card (highest card wins)

BETTING RULES:
- Minimum raise must be at least the size of the previous bet or raise
- All-in occurs when a player bets all their chips
- Side pots are created when players have different stack sizes
- String betting is not allowed - action must be clear and complete

When analyzing a situation, always ensure:
1. All proposed actions are legal
2. Betting sizes meet minimum requirements
3. Hand rankings are correctly identified
4. Game flow follows proper sequence
        """
        
        super().__init__(
            name="RulesAgent",
            system_message=system_message,
            specialty="Rules and Game Mechanics",
            llm_config=llm_config
        )
    
    def validate_action(self, action: str, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if a proposed action is legal"""
        validation = {
            "is_valid": True,
            "issues": [],
            "corrected_action": action
        }
        
        bet_to_call = situation.get('bet_to_call', 0)
        stack_size = situation.get('stack_size', 0)
        
        if action.lower().startswith('raise'):
            try:
                # Extract raise amount
                raise_amount = float(action.split()[-1]) if len(action.split()) > 1 else 0
                
                if raise_amount < bet_to_call * 2:  # Minimum raise rule
                    validation["is_valid"] = False
                    validation["issues"].append(f"Minimum raise is {bet_to_call * 2}, you proposed {raise_amount}")
                    validation["corrected_action"] = f"raise {bet_to_call * 2}"
                
                if raise_amount > stack_size:
                    validation["is_valid"] = False
                    validation["issues"].append("Cannot raise more than your stack size")
                    validation["corrected_action"] = "all-in"
                    
            except ValueError:
                validation["is_valid"] = False
                validation["issues"].append("Invalid raise format")
        
        return validation
    
    def evaluate_hand_strength(self, hole_cards: str, board: str = "") -> Dict[str, Any]:
        """Evaluate the strength of a poker hand"""
        # This is a simplified version - would use proper hand evaluator in real implementation
        evaluation = {
            "hand_type": "High Card",
            "strength": 1,  # 1-10 scale
            "description": "Hand strength evaluation"
        }
        
        # Basic pocket pair detection
        if hole_cards and len(hole_cards.split()) == 2:
            card1, card2 = hole_cards.split()
            if card1[0] == card2[0]:  # Same rank
                evaluation["hand_type"] = "Pocket Pair"
                evaluation["strength"] = 5
                
                # Premium pairs
                if card1[0] in ['A', 'K', 'Q']:
                    evaluation["strength"] = 9
                    evaluation["description"] = f"Premium pocket pair ({card1[0]}s)"
                elif card1[0] in ['J', '10', '9']:
                    evaluation["strength"] = 7
                    evaluation["description"] = f"Strong pocket pair ({card1[0]}s)"
                else:
                    evaluation["description"] = f"Pocket pair ({card1[0]}s)"
        
        return evaluation
    
    def get_recommendation(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Get rules-based recommendation"""
        context = self.format_poker_context(situation)
        
        # Validate current situation
        validation_issues = []
        
        # Check for common rule violations
        if situation.get('bet_to_call', 0) > situation.get('stack_size', 0):
            validation_issues.append("Bet to call exceeds stack size - all-in situation")
        
        reasoning = f"From rules perspective:\n{context}"
        if validation_issues:
            reasoning += f"\nRule issues: {'; '.join(validation_issues)}"
        
        recommendation = "Follow proper betting structure"
        confidence = 0.9
        
        # Basic recommendations based on position and action
        position = situation.get('position', '').lower()
        if 'bb' in position and situation.get('bet_to_call', 0) == 0:
            recommendation = "Option to check or bet (you're in big blind)"
        elif situation.get('bet_to_call', 0) > 0:
            recommendation = "Must call, raise, or fold"
        else:
            recommendation = "Option to check or bet"
        
        return {
            "agent": self.name,
            "specialty": self.specialty,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": reasoning,
            "validation_issues": validation_issues
        }