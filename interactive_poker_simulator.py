#!/usr/bin/env python3
"""
Interactive Poker Simulator with AI Agents

A command-line interface for playing simulated poker hands while getting
strategic advice from specialized AI agents. Features visualization and
real-time agent discussions.
"""

import os
import sys
import random
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional
import json

# Fix tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add project root to path
sys.path.append('.')

# Import our modules
from agents import RulesAgent, PositionAgent, MathAgent, JonathanAgent
from game.poker_engine import SimplifiedPokerEngine
from visualization.table_view import PokerTableVisualizer
from setup import KnowledgeBaseSetup
from autogen import ConversableAgent, GroupChat, GroupChatManager

class InteractivePokerSimulator:
    """Interactive poker simulation with AI agents and visualization"""
    
    def __init__(self):
        self.engine = SimplifiedPokerEngine()
        self.visualizer = PokerTableVisualizer()
        self.agents = None
        self.chat_manager = None
        self.kb = None
        self.session_hands = []
        
        # Game settings
        self.starting_stack = 100.0
        self.current_stack = self.starting_stack
        self.hands_played = 0
        
        # Initialize components
        self.setup_knowledge_base()
        self.setup_agents()
    
    def setup_knowledge_base(self):
        """Initialize the knowledge base"""
        print("🔄 Setting up knowledge base...")
        try:
            setup_manager = KnowledgeBaseSetup()
            self.kb, setup_info = setup_manager.initialize_knowledge_base()
            
            if setup_info["success"]:
                stats = setup_info.get("stats", {})
                print(f"✅ Knowledge base loaded: {stats.get('total_documents', 0)} documents")
            else:
                print("⚠️ Knowledge base failed - continuing without RAG")
                self.kb = None
        except Exception as e:
            print(f"⚠️ Knowledge base error: {e}")
            self.kb = None
    
    def setup_agents(self):
        """Initialize AI agents with Ollama"""
        print("\n🤖 Setting up AI agents...")
        try:
            # Configure Ollama
            llm_config = {
                "config_list": [
                    {
                        "model": "llama3.2:latest",
                        "base_url": "http://localhost:11434/v1",
                        "api_key": "ollama",
                        "temperature": 0.3,
                        "price": [0, 0]
                    }
                ],
                "timeout": 120,
            }
            
            # Create agents
            rules_agent = RulesAgent(llm_config)
            position_agent = PositionAgent(llm_config)
            math_agent = MathAgent(llm_config)
            jonathan_agent = JonathanAgent(llm_config, knowledge_base=self.kb)
            
            self.agents = [rules_agent, position_agent, math_agent, jonathan_agent]
            
            # Create GroupChat
            group_chat = GroupChat(
                agents=self.agents,
                messages=[],
                max_round=6,  # Shorter for interactive use
                speaker_selection_method="auto",
                allow_repeat_speaker=False
            )
            
            self.chat_manager = GroupChatManager(
                groupchat=group_chat,
                llm_config=llm_config
            )
            
            print(f"✅ Created {len(self.agents)} AI agents with GroupChat")
            
        except Exception as e:
            print(f"⚠️ Agent setup failed: {e}")
            print("💡 Continuing with mock agents - make sure Ollama is running")
            self.agents = None
            self.chat_manager = None
    
    def generate_random_hand(self) -> Dict[str, Any]:
        """Generate a random poker scenario"""
        scenarios = ['premium_pair', 'tough_decision', 'bluff_spot', 'pocket_pair', 'drawing_hand']
        scenario_type = random.choice(scenarios)
        
        # Generate base scenario
        game_state = self.engine.create_scenario(scenario_type)
        
        # Add some randomization
        positions = ['UTG', 'MP', 'CO', 'BTN', 'SB', 'BB']
        game_state['position'] = random.choice(positions)
        game_state['stack_size'] = self.current_stack
        game_state['pot_size'] = random.uniform(5, 25)
        game_state['bet_to_call'] = random.uniform(0, 15)
        game_state['opponents'] = random.randint(1, 4)
        
        # Sometimes add board cards
        if random.random() > 0.6:  # 40% chance of flop+
            board_cards = self.generate_board()
            game_state['board'] = ' '.join(board_cards)
            game_state['street'] = 'flop' if len(board_cards) == 3 else 'turn' if len(board_cards) == 4 else 'river'
        else:
            game_state['street'] = 'preflop'
        
        return game_state
    
    def generate_board(self) -> List[str]:
        """Generate random board cards"""
        suits = ['h', 'd', 'c', 's']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        
        cards = []
        used = set()
        
        num_cards = random.choice([3, 4, 5])  # flop, turn, or river
        
        for _ in range(num_cards):
            while True:
                rank = random.choice(ranks)
                suit = random.choice(suits)
                card = f"{rank}{suit}"
                if card not in used:
                    cards.append(card)
                    used.add(card)
                    break
        
        return cards
    
    def get_agent_recommendations(self, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommendations from AI agents"""
        if not self.agents:
            # Mock recommendations
            return [
                {
                    'agent': 'RulesAgent',
                    'specialty': 'Rules and Game Mechanics',
                    'recommendation': 'All actions are legal - proceed with strategy',
                    'confidence': 0.95,
                    'reasoning': 'Standard betting situation, all options available'
                },
                {
                    'agent': 'MathAgent',
                    'specialty': 'Mathematics and Probability',
                    'recommendation': self.get_math_recommendation(game_state),
                    'confidence': random.uniform(0.7, 0.9),
                    'reasoning': 'Based on pot odds and equity calculations'
                },
                {
                    'agent': 'PositionAgent',
                    'specialty': 'Position and Ranges',
                    'recommendation': self.get_position_recommendation(game_state),
                    'confidence': random.uniform(0.75, 0.88),
                    'reasoning': f"Position analysis for {game_state['position']}"
                },
                {
                    'agent': 'JonathanAgent',
                    'specialty': 'Jonathan Little Strategy',
                    'recommendation': 'Apply GTO principles with exploitative adjustments',
                    'confidence': random.uniform(0.8, 0.95),
                    'reasoning': 'Based on similar WPH episode patterns'
                }
            ]
        
        # Get real agent recommendations
        recommendations = []
        for agent in self.agents:
            try:
                rec = agent.get_recommendation(game_state)
                recommendations.append(rec)
            except Exception as e:
                print(f"⚠️ Error from {agent.name}: {e}")
                # Fallback recommendation
                recommendations.append({
                    'agent': agent.name,
                    'specialty': agent.specialty,
                    'recommendation': 'Unable to analyze - check connection',
                    'confidence': 0.0,
                    'reasoning': f'Agent error: {str(e)[:50]}...'
                })
        
        return recommendations
    
    def get_math_recommendation(self, game_state: Dict[str, Any]) -> str:
        """Simple math-based recommendation"""
        bet_to_call = game_state.get('bet_to_call', 0)
        pot_size = game_state.get('pot_size', 10)
        
        if bet_to_call == 0:
            return "CHECK or BET for value"
        
        pot_odds = bet_to_call / (pot_size + bet_to_call)
        if pot_odds < 0.3:
            return "CALL - good pot odds"
        elif pot_odds > 0.5:
            return "FOLD - poor pot odds"
        else:
            return "CALL or RAISE depending on hand strength"
    
    def get_position_recommendation(self, game_state: Dict[str, Any]) -> str:
        """Simple position-based recommendation"""
        position = game_state.get('position', 'BTN')
        
        if position in ['UTG', 'MP']:
            return "TIGHT play - early position"
        elif position in ['CO', 'BTN']:
            return "AGGRESSIVE play - late position advantage"
        else:  # SB, BB
            return "DEFEND or FOLD based on hand strength"
    
    def get_group_discussion(self, game_state: Dict[str, Any], question: str) -> str:
        """Get collaborative agent discussion"""
        if not self.chat_manager:
            return """
Mock Agent Discussion:

RulesAgent: This is a legal betting situation. All standard actions are available.

MathAgent: Based on pot odds, this looks like a profitable spot to continue with strong hands.

PositionAgent: Our position gives us good information and betting options post-flop.

JonathanAgent: Similar to patterns in WPH episodes - value betting is often optimal here.

Consensus: Proceed with aggressive value-focused strategy.
"""
        
        # Format situation for agents
        context = f"""
POKER HAND ANALYSIS:

Position: {game_state.get('position', 'Unknown')}
Hole Cards: {game_state.get('hole_cards', 'Unknown')}
Board: {game_state.get('board', 'Preflop')}
Street: {game_state.get('street', 'preflop')}
Pot Size: ${game_state.get('pot_size', 0)}
Stack Size: ${game_state.get('stack_size', 0)}
Bet to Call: ${game_state.get('bet_to_call', 0)}
Opponents: {game_state.get('opponents', 1)}

QUESTION: {question}

Please provide your expert analysis. Keep responses concise for interactive play.
"""
        
        try:
            # Start group discussion
            chat_result = self.agents[0].initiate_chat(
                recipient=self.chat_manager,
                message=context,
                max_turns=6
            )
            
            return str(chat_result)
        
        except Exception as e:
            return f"Group discussion error: {e}\n\nFalling back to individual agent analysis..."
    
    def display_hand(self, game_state: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Display the poker hand with visualization"""
        print("\n" + "="*60)
        print(f"📊 HAND #{self.hands_played + 1}")
        print("="*60)
        
        # Game state info
        print(f"Street: {game_state.get('street', 'preflop').upper()}")
        print(f"Position: {game_state['position']}")
        print(f"Hole Cards: {game_state['hole_cards']}")
        if game_state.get('board'):
            print(f"Board: {game_state['board']}")
        print(f"Stack: ${game_state['stack_size']}")
        print(f"Pot: ${game_state['pot_size']}")
        print(f"Bet to Call: ${game_state['bet_to_call']}")
        print(f"Opponents: {game_state['opponents']}")
        
        # Agent recommendations
        print(f"\n🤖 AGENT RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['agent']}: {rec['recommendation']} ({rec['confidence']:.1%})")
        
        # Create and show visualization
        try:
            fig = self.visualizer.visualize_game_state(game_state, recommendations)
            plt.show(block=False)  # Non-blocking show
            plt.pause(0.1)  # Brief pause to render
        except Exception as e:
            print(f"⚠️ Visualization error: {e}")
    
    def process_action(self, action: str, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process player action and update game state"""
        bet_amount = 0
        
        if action.startswith('bet') or action.startswith('raise'):
            try:
                parts = action.split()
                if len(parts) > 1:
                    bet_amount = float(parts[1])
                else:
                    bet_amount = max(game_state['bet_to_call'] * 2, 5)  # Default raise
            except:
                bet_amount = 5
        
        # Simple outcome simulation
        outcomes = ['win', 'lose', 'chop']
        weights = [0.4, 0.4, 0.2]  # 40% win, 40% lose, 20% chop
        
        # Adjust weights based on action
        if action == 'fold':
            outcome = 'fold'
            result_amount = -game_state.get('bet_to_call', 0)
        else:
            outcome = random.choices(outcomes, weights=weights)[0]
            
            if outcome == 'win':
                result_amount = game_state['pot_size'] + bet_amount
            elif outcome == 'lose':
                result_amount = -(game_state.get('bet_to_call', 0) + bet_amount)
            else:  # chop
                result_amount = 0
        
        # Update stack
        self.current_stack += result_amount
        
        result = {
            'action': action,
            'outcome': outcome,
            'amount_change': result_amount,
            'new_stack': self.current_stack
        }
        
        # Store hand history
        hand_result = {
            'hand_number': self.hands_played + 1,
            'game_state': game_state.copy(),
            'action': action,
            'outcome': outcome,
            'stack_change': result_amount,
            'final_stack': self.current_stack
        }
        self.session_hands.append(hand_result)
        
        return result
    
    def show_session_stats(self):
        """Display session statistics"""
        if not self.session_hands:
            print("No hands played yet!")
            return
        
        total_profit = self.current_stack - self.starting_stack
        win_rate = sum(1 for h in self.session_hands if h['outcome'] == 'win') / len(self.session_hands)
        
        print(f"\n📊 SESSION STATS:")
        print(f"Hands Played: {len(self.session_hands)}")
        print(f"Starting Stack: ${self.starting_stack}")
        print(f"Current Stack: ${self.current_stack}")
        print(f"Profit/Loss: ${total_profit:+.2f}")
        print(f"Win Rate: {win_rate:.1%}")
        
        # Show recent hands
        print(f"\n📝 RECENT HANDS:")
        for hand in self.session_hands[-5:]:
            result_symbol = "✅" if hand['outcome'] == 'win' else "❌" if hand['outcome'] == 'lose' else "🤝" if hand['outcome'] == 'chop' else "❌"
            print(f"Hand {hand['hand_number']}: {hand['action']} → {hand['outcome']} {result_symbol} (${hand['stack_change']:+.2f})")
    
    def main_loop(self):
        """Main interactive loop"""
        print("🎰 INTERACTIVE POKER SIMULATOR")
        print("="*60)
        print("Commands:")
        print("  'new' or 'n' - Deal new hand")
        print("  'fold', 'call', 'check', 'bet X', 'raise X' - Make action")
        print("  'discuss QUESTION' - Ask agents to discuss strategy")
        print("  'stats' - Show session statistics")
        print("  'reset' - Reset stack and start over")
        print("  'quit' or 'q' - Exit simulator")
        print("="*60)
        
        current_game_state = None
        current_recommendations = None
        
        while True:
            try:
                command = input("\n🎯 Enter command: ").strip().lower()
                
                if command in ['quit', 'q', 'exit']:
                    print("\n👋 Thanks for playing!")
                    self.show_session_stats()
                    break
                
                elif command in ['new', 'n', 'deal']:
                    current_game_state = self.generate_random_hand()
                    current_recommendations = self.get_agent_recommendations(current_game_state)
                    self.display_hand(current_game_state, current_recommendations)
                
                elif command == 'stats':
                    self.show_session_stats()
                
                elif command == 'reset':
                    self.current_stack = self.starting_stack
                    self.hands_played = 0
                    self.session_hands = []
                    print("🔄 Session reset! Stack back to $100")
                
                elif command.startswith('discuss '):
                    if current_game_state:
                        question = command[8:]  # Remove 'discuss '
                        print(f"\n💬 AGENT DISCUSSION: {question}")
                        print("-" * 60)
                        discussion = self.get_group_discussion(current_game_state, question)
                        print(discussion)
                    else:
                        print("❌ No active hand! Deal a new hand first with 'new'")
                
                elif command in ['fold', 'call', 'check'] or command.startswith('bet') or command.startswith('raise'):
                    if current_game_state:
                        result = self.process_action(command, current_game_state)
                        self.hands_played += 1
                        
                        # Show result
                        print(f"\n🎲 RESULT:")
                        print(f"Action: {result['action']}")
                        print(f"Outcome: {result['outcome']}")
                        print(f"Stack Change: ${result['amount_change']:+.2f}")
                        print(f"New Stack: ${result['new_stack']}")
                        
                        # Clear current hand
                        current_game_state = None
                        current_recommendations = None
                        
                        # Close any open plots
                        plt.close('all')
                    else:
                        print("❌ No active hand! Deal a new hand first with 'new'")
                
                elif command in ['help', 'h']:
                    print("🎯 Available commands:")
                    print("  new/n - Deal new hand")
                    print("  fold/call/check/bet X/raise X - Make action")
                    print("  discuss QUESTION - Agent discussion")
                    print("  stats - Session statistics")
                    print("  reset - Reset session")
                    print("  quit/q - Exit")
                
                else:
                    print("❓ Unknown command. Type 'help' for available commands")
            
            except KeyboardInterrupt:
                print("\n👋 Exiting simulator...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    simulator = InteractivePokerSimulator()
    simulator.main_loop()