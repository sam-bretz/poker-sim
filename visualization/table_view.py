"""
Table visualization for the poker assistant using matplotlib.
Creates clear visual representations of poker hands and game states.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PokerTableVisualizer:
    """Creates visual representations of poker game states"""
    
    def __init__(self):
        self.fig_width = 12
        self.fig_height = 8
        
        # Colors
        self.colors = {
            'table_felt': '#2E7D32',  # Green felt
            'card_bg': '#FFFFFF',
            'card_border': '#000000',
            'chip_stack': '#FFD700',  # Gold
            'pot': '#FF4444',  # Red
            'hero_highlight': '#00BCD4',  # Cyan
            'text': '#FFFFFF',
            'board_bg': '#1B5E20'  # Darker green
        }
        
        # Card symbols
        self.suit_symbols = {
            'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'
        }
        
        self.suit_colors = {
            'h': '#FF0000', 'd': '#FF0000',  # Red
            'c': '#000000', 's': '#000000'   # Black
        }
    
    def create_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """Create a new figure for the poker table"""
        fig, ax = plt.subplots(1, 1, figsize=(self.fig_width, self.fig_height))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Draw table felt background
        table_bg = Rectangle((0, 0), 10, 6, 
                           facecolor=self.colors['table_felt'], 
                           edgecolor='darkgreen', 
                           linewidth=3)
        ax.add_patch(table_bg)
        
        return fig, ax
    
    def draw_card(self, ax: plt.Axes, x: float, y: float, card_str: str, 
                  width: float = 0.6, height: float = 0.8, face_up: bool = True):
        """Draw a single playing card"""
        
        if not face_up:
            # Draw card back
            card_bg = Rectangle((x, y), width, height,
                              facecolor='#4169E1',  # Royal blue
                              edgecolor=self.colors['card_border'],
                              linewidth=2)
            ax.add_patch(card_bg)
            
            # Add pattern
            ax.text(x + width/2, y + height/2, '🂠', 
                   fontsize=20, ha='center', va='center', color='white')
            return
        
        if len(card_str) < 2:
            card_str = "??"
        
        rank = card_str[0] if len(card_str) > 0 else '?'
        suit = card_str[1] if len(card_str) > 1 else 's'
        
        # Draw card background
        card_bg = Rectangle((x, y), width, height,
                          facecolor=self.colors['card_bg'],
                          edgecolor=self.colors['card_border'],
                          linewidth=2)
        ax.add_patch(card_bg)
        
        # Get suit symbol and color
        suit_symbol = self.suit_symbols.get(suit.lower(), '♠')
        suit_color = self.suit_colors.get(suit.lower(), '#000000')
        
        # Draw rank (larger)
        ax.text(x + width/2, y + height*0.65, rank.upper(),
               fontsize=16, fontweight='bold', ha='center', va='center',
               color=suit_color)
        
        # Draw suit symbol
        ax.text(x + width/2, y + height*0.35, suit_symbol,
               fontsize=14, ha='center', va='center', color=suit_color)
    
    def draw_board(self, ax: plt.Axes, board_cards: List[str]):
        """Draw community cards in the center of the table"""
        if not board_cards:
            return
        
        # Board area background
        board_width = len(board_cards) * 0.8 + 0.4
        board_x = 5 - board_width/2
        board_bg = Rectangle((board_x - 0.2, 2.6), board_width, 1.0,
                           facecolor=self.colors['board_bg'],
                           edgecolor='white',
                           linewidth=2,
                           alpha=0.3)
        ax.add_patch(board_bg)
        
        # Label
        ax.text(5, 3.8, 'BOARD', fontsize=12, fontweight='bold',
               ha='center', va='center', color=self.colors['text'])
        
        # Draw cards
        start_x = 5 - (len(board_cards) * 0.8)/2 + 0.1
        for i, card in enumerate(board_cards):
            card_x = start_x + i * 0.8
            self.draw_card(ax, card_x, 2.8, card)
    
    def draw_pot(self, ax: plt.Axes, pot_size: float):
        """Draw the pot in the center"""
        # Pot circle
        pot_circle = Circle((5, 1.8), 0.4, 
                          facecolor=self.colors['pot'],
                          edgecolor='white',
                          linewidth=2,
                          alpha=0.8)
        ax.add_patch(pot_circle)
        
        # Pot text
        ax.text(5, 1.8, f'${pot_size}', 
               fontsize=11, fontweight='bold',
               ha='center', va='center', color='white')
        
        ax.text(5, 1.4, 'POT', 
               fontsize=10, fontweight='bold',
               ha='center', va='center', color=self.colors['text'])
    
    def get_player_position(self, position: str, total_players: int) -> Tuple[float, float]:
        """Get x, y coordinates for player position"""
        
        # 6-max positions around the table
        positions_6max = {
            'UTG': (2, 0.5),
            'MP': (1, 2.5),
            'CO': (2, 5),
            'BTN': (5, 5.5), 
            'SB': (8, 5),
            'BB': (9, 2.5)
        }
        
        # 4-handed positions
        positions_4max = {
            'CO': (2, 5),
            'BTN': (5, 5.5),
            'SB': (8, 5), 
            'BB': (8, 0.5)
        }
        
        # Choose position mapping
        if total_players <= 4:
            return positions_4max.get(position, (5, 0.5))
        else:
            return positions_6max.get(position, (5, 0.5))
    
    def draw_player(self, ax: plt.Axes, name: str, position: str, 
                   stack: float, cards: List[str], total_players: int,
                   is_hero: bool = False, is_active: bool = False):
        """Draw a player with their information"""
        
        x, y = self.get_player_position(position, total_players)
        
        # Player background
        bg_color = self.colors['hero_highlight'] if is_hero else 'darkgray'
        alpha = 0.9 if is_hero else 0.7
        
        player_bg = Rectangle((x-0.8, y-0.5), 1.6, 1.0,
                            facecolor=bg_color,
                            edgecolor='white',
                            linewidth=2 if is_hero else 1,
                            alpha=alpha)
        ax.add_patch(player_bg)
        
        # Player name and position
        name_text = f"{name}\n({position})"
        ax.text(x, y+0.3, name_text, 
               fontsize=9, fontweight='bold' if is_hero else 'normal',
               ha='center', va='center', color='white')
        
        # Stack size
        ax.text(x, y-0.3, f'${stack}', 
               fontsize=9, ha='center', va='center', color='white')
        
        # Draw hole cards if hero or if cards are revealed
        if cards and (is_hero or len(cards) == 2):
            card_y = y + 0.6 if y > 3 else y - 1.0  # Position cards above or below
            
            for i, card in enumerate(cards[:2]):  # Max 2 hole cards
                card_x = x - 0.4 + i * 0.5
                face_up = is_hero  # Only show hero's cards face up
                self.draw_card(ax, card_x, card_y, card, 
                             width=0.4, height=0.6, face_up=face_up)
    
    def draw_action_buttons(self, ax: plt.Axes, actions: List[str]):
        """Draw available action buttons"""
        if not actions:
            return
        
        # Action area
        action_y = 0.2
        button_width = 1.2
        spacing = 0.1
        total_width = len(actions) * button_width + (len(actions) - 1) * spacing
        start_x = 5 - total_width/2
        
        for i, action in enumerate(actions):
            button_x = start_x + i * (button_width + spacing)
            
            # Button background
            button_bg = Rectangle((button_x, action_y), button_width, 0.4,
                                facecolor='lightgray',
                                edgecolor='black',
                                linewidth=1)
            ax.add_patch(button_bg)
            
            # Button text
            ax.text(button_x + button_width/2, action_y + 0.2, action.upper(),
                   fontsize=10, fontweight='bold',
                   ha='center', va='center', color='black')
    
    def visualize_game_state(self, game_state: Dict[str, Any], 
                           agent_recommendations: Optional[List[Dict]] = None) -> plt.Figure:
        """Create complete visualization of the game state"""
        
        fig, ax = self.create_figure()
        
        # Title
        street = game_state.get('street', 'preflop').upper()
        scenario = game_state.get('scenario_description', 'Poker Hand Analysis')
        ax.text(5, 5.7, f'{scenario} - {street}', 
               fontsize=14, fontweight='bold', 
               ha='center', va='center', color=self.colors['text'])
        
        # Draw pot
        pot_size = game_state.get('pot_size', 0)
        self.draw_pot(ax, pot_size)
        
        # Draw board
        board_str = game_state.get('board', '')
        if board_str:
            board_cards = board_str.split()
            self.draw_board(ax, board_cards)
        
        # Draw players (simplified - extract from game state)
        hero_position = game_state.get('position', 'BTN')
        hero_cards = game_state.get('hole_cards', '').split()
        hero_stack = game_state.get('stack_size', 100)
        
        total_players = game_state.get('opponents', 1) + 1
        
        # Draw hero
        self.draw_player(ax, 'HERO', hero_position, hero_stack, 
                        hero_cards, total_players, is_hero=True)
        
        # Draw opponents (simplified)
        opponent_positions = ['UTG', 'MP', 'CO', 'SB', 'BB']
        opponent_count = 0
        for pos in opponent_positions:
            if pos != hero_position and opponent_count < game_state.get('opponents', 1):
                self.draw_player(ax, f'OPP{opponent_count+1}', pos, 100, 
                               ['??', '??'], total_players)
                opponent_count += 1
        
        # Action buttons removed - they were occluding player cards
        # The available actions are shown in the text interface instead
        
        # Add agent recommendations panel if provided
        if agent_recommendations:
            self.draw_recommendations_panel(ax, agent_recommendations)
        
        plt.tight_layout()
        return fig
    
    def draw_recommendations_panel(self, ax: plt.Axes, recommendations: List[Dict]):
        """Draw agent recommendations panel"""
        panel_x = 0.2
        panel_y = 4.5
        panel_width = 3.0
        panel_height = 1.2
        
        # Panel background
        panel_bg = Rectangle((panel_x, panel_y), panel_width, panel_height,
                           facecolor='black',
                           edgecolor='white',
                           linewidth=1,
                           alpha=0.8)
        ax.add_patch(panel_bg)
        
        # Panel title
        ax.text(panel_x + panel_width/2, panel_y + panel_height - 0.1, 
               'AGENT RECOMMENDATIONS', 
               fontsize=10, fontweight='bold',
               ha='center', va='top', color='white')
        
        # Show top 3 recommendations
        y_pos = panel_y + panel_height - 0.3
        for i, rec in enumerate(recommendations[:3]):
            agent_name = rec.get('agent', 'Unknown')
            recommendation = rec.get('recommendation', 'No recommendation')
            confidence = rec.get('confidence', 0.5)
            
            # Truncate long recommendations
            if len(recommendation) > 30:
                recommendation = recommendation[:27] + "..."
            
            rec_text = f"{agent_name}: {recommendation} ({confidence:.1%})"
            ax.text(panel_x + 0.1, y_pos, rec_text,
                   fontsize=8, ha='left', va='top', color='white')
            y_pos -= 0.2

if __name__ == "__main__":
    # Test the visualizer
    viz = PokerTableVisualizer()
    
    # Create test game state
    test_state = {
        'street': 'flop',
        'position': 'BTN',
        'hole_cards': 'Ah Ks',
        'board': 'Kh Qd 7c',
        'pot_size': 15.0,
        'stack_size': 95.0,
        'bet_to_call': 5.0,
        'opponents': 2,
        'scenario_description': 'Top pair with top kicker'
    }
    
    # Create test recommendations
    test_recs = [
        {'agent': 'MathAgent', 'recommendation': 'BET for value', 'confidence': 0.85},
        {'agent': 'PositionAgent', 'recommendation': 'Use position advantage', 'confidence': 0.80},
        {'agent': 'JonathanAgent', 'recommendation': 'Build pot with strong hand', 'confidence': 0.90}
    ]
    
    fig = viz.visualize_game_state(test_state, test_recs)
    plt.savefig('test_poker_table.png', dpi=150, bbox_inches='tight')
    plt.show()