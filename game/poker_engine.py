"""
Simplified Poker Game Engine for AG2 Poker Assistant.
Focuses on single-hand analysis rather than full game simulation.
"""

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Street(Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"

class Action(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"

@dataclass
class Card:
    """Represents a playing card"""
    rank: str  # '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'
    suit: str  # 'h', 'd', 'c', 's'

    def __str__(self):
        return f"{self.rank}{self.suit}"

    @classmethod
    def from_string(cls, card_str: str):
        """Create card from string like 'Ah' or 'Ks'"""
        if len(card_str) != 2:
            raise ValueError(f"Invalid card string: {card_str}")
        return cls(card_str[0], card_str[1])

@dataclass
class Player:
    """Represents a poker player"""
    name: str
    position: str
    stack: float
    hole_cards: List[Card]
    is_hero: bool = False

    def __str__(self):
        cards_str = " ".join(str(card) for card in self.hole_cards)
        return f"{self.name} ({self.position}): {cards_str} - ${self.stack}"

class SimplifiedPokerEngine:
    """Simplified poker engine for single-hand analysis"""

    def __init__(self):
        self.reset_game()

        # Standard deck
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.suits = ['h', 'd', 'c', 's']

        # Positions for 6-max table
        self.positions_6max = ['UTG', 'MP', 'CO', 'BTN', 'SB', 'BB']

    def reset_game(self):
        """Reset the game state"""
        self.players: List[Player] = []
        self.board: List[Card] = []
        self.pot = 0.0
        self.current_bet = 0.0
        self.small_blind = 0.5
        self.big_blind = 1.0
        self.street = Street.PREFLOP
        self.action_history: List[str] = []

    def create_deck(self) -> List[Card]:
        """Create a standard 52-card deck"""
        return [Card(rank, suit) for rank in self.ranks for suit in self.suits]

    def deal_cards(self, deck: List[Card], num_cards: int) -> List[Card]:
        """Deal specified number of cards from deck"""
        cards = []
        for _ in range(num_cards):
            if deck:
                cards.append(deck.pop())
        return cards

    def setup_hand(self, hero_position: str = "BTN", hero_cards: str = "random",
                   num_opponents: int = 2, stack_size: float = 100.0) -> Dict[str, Any]:
        """Setup a new poker hand"""
        self.reset_game()

        # Create and shuffle deck
        deck = self.create_deck()
        random.shuffle(deck)

        # Determine positions
        if num_opponents + 1 > len(self.positions_6max):
            positions = self.positions_6max
        else:
            # Get subset of positions including hero_position
            hero_idx = self.positions_6max.index(hero_position.upper())
            positions = []
            for i in range(num_opponents + 1):
                pos_idx = (hero_idx - num_opponents + i) % len(self.positions_6max)
                positions.append(self.positions_6max[pos_idx])

        # Create players
        for i, position in enumerate(positions):
            is_hero = (position == hero_position.upper())
            player_name = "Hero" if is_hero else f"Opponent{i}"

            # Deal hole cards
            if is_hero and hero_cards != "random":
                # Parse hero cards like "AhKs"
                try:
                    if len(hero_cards) == 4:
                        card1 = Card.from_string(hero_cards[:2])
                        card2 = Card.from_string(hero_cards[2:])
                        hole_cards = [card1, card2]
                        # Remove these cards from deck
                        deck = [card for card in deck if not (
                            (card.rank == card1.rank and card.suit == card1.suit) or
                            (card.rank == card2.rank and card.suit == card2.suit)
                        )]
                    else:
                        hole_cards = self.deal_cards(deck, 2)
                except:
                    hole_cards = self.deal_cards(deck, 2)  # Fallback to random
            else:
                hole_cards = self.deal_cards(deck, 2)

            player = Player(
                name=player_name,
                position=position,
                stack=stack_size,
                hole_cards=hole_cards,
                is_hero=is_hero
            )
            self.players.append(player)

        # Post blinds
        self._post_blinds()

        return self.get_game_state()

    def _post_blinds(self):
        """Post small and big blinds"""
        sb_player = None
        bb_player = None

        for player in self.players:
            if player.position == 'SB':
                sb_player = player
            elif player.position == 'BB':
                bb_player = player

        if sb_player:
            sb_player.stack -= self.small_blind
            self.pot += self.small_blind
            self.action_history.append(f"{sb_player.name} posts SB ${self.small_blind}")

        if bb_player:
            bb_player.stack -= self.big_blind
            self.pot += self.big_blind
            self.current_bet = self.big_blind
            self.action_history.append(f"{bb_player.name} posts BB ${self.big_blind}")

    def deal_flop(self):
        """Deal the flop (3 cards)"""
        if self.street != Street.PREFLOP:
            return

        deck = self.create_deck()
        # Remove known cards
        for player in self.players:
            for card in player.hole_cards:
                deck = [c for c in deck if not (c.rank == card.rank and c.suit == card.suit)]

        random.shuffle(deck)
        self.board = self.deal_cards(deck, 3)
        self.street = Street.FLOP
        self.current_bet = 0.0

    def deal_turn(self):
        """Deal the turn (4th card)"""
        if self.street != Street.FLOP:
            return

        deck = self.create_deck()
        # Remove known cards
        for player in self.players:
            for card in player.hole_cards:
                deck = [c for c in deck if not (c.rank == card.rank and c.suit == card.suit)]
        for card in self.board:
            deck = [c for c in deck if not (c.rank == card.rank and c.suit == card.suit)]

        random.shuffle(deck)
        new_card = self.deal_cards(deck, 1)
        if new_card:
            self.board.append(new_card[0])
            self.street = Street.TURN
            self.current_bet = 0.0

    def deal_river(self):
        """Deal the river (5th card)"""
        if self.street != Street.TURN:
            return

        deck = self.create_deck()
        # Remove known cards
        for player in self.players:
            for card in player.hole_cards:
                deck = [c for c in deck if not (c.rank == card.rank and c.suit == card.suit)]
        for card in self.board:
            deck = [c for c in deck if not (c.rank == card.rank and c.suit == card.suit)]

        random.shuffle(deck)
        new_card = self.deal_cards(deck, 1)
        if new_card:
            self.board.append(new_card[0])
            self.street = Street.RIVER
            self.current_bet = 0.0

    def get_hero_player(self) -> Optional[Player]:
        """Get the hero player"""
        for player in self.players:
            if player.is_hero:
                return player
        return None

    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state for agent analysis"""
        hero = self.get_hero_player()

        if not hero:
            return {"error": "No hero player found"}

        # Format hole cards
        hole_cards_str = " ".join(str(card) for card in hero.hole_cards)

        # Format board
        board_str = " ".join(str(card) for card in self.board) if self.board else ""

        # Calculate bet to call
        bet_to_call = max(0, self.current_bet - 0)  # Simplified - assumes no previous action

        # Count opponents
        opponents = len([p for p in self.players if not p.is_hero])

        return {
            "street": self.street.value,
            "position": hero.position,
            "hole_cards": hole_cards_str,
            "board": board_str,
            "pot_size": self.pot,
            "stack_size": hero.stack,
            "bet_to_call": bet_to_call,
            "current_bet": self.current_bet,
            "opponents": opponents,
            "action_history": " | ".join(self.action_history[-3:]),  # Last 3 actions
            "players": [str(player) for player in self.players]
        }

    def create_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Create predefined scenarios for testing agents"""

        scenarios = {
            "premium_pair": {
                "hero_position": "BTN",
                "hero_cards": "AhAs",
                "num_opponents": 2,
                "description": "Premium pocket aces on the button"
            },

            "tough_decision": {
                "hero_position": "BB",
                "hero_cards": "AhQd",
                "num_opponents": 3,
                "description": "AQ in big blind facing action"
            },

            "bluff_spot": {
                "hero_position": "CO",
                "hero_cards": "7h8h",
                "num_opponents": 2,
                "description": "Suited connector in late position"
            },

            "pocket_pair": {
                "hero_position": "MP",
                "hero_cards": "9h9d",
                "num_opponents": 4,
                "description": "Mid pocket pair in middle position"
            }
        }

        if scenario_name not in scenarios:
            scenario_name = "premium_pair"  # Default

        scenario = scenarios[scenario_name]
        game_state = self.setup_hand(
            hero_position=scenario["hero_position"],
            hero_cards=scenario["hero_cards"],
            num_opponents=scenario["num_opponents"]
        )

        game_state["scenario"] = scenario_name
        game_state["scenario_description"] = scenario["description"]

        return game_state

    def advance_street(self):
        """Advance to the next street"""
        if self.street == Street.PREFLOP:
            self.deal_flop()
        elif self.street == Street.FLOP:
            self.deal_turn()
        elif self.street == Street.TURN:
            self.deal_river()

        return self.get_game_state()

if __name__ == "__main__":
    # Test the poker engine
    engine = SimplifiedPokerEngine()

    # Test scenario creation
    state = engine.create_scenario("premium_pair")
    print("=== Poker Hand Setup ===")
    print(f"Scenario: {state['scenario_description']}")
    print(f"Position: {state['position']}")
    print(f"Hole Cards: {state['hole_cards']}")
    print(f"Pot Size: ${state['pot_size']}")
    print(f"Stack Size: ${state['stack_size']}")
    print("\nPlayers:")
    for player in state['players']:
        print(f"  {player}")

    # Test dealing flop
    print("\n=== Dealing Flop ===")
    flop_state = engine.advance_street()
    print(f"Board: {flop_state['board']}")
    print(f"Street: {flop_state['street']}")
