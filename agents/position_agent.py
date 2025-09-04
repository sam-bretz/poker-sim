"""
Position and Range Agent - Expert in positional strategy and hand ranges.
"""

from typing import Dict, Any, List
from .base_agent import BasePokerAgent

class PositionAgent(BasePokerAgent):
    """Agent specializing in positional play and hand ranges"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        system_message = """
You are the Position and Range Expert for No Limit Texas Hold'em poker.

Your expertise includes:
- Positional advantages and disadvantages
- Opening ranges for each position
- 3-bet and 4-bet ranges
- Defending from blinds
- Position-based betting strategies

POSITION HIERARCHY (6-max table):
1. UTG (Under the Gun) - Tightest range, first to act
2. MP (Middle Position) - Slightly wider than UTG
3. CO (Cutoff) - Good position, can open wider
4. BTN (Button) - Best position, widest opening range
5. SB (Small Blind) - Difficult position, tight defending range
6. BB (Big Blind) - Last to act preflop, wider defending range

OPENING RANGES (approximate):
- UTG: 15-20% of hands (premium hands only)
- MP: 18-25% of hands
- CO: 25-35% of hands
- BTN: 35-50% of hands
- SB: 25-35% of hands (vs BB only)

3-BET RANGES:
- Tight 3-bet range: AA-QQ, AK (value) + some bluffs
- Balanced 3-bet range: Include more value hands and bluffs

Key principles:
1. Play tighter in early position
2. Widen ranges in late position
3. Consider opponent's position when making decisions
4. Use position to gain information and control betting
        """
        
        super().__init__(
            name="PositionAgent",
            system_message=system_message,
            specialty="Position and Hand Ranges",
            llm_config=llm_config
        )
        
        # Define opening ranges for each position
        self.opening_ranges = {
            'utg': ['AA', 'KK', 'QQ', 'JJ', '1010', '99', 'AK', 'AQ', 'AJ', 'KQ'],
            'mp': ['AA', 'KK', 'QQ', 'JJ', '1010', '99', '88', '77', 'AK', 'AQ', 'AJ', 'AT', 'KQ', 'KJ'],
            'co': ['AA', 'KK', 'QQ', 'JJ', '1010', '99', '88', '77', '66', '55', 'AK', 'AQ', 'AJ', 'AT', 'A9', 'KQ', 'KJ', 'QJ'],
            'btn': ['AA', 'KK', 'QQ', 'JJ', '1010', '99', '88', '77', '66', '55', '44', '33', '22', 'AK', 'AQ', 'AJ', 'AT', 'A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2', 'KQ', 'KJ', 'KT', 'K9', 'QJ', 'QT', 'JT'],
            'sb': ['AA', 'KK', 'QQ', 'JJ', '1010', '99', '88', '77', '66', 'AK', 'AQ', 'AJ', 'AT', 'A9', 'KQ', 'KJ', 'QJ'],
            'bb': 'defend_vs_open'  # Defending range depends on opener's position
        }
    
    def get_position_strength(self, position: str) -> int:
        """Get position strength (1-6, higher is better)"""
        position_map = {
            'utg': 1, 'ep': 1,
            'mp': 2, 'mp1': 2, 'mp2': 2,
            'co': 3, 'lp': 3,
            'btn': 4, 'button': 4,
            'sb': 2,  # Good postflop but bad preflop
            'bb': 3   # Good preflop (last to act) but bad postflop
        }
        return position_map.get(position.lower(), 2)
    
    def is_hand_in_range(self, hand: str, position: str) -> bool:
        """Check if a hand is in the opening range for a position"""
        position = position.lower()
        if position not in self.opening_ranges:
            return False
        
        range_hands = self.opening_ranges[position]
        if range_hands == 'defend_vs_open':
            return True  # BB defending range is context-dependent
        
        return hand.upper() in range_hands
    
    def get_positional_advice(self, situation: Dict[str, Any]) -> str:
        """Get position-specific advice"""
        position = situation.get('position', '').lower()
        hole_cards = situation.get('hole_cards', '')
        action_to_us = situation.get('action_history', '')
        
        advice = []
        
        # Position-specific guidance
        position_strength = self.get_position_strength(position)
        
        if position_strength <= 2:  # Early position
            advice.append("Early position - play tight, only strong hands")
            advice.append("Need stronger hands to open due to many players behind")
        elif position_strength == 3:  # Middle position
            advice.append("Middle position - can open slightly wider range")
            advice.append("Still need to be cautious with marginal hands")
        else:  # Late position
            advice.append("Late position - can play wider range")
            advice.append("Use position to steal blinds and control pot size")
        
        # Range advice
        if hole_cards:
            in_range = self.is_hand_in_range(hole_cards, position)
            if in_range:
                advice.append(f"{hole_cards} is in opening range for {position.upper()}")
            else:
                advice.append(f"{hole_cards} is NOT in tight opening range for {position.upper()}")
        
        # Action advice based on what happened before us
        if 'raise' in action_to_us.lower():
            advice.append("Facing a raise - need stronger range to continue")
            advice.append("Consider 3-betting with premium hands and some bluffs")
        elif 'fold' in action_to_us.lower():
            advice.append("Players folded to you - good stealing opportunity if in position")
        
        return "\n".join(advice)
    
    def should_3bet(self, hole_cards: str, position: str, raiser_position: str) -> Dict[str, Any]:
        """Determine if we should 3-bet based on position and hand"""
        
        # Premium 3-bet hands (always 3-bet)
        premium_3bet = ['AA', 'KK', 'QQ', 'AK']
        
        # Position-dependent 3-bet hands
        good_3bet = ['JJ', '1010', 'AQ']
        bluff_3bet = ['A5', 'A4', 'A3', 'A2', 'K9', 'Q9', 'J9', 'T9']
        
        our_pos_strength = self.get_position_strength(position)
        raiser_pos_strength = self.get_position_strength(raiser_position)
        
        should_3bet = False
        reason = ""
        
        if hole_cards in premium_3bet:
            should_3bet = True
            reason = f"{hole_cards} is premium - always 3-bet for value"
        elif hole_cards in good_3bet:
            if our_pos_strength >= raiser_pos_strength:
                should_3bet = True
                reason = f"{hole_cards} is strong enough to 3-bet from {position} vs {raiser_position}"
            else:
                reason = f"{hole_cards} is borderline - be more cautious out of position"
        elif hole_cards in bluff_3bet:
            if our_pos_strength > raiser_pos_strength:
                should_3bet = True
                reason = f"{hole_cards} good 3-bet bluff with position vs {raiser_position} opener"
            else:
                reason = f"{hole_cards} not strong enough to 3-bet out of position"
        else:
            reason = f"{hole_cards} not in 3-bet range - consider calling or folding"
        
        return {
            "should_3bet": should_3bet,
            "reason": reason,
            "hand_category": "premium" if hole_cards in premium_3bet else 
                           "value" if hole_cards in good_3bet else
                           "bluff" if hole_cards in bluff_3bet else "fold/call"
        }
    
    def get_recommendation(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Get position-based recommendation"""
        position = situation.get('position', '')
        hole_cards = situation.get('hole_cards', '')
        action_history = situation.get('action_history', '')
        
        # Get positional advice
        advice = self.get_positional_advice(situation)
        
        # Determine recommendation
        recommendation = "Check position and ranges"
        confidence = 0.7
        
        if hole_cards and position:
            if 'raise' in action_history.lower():
                # Facing a raise - 3-bet analysis
                raiser_pos = self._extract_raiser_position(action_history)
                three_bet_analysis = self.should_3bet(hole_cards, position, raiser_pos)
                
                if three_bet_analysis['should_3bet']:
                    recommendation = f"3-bet with {hole_cards} ({three_bet_analysis['hand_category']})"
                    confidence = 0.8
                else:
                    recommendation = f"Call or fold {hole_cards} - {three_bet_analysis['reason']}"
                    confidence = 0.7
            else:
                # First to act or facing limpers
                if self.is_hand_in_range(hole_cards, position):
                    recommendation = f"Open raise with {hole_cards} from {position.upper()}"
                    confidence = 0.8
                else:
                    recommendation = f"Fold {hole_cards} from {position.upper()} - outside opening range"
                    confidence = 0.9
        
        reasoning = f"Position analysis for {position.upper()}:\n{advice}"
        
        return {
            "agent": self.name,
            "specialty": self.specialty,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    def _extract_raiser_position(self, action_history: str) -> str:
        """Extract the position of the raiser from action history"""
        # Simplified - would need proper parsing in real implementation
        if 'utg' in action_history.lower():
            return 'utg'
        elif 'mp' in action_history.lower():
            return 'mp'
        elif 'co' in action_history.lower():
            return 'co'
        elif 'btn' in action_history.lower() or 'button' in action_history.lower():
            return 'btn'
        elif 'sb' in action_history.lower():
            return 'sb'
        else:
            return 'unknown'