"""
Table visualization for the poker assistant using matplotlib.
Creates clear visual representations of poker hands and game states.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class PokerTableVisualizer:
    """Creates visual representations of poker game states"""

    def __init__(self):
        self.fig_width = 12
        self.fig_height = 8

        # Colors
        self.colors = {
            "table_felt": "#2E7D32",  # Green felt
            "card_bg": "#FFFFFF",
            "card_border": "#000000",
            "chip_stack": "#FFD700",  # Gold
            "pot": "#FF4444",  # Red
            "hero_highlight": "#00BCD4",  # Cyan
            "text": "#FFFFFF",
            "board_bg": "#1B5E20",  # Darker green
        }

        # Card symbols
        self.suit_symbols = {"h": "♥", "d": "♦", "c": "♣", "s": "♠"}

        self.suit_colors = {
            "h": "#FF0000",
            "d": "#FF0000",  # Red
            "c": "#000000",
            "s": "#000000",  # Black
        }

    def create_figure(self) -> Tuple[Figure, Axes]:
        """Create a new figure for the poker table"""
        fig, ax = plt.subplots(1, 1, figsize=(self.fig_width, self.fig_height))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_aspect("equal")
        ax.axis("off")

        # Draw table felt background
        table_bg = Rectangle(
            (0, 0),
            10,
            6,
            facecolor=self.colors["table_felt"],
            edgecolor="darkgreen",
            linewidth=3,
        )
        ax.add_patch(table_bg)

        return fig, ax

    def draw_card(
        self,
        ax: Axes,
        x: float,
        y: float,
        card_str: str,
        width: float = 0.6,
        height: float = 0.8,
        face_up: bool = True,
    ):
        """Draw a single playing card"""

        if not face_up:
            # Draw card back
            card_bg = Rectangle(
                (x, y),
                width,
                height,
                facecolor="#4169E1",  # Royal blue
                edgecolor=self.colors["card_border"],
                linewidth=2,
            )
            ax.add_patch(card_bg)

            # Add pattern
            ax.text(
                x + width / 2,
                y + height / 2,
                "🂠",
                fontsize=20,
                ha="center",
                va="center",
                color="white",
            )
            return

        if len(card_str) < 2:
            card_str = "??"

        rank = card_str[0] if len(card_str) > 0 else "?"
        suit = card_str[1] if len(card_str) > 1 else "s"

        # Draw card background
        card_bg = Rectangle(
            (x, y),
            width,
            height,
            facecolor=self.colors["card_bg"],
            edgecolor=self.colors["card_border"],
            linewidth=2,
        )
        ax.add_patch(card_bg)

        # Get suit symbol and color
        suit_symbol = self.suit_symbols.get(suit.lower(), "♠")
        suit_color = self.suit_colors.get(suit.lower(), "#000000")

        # Draw rank (larger)
        ax.text(
            x + width / 2,
            y + height * 0.65,
            rank.upper(),
            fontsize=16,
            fontweight="bold",
            ha="center",
            va="center",
            color=suit_color,
        )

        # Draw suit symbol
        ax.text(
            x + width / 2,
            y + height * 0.35,
            suit_symbol,
            fontsize=14,
            ha="center",
            va="center",
            color=suit_color,
        )

    def draw_board(self, ax: Axes, board_cards: List[str]):
        """Draw community cards in the center of the table"""
        if not board_cards:
            return

        # Board area background
        board_width = len(board_cards) * 0.8 + 0.4
        board_x = 5 - board_width / 2
        board_bg = Rectangle(
            (board_x - 0.2, 2.6),
            board_width,
            1.0,
            facecolor=self.colors["board_bg"],
            edgecolor="white",
            linewidth=2,
            alpha=0.3,
        )
        ax.add_patch(board_bg)

        # Label
        ax.text(
            5,
            3.8,
            "BOARD",
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="center",
            color=self.colors["text"],
        )

        # Draw cards
        start_x = 5 - (len(board_cards) * 0.8) / 2 + 0.1
        for i, card in enumerate(board_cards):
            card_x = start_x + i * 0.8
            self.draw_card(ax, card_x, 2.8, card)

    def draw_pot(self, ax: Axes, pot_size: float):
        """Draw the pot in the center"""
        # Pot circle
        pot_circle = Circle(
            (5, 1.8),
            0.4,
            facecolor=self.colors["pot"],
            edgecolor="white",
            linewidth=2,
            alpha=0.8,
        )
        ax.add_patch(pot_circle)

        # Format pot size properly (avoid floating point precision issues)
        if pot_size == int(pot_size):
            pot_text = f"${int(pot_size)}.0"
        else:
            pot_text = f"${pot_size:.1f}"

        # Pot text
        ax.text(
            5,
            1.8,
            pot_text,
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="center",
            color="white",
        )

        ax.text(
            5,
            1.4,
            "POT",
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            color=self.colors["text"],
        )

    def get_player_position(
        self, position: str, total_players: int
    ) -> Tuple[float, float]:
        """Get x, y coordinates for player position"""

        # 6-max positions around the table with better spacing
        positions_6max = {
            "UTG": (2.5, 1.0),  # Bottom left
            "MP": (1.5, 3.0),  # Left side
            "CO": (2.5, 4.8),  # Top left
            "BTN": (5, 5.2),  # Top center
            "SB": (7.5, 4.8),  # Top right
            "BB": (8.5, 3.0),  # Right side
        }

        # 4-handed positions with better spacing
        positions_4max = {
            "CO": (2.5, 4.8),  # Top left
            "BTN": (5, 5.2),  # Top center
            "SB": (7.5, 4.8),  # Top right
            "BB": (8.5, 1.0),  # Bottom right
        }

        # Choose position mapping
        if total_players <= 4:
            return positions_4max.get(position, (5, 1.0))
        else:
            return positions_6max.get(position, (5, 1.0))

    def draw_player(
        self,
        ax: Axes,
        name: str,
        position: str,
        stack: float,
        cards: List[str],
        total_players: int,
        is_hero: bool = False,
        is_active: bool = False,
    ):
        """Draw a player with their information"""

        x, y = self.get_player_position(position, total_players)

        # Player background
        bg_color = self.colors["hero_highlight"] if is_hero else "darkgray"
        alpha = 0.9 if is_hero else 0.7

        player_bg = Rectangle(
            (x - 0.8, y - 0.5),
            1.6,
            1.0,
            facecolor=bg_color,
            edgecolor="white",
            linewidth=2 if is_hero else 1,
            alpha=alpha,
        )
        ax.add_patch(player_bg)

        # Player name and position
        name_text = f"{name}\n({position})"
        ax.text(
            x,
            y + 0.3,
            name_text,
            fontsize=9,
            fontweight="bold" if is_hero else "normal",
            ha="center",
            va="center",
            color="white",
        )

        # Stack size
        ax.text(
            x, y - 0.3, f"${stack}", fontsize=9, ha="center", va="center", color="white"
        )

        # Draw hole cards if hero or if cards are revealed
        if cards and (is_hero or len(cards) == 2):
            # Better card positioning to avoid pot area (center: x=5, y=1.8, radius=0.4)
            # Pot area spans roughly x=4.6-5.4, y=1.4-2.2
            if y > 3.5:  # Top half of table
                card_y = y - 0.8  # Cards below player
            elif y < 2.5:  # Bottom half of table
                card_y = y + 0.6  # Cards above player
                # Extra check to avoid pot area for bottom players
                if 4.2 < x < 5.8 and card_y > 1.2:  # Near pot horizontally
                    card_y = max(y + 0.8, 2.4)  # Move cards further away from pot
            else:  # Middle positions
                if x < 5:  # Left side
                    card_y = y - 0.4
                else:  # Right side
                    card_y = y - 0.4

            # Ensure cards stay within bounds and don't overlap pot
            card_y = max(0.1, min(5.2, card_y))
            
            # Final pot avoidance check - if cards would be in pot area, move them
            if 1.0 < card_y < 2.6 and 4.2 < x < 5.8:  # Cards in pot zone
                if y > 3:  # Player above pot
                    card_y = min(card_y, 0.8)  # Move cards to bottom
                else:  # Player below/beside pot
                    card_y = max(card_y, 2.8)  # Move cards above pot

            for i, card in enumerate(cards[:2]):  # Max 2 hole cards
                card_x = x - 0.4 + i * 0.5
                # Ensure cards stay within horizontal bounds
                card_x = max(0.1, min(9.3, card_x))
                
                # Additional pot avoidance for card horizontal position
                if 1.0 < card_y < 2.6:  # Cards at pot level
                    if 4.6 < card_x < 5.4:  # Card would overlap pot horizontally
                        if x < 5:  # Player on left, move cards left
                            card_x = min(card_x, 4.0)
                        else:  # Player on right, move cards right
                            card_x = max(card_x, 6.0)

                face_up = is_hero  # Only show hero's cards face up
                self.draw_card(
                    ax, card_x, card_y, card, width=0.4, height=0.6, face_up=face_up
                )

    def draw_action_buttons(self, ax: Axes, actions: List[str]):
        """Draw available action buttons"""
        if not actions:
            return

        # Action area
        action_y = 0.2
        button_width = 1.2
        spacing = 0.1
        total_width = len(actions) * button_width + (len(actions) - 1) * spacing
        start_x = 5 - total_width / 2

        for i, action in enumerate(actions):
            button_x = start_x + i * (button_width + spacing)

            # Button background
            button_bg = Rectangle(
                (button_x, action_y),
                button_width,
                0.4,
                facecolor="lightgray",
                edgecolor="black",
                linewidth=1,
            )
            ax.add_patch(button_bg)

            # Button text
            ax.text(
                button_x + button_width / 2,
                action_y + 0.2,
                action.upper(),
                fontsize=10,
                fontweight="bold",
                ha="center",
                va="center",
                color="black",
            )

    def visualize_game_state(self, game_state: Dict[str, Any]) -> Figure:
        """Create complete visualization of the game state (GUI shows only game state, no agent recommendations)"""

        fig, ax = self.create_figure()

        # Title
        street = game_state.get("street", "preflop").upper()
        scenario = game_state.get("scenario_description", "Poker Hand Analysis")
        ax.text(
            5,
            5.7,
            f"{scenario} - {street}",
            fontsize=14,
            fontweight="bold",
            ha="center",
            va="center",
            color=self.colors["text"],
        )

        # Draw pot
        pot_size = game_state.get("pot_size", 0)
        self.draw_pot(ax, pot_size)

        # Draw board
        board_str = game_state.get("board", "")
        if board_str:
            board_cards = board_str.split()
            self.draw_board(ax, board_cards)

        # Draw players (simplified - extract from game state)
        hero_position = game_state.get("position", "BTN")
        hero_cards = game_state.get("hole_cards", "").split()
        hero_stack = game_state.get("stack_size", 100)

        total_players = game_state.get("opponents", 1) + 1

        # Draw hero
        self.draw_player(
            ax,
            "HERO",
            hero_position,
            hero_stack,
            hero_cards,
            total_players,
            is_hero=True,
        )

        # Draw opponents (simplified)
        opponent_positions = ["UTG", "MP", "CO", "SB", "BB"]
        opponent_count = 0
        for pos in opponent_positions:
            if pos != hero_position and opponent_count < game_state.get("opponents", 1):
                self.draw_player(
                    ax,
                    f"OPP{opponent_count + 1}",
                    pos,
                    100,
                    ["??", "??"],
                    total_players,
                )
                opponent_count += 1

        # GUI shows only game state - agent recommendations and discussions are in terminal

        plt.tight_layout()
        return fig


if __name__ == "__main__":
    # Test the visualizer
    viz = PokerTableVisualizer()

    # Create test game state
    test_state = {
        "street": "flop",
        "position": "BTN",
        "hole_cards": "Ah Ks",
        "board": "Kh Qd 7c",
        "pot_size": 15.0,
        "stack_size": 95.0,
        "bet_to_call": 5.0,
        "opponents": 2,
        "scenario_description": "Top pair with top kicker",
    }

    # GUI shows only game state - agent recommendations printed to terminal
    print("🤖 Agent recommendations would appear in terminal:")
    print("• MathAgent: BET for value (85.0%)")
    print("• PositionAgent: Use position advantage (80.0%)")
    print("• JonathanAgent: Build pot with strong hand (90.0%)")

    fig = viz.visualize_game_state(test_state)
    plt.savefig("test_poker_table_clean.png", dpi=150, bbox_inches="tight")
    plt.show()
