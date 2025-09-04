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
from typing import Dict, List, Any

# Fix tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add project root to path
sys.path.append(".")

# Import our modules
from agents import RulesAgent, PositionAgent, MathAgent, JonathanAgent
from game.poker_engine import SimplifiedPokerEngine
from visualization.table_view import PokerTableVisualizer
from setup import KnowledgeBaseSetup
from autogen import GroupChat, GroupChatManager  # type: ignore


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
                print(
                    f"✅ Knowledge base loaded: {stats.get('total_documents', 0)} documents"
                )
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
                        "price": [0, 0],
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
                allow_repeat_speaker=False,
            )

            self.chat_manager = GroupChatManager(
                groupchat=group_chat, llm_config=llm_config
            )

            print(f"✅ Created {len(self.agents)} AI agents with GroupChat")

        except Exception as e:
            print(f"⚠️ Agent setup failed: {e}")
            print("💡 Continuing with mock agents - make sure Ollama is running")
            self.agents = None
            self.chat_manager = None

    def generate_random_hand(self) -> Dict[str, Any]:
        """Generate a random poker scenario"""
        scenarios = [
            "premium_pair",
            "tough_decision",
            "bluff_spot",
            "pocket_pair",
            "drawing_hand",
        ]
        scenario_type = random.choice(scenarios)

        # Generate base scenario
        game_state = self.engine.create_scenario(scenario_type)

        # Add some randomization
        positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        game_state["position"] = random.choice(positions)
        game_state["stack_size"] = self.current_stack
        game_state["pot_size"] = random.uniform(5, 25)
        game_state["bet_to_call"] = random.uniform(0, 15)
        game_state["opponents"] = random.randint(1, 4)

        # Sometimes add board cards
        if random.random() > 0.6:  # 40% chance of flop+
            board_cards = self.generate_board()
            game_state["board"] = " ".join(board_cards)
            game_state["street"] = (
                "flop"
                if len(board_cards) == 3
                else "turn"
                if len(board_cards) == 4
                else "river"
            )
        else:
            game_state["street"] = "preflop"

        return game_state

    def generate_board(self) -> List[str]:
        """Generate random board cards"""
        suits = ["h", "d", "c", "s"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

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

    def get_agent_recommendations(
        self, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get recommendations from AI agents"""
        if not self.agents:
            # Mock recommendations
            return [
                {
                    "agent": "RulesAgent",
                    "specialty": "Rules and Game Mechanics",
                    "recommendation": "All actions are legal - proceed with strategy",
                    "confidence": 0.95,
                    "reasoning": "Standard betting situation, all options available",
                },
                {
                    "agent": "MathAgent",
                    "specialty": "Mathematics and Probability",
                    "recommendation": self.get_math_recommendation(game_state),
                    "confidence": random.uniform(0.7, 0.9),
                    "reasoning": "Based on pot odds and equity calculations",
                },
                {
                    "agent": "PositionAgent",
                    "specialty": "Position and Ranges",
                    "recommendation": self.get_position_recommendation(game_state),
                    "confidence": random.uniform(0.75, 0.88),
                    "reasoning": f"Position analysis for {game_state['position']}",
                },
                {
                    "agent": "JonathanAgent",
                    "specialty": "Jonathan Little Strategy",
                    "recommendation": "Apply GTO principles with exploitative adjustments",
                    "confidence": random.uniform(0.8, 0.95),
                    "reasoning": "Based on similar WPH episode patterns",
                },
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
                recommendations.append(
                    {
                        "agent": agent.name,
                        "specialty": agent.specialty,
                        "recommendation": "Unable to analyze - check connection",
                        "confidence": 0.0,
                        "reasoning": f"Agent error: {str(e)[:50]}...",
                    }
                )

        return recommendations

    def get_math_recommendation(self, game_state: Dict[str, Any]) -> str:
        """Simple math-based recommendation"""
        bet_to_call = game_state.get("bet_to_call", 0)
        pot_size = game_state.get("pot_size", 10)

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
        position = game_state.get("position", "BTN")

        if position in ["UTG", "MP"]:
            return "TIGHT play - early position"
        elif position in ["CO", "BTN"]:
            return "AGGRESSIVE play - late position advantage"
        else:  # SB, BB
            return "DEFEND or FOLD based on hand strength"

    def get_group_discussion(self, game_state: Dict[str, Any], question: str) -> str:
        """Get collaborative agent discussion with consolidated recommendation"""
        if not self.chat_manager:
            # Create consolidated mock recommendation
            pot_odds = (
                game_state.get("bet_to_call", 0)
                / (game_state.get("pot_size", 10) + game_state.get("bet_to_call", 0))
                if game_state.get("bet_to_call", 0) > 0
                else 0
            )
            position = game_state.get("position", "BTN")

            # Determine primary recommendation based on simple heuristics
            if pot_odds < 0.25:
                primary_action = "CALL"
                confidence = "High"
            elif pot_odds > 0.5:
                primary_action = "FOLD"
                confidence = "High"
            else:
                primary_action = "RAISE" if position in ["BTN", "CO"] else "CALL"
                confidence = "Medium"

            return f"""🎯 CONSOLIDATED RECOMMENDATION: {primary_action} ({confidence} Confidence)

📋 AGENT ANALYSIS SUMMARY:
• RulesAgent: All actions legal - focus on optimal EV play
• MathAgent: Pot odds {pot_odds:.1%} suggest {"profitable" if pot_odds < 0.33 else "marginal" if pot_odds < 0.5 else "unprofitable"} continuation
• PositionAgent: {position} position {"favors aggression" if position in ["BTN", "CO"] else "requires caution"}
• JonathanAgent: WPH patterns support {"value-focused" if primary_action == "RAISE" else "disciplined"} approach

💡 REASONING: {"Strong pot odds and position support aggressive play" if primary_action == "RAISE" else "Pot odds justify call with drawing potential" if primary_action == "CALL" else "Poor pot odds warrant disciplined fold"}"""

        # Get individual agent recommendations first
        recommendations = []
        if self.agents:
            for agent in self.agents:
                try:
                    rec = agent.get_recommendation(game_state)
                    recommendations.append(
                        {
                            "agent": rec.get("agent", agent.name),
                            "action": rec.get("recommendation", "No recommendation"),
                            "reasoning": rec.get("reasoning", "No reasoning provided")[
                                :100
                            ]
                            + "..."
                            if len(rec.get("reasoning", "")) > 100
                            else rec.get("reasoning", "No reasoning provided"),
                        }
                    )
                except Exception as e:
                    recommendations.append(
                        {
                            "agent": agent.name,
                            "action": "Analysis failed",
                            "reasoning": f"Error: {str(e)[:50]}...",
                        }
                    )

        # Consolidate recommendations into single suggestion
        action_votes = {}
        for rec in recommendations:
            action = rec["action"].upper()
            # Extract primary action (CALL, FOLD, RAISE, BET, CHECK)
            primary_action = "CALL"
            for keyword in ["FOLD", "RAISE", "BET", "CHECK", "CALL"]:
                if keyword in action:
                    primary_action = keyword
                    break
            action_votes[primary_action] = action_votes.get(primary_action, 0) + 1

        # Determine consensus recommendation
        if action_votes:
            consensus_action = max(action_votes.keys(), key=lambda x: action_votes[x])
            vote_count = action_votes[consensus_action]
            confidence = (
                "High" if vote_count >= 3 else "Medium" if vote_count >= 2 else "Low"
            )
        else:
            consensus_action = "FOLD"
            confidence = "Low"
            vote_count = 0

        # Format consolidated response
        result = f"🎯 CONSOLIDATED RECOMMENDATION: {consensus_action} ({confidence} Confidence)\n\n"
        result += "📋 AGENT ANALYSIS SUMMARY:\n"

        for rec in recommendations:
            result += f"• {rec['agent']}: {rec['reasoning']}\n"

        # Add consensus reasoning
        result += f"\n💡 CONSENSUS REASONING: {vote_count} agents recommend {consensus_action.lower()}ing based on combined analysis of position, pot odds, and strategic considerations."

        return result

    def display_hand(
        self, game_state: Dict[str, Any], recommendations: List[Dict[str, Any]]
    ):
        """Display the poker hand with visualization"""
        print("\n" + "=" * 60)
        print(f"📊 HAND #{self.hands_played + 1}")
        print("=" * 60)

        # Game state info
        print(f"Street: {game_state.get('street', 'preflop').upper()}")
        print(f"Position: {game_state['position']}")
        print(f"Hole Cards: {game_state['hole_cards']}")
        if game_state.get("board"):
            print(f"Board: {game_state['board']}")
        print(f"Stack: ${game_state['stack_size']}")
        print(f"Pot: ${game_state['pot_size']}")
        print(f"Bet to Call: ${game_state['bet_to_call']}")
        print(f"Opponents: {game_state['opponents']}")

        # Agent recommendations
        print("\n🤖 AGENT RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(
                f"{i}. {rec['agent']}: {rec['recommendation']} ({rec['confidence']:.1%})"
            )

        # Create and show visualization (GUI shows only game state, recommendations in terminal)
        try:
            self.visualizer.visualize_game_state(game_state)
            plt.show(block=False)  # Non-blocking show
            plt.pause(0.1)  # Brief pause to render
        except Exception as e:
            print(f"⚠️ Visualization error: {e}")

    def process_action(self, action: str, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process player action and simulate complete hand progression"""
        bet_amount = 0
        
        # Parse bet/raise amount
        if action.startswith("bet") or action.startswith("raise"):
            try:
                parts = action.split()
                if len(parts) > 1:
                    bet_amount = float(parts[1])
                else:
                    bet_amount = max(game_state["bet_to_call"] * 2, 5)  # Default raise
            except (ValueError, IndexError):
                bet_amount = 5

        print("\n🎲 HAND PROGRESSION:")
        print("=" * 50)
        
        # Handle fold immediately
        if action == "fold":
            print(f"📉 PREFLOP: You fold {game_state['hole_cards']}")
            print("💰 RESULT: Folded - no further action")
            
            result_amount = -game_state.get("bet_to_call", 0)
            self.current_stack += result_amount
            
            result = {
                "action": action,
                "outcome": "fold",
                "amount_change": result_amount,
                "new_stack": self.current_stack,
                "hand_progression": ["Folded preflop - hand ends"]
            }
        else:
            # Simulate complete hand progression
            progression = self.simulate_hand_progression(action, bet_amount, game_state)
            result = progression
            
            # Update stack
            self.current_stack += result["amount_change"]
            result["new_stack"] = self.current_stack

        # Store hand history
        hand_result = {
            "hand_number": self.hands_played + 1,
            "game_state": game_state.copy(),
            "action": action,
            "outcome": result["outcome"],
            "stack_change": result["amount_change"],
            "final_stack": self.current_stack,
            "progression": result.get("hand_progression", [])
        }
        self.session_hands.append(hand_result)

        return result

    def simulate_hand_progression(self, action: str, bet_amount: float, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate complete hand from current action to river"""
        progression = []
        current_pot = game_state["pot_size"]
        board_cards = game_state.get("board", "").split() if game_state.get("board") else []
        street = game_state.get("street", "preflop")
        hero_cards = game_state["hole_cards"]
        position = game_state["position"]
        
        # Calculate hand strength for outcome probability
        hand_strength = self.evaluate_hand_strength(hero_cards, board_cards)
        
        # Show initial action
        initial_action = f"📈 {street.upper()}: You {action}"
        if bet_amount > 0:
            initial_action += f" ${bet_amount}"
            current_pot += bet_amount
        else:
            current_pot += game_state.get("bet_to_call", 0)
        
        progression.append(initial_action)
        print(initial_action)
        
        # Simulate opponent responses and remaining streets
        total_invested = bet_amount if bet_amount > 0 else game_state.get("bet_to_call", 0)
        streets_to_play = []
        
        # Determine which streets to play based on current street
        street_order = ["preflop", "flop", "turn", "river"]
        current_index = street_order.index(street) if street in street_order else 0
        
        for i in range(current_index + 1, len(street_order)):
            streets_to_play.append(street_order[i])
        
        # Generate board cards for remaining streets
        all_cards = []
        if not board_cards:  # Starting preflop
            all_cards = self.generate_board()  # This will be flop+turn+river
            board_cards = all_cards[:3]  # Flop
        elif len(board_cards) == 3:  # Currently on flop
            all_cards = board_cards + self.generate_board()[3:5]  # Add turn+river
        elif len(board_cards) == 4:  # Currently on turn
            all_cards = board_cards + [self.generate_board()[4]]  # Add river
        else:
            all_cards = board_cards
        
        # Simulate each street
        for i, next_street in enumerate(streets_to_play):
            # Update board
            if next_street == "flop" and len(board_cards) == 0:
                board_cards = all_cards[:3]
                board_str = " ".join(board_cards)
                street_msg = f"🃏 FLOP: {board_str} (pot: ${current_pot})"
                progression.append(street_msg)
                print(street_msg)
                
            elif next_street == "turn" and len(board_cards) == 3:
                board_cards = all_cards[:4]
                turn_card = all_cards[3]
                current_pot += random.uniform(5, 15)  # Betting action
                street_msg = f"🃏 TURN: {turn_card} (pot: ${current_pot:.0f})"
                progression.append(street_msg)
                print(street_msg)
                
            elif next_street == "river" and len(board_cards) == 4:
                board_cards = all_cards[:5]
                river_card = all_cards[4]
                current_pot += random.uniform(10, 25)  # Final betting
                street_msg = f"🃏 RIVER: {river_card} (pot: ${current_pot:.0f})"
                progression.append(street_msg)
                print(street_msg)
                
                # Update hand strength with complete board
                hand_strength = self.evaluate_hand_strength(hero_cards, board_cards)
        
        # Simulate opponent actions throughout
        opponent_action = random.choice(["calls", "raises", "calls"])  # Mostly calls for simplicity
        opp_msg = f"🤖 Opponent {opponent_action}"
        progression.append(opp_msg)
        print(opp_msg)
        
        # Determine final outcome based on hand strength and position
        win_probability = hand_strength
        
        # Adjust probability based on position and action
        if position in ["BTN", "CO"]:
            win_probability += 0.1  # Position advantage
        if action.startswith("raise"):
            win_probability += 0.05  # Aggression bonus
            
        # Final showdown
        final_board = " ".join(all_cards[:5]) if len(all_cards) >= 5 else " ".join(board_cards)
        showdown_msg = f"🎯 SHOWDOWN: {hero_cards} vs Opponent on {final_board}"
        progression.append(showdown_msg)
        print(showdown_msg)
        
        # Determine winner
        if random.random() < win_probability:
            outcome = "win"
            result_amount = current_pot - total_invested
            result_msg = f"🏆 WINNER! You win ${current_pot:.0f} pot"
        else:
            outcome = "lose" 
            result_amount = -total_invested
            opponent_hand = self.generate_opponent_hand()
            result_msg = f"💔 LOSE: Opponent wins with {opponent_hand}"
            
        progression.append(result_msg)
        print(f"\n{result_msg}")
        print(f"💰 Stack Change: ${result_amount:+.0f}")
        
        return {
            "action": action,
            "outcome": outcome,
            "amount_change": result_amount,
            "hand_progression": progression,
            "final_board": final_board,
            "final_pot": current_pot
        }

    def evaluate_hand_strength(self, hero_cards: str, board_cards: List[str]) -> float:
        """Evaluate hand strength (0.0 to 1.0) based on cards"""
        # Simple hand strength evaluation
        cards = hero_cards.split()
        if not cards or len(cards) < 2:
            return 0.5
            
        card1, card2 = cards[0], cards[1]
        
        # Extract ranks and suits
        rank1, suit1 = card1[0], card1[1] if len(card1) > 1 else 'h'
        rank2, suit2 = card2[0], card2[1] if len(card2) > 1 else 'h'
        
        # Basic hand strength
        strength = 0.4  # Base strength
        
        # Premium pairs
        if rank1 == rank2:
            if rank1 in ['A', 'K', 'Q']:
                strength = 0.85  # Premium pairs
            elif rank1 in ['J', 'T', '9']:
                strength = 0.75  # Strong pairs
            else:
                strength = 0.65  # Small pairs
        
        # High cards
        elif rank1 in ['A', 'K'] or rank2 in ['A', 'K']:
            strength = 0.70 if suit1 == suit2 else 0.65  # Suited/unsuited premium
        
        # Suited connectors and good hands
        elif suit1 == suit2:
            strength += 0.1  # Suited bonus
            
        # Adjust for board texture (simplified)
        if board_cards:
            # Reduce strength on dangerous boards
            if len(set(card[1] for card in board_cards)) <= 2:  # Flush possible
                strength *= 0.9
            if any(abs(ord(card[0]) - ord(other[0])) <= 1 for card in board_cards for other in board_cards if card != other):  # Straight possible
                strength *= 0.9
                
        return min(strength, 1.0)

    def generate_opponent_hand(self) -> str:
        """Generate a random opponent hand for display"""
        hands = [
            "Kh Qd", "Jc Ts", "9h 8s", "Ah 5d", "Qd Jh", 
            "Tc 9c", "8d 7h", "As Kd", "Qh Qc", "Jd Jh"
        ]
        return random.choice(hands)

    def show_session_stats(self):
        """Display session statistics"""
        if not self.session_hands:
            print("No hands played yet!")
            return

        total_profit = self.current_stack - self.starting_stack
        win_rate = sum(1 for h in self.session_hands if h["outcome"] == "win") / len(
            self.session_hands
        )

        print("\n📊 SESSION STATS:")
        print(f"Hands Played: {len(self.session_hands)}")
        print(f"Starting Stack: ${self.starting_stack}")
        print(f"Current Stack: ${self.current_stack}")
        print(f"Profit/Loss: ${total_profit:+.2f}")
        print(f"Win Rate: {win_rate:.1%}")

        # Show recent hands
        print("\n📝 RECENT HANDS:")
        for hand in self.session_hands[-5:]:
            result_symbol = (
                "✅"
                if hand["outcome"] == "win"
                else "❌"
                if hand["outcome"] == "lose"
                else "🤝"
                if hand["outcome"] == "chop"
                else "❌"
            )
            print(
                f"Hand {hand['hand_number']}: {hand['action']} → {hand['outcome']} {result_symbol} (${hand['stack_change']:+.2f})"
            )

    def main_loop(self):
        """Main interactive loop"""
        print("🎰 INTERACTIVE POKER SIMULATOR")
        print("=" * 60)
        print("Commands:")
        print("  'new' or 'n' - Deal new hand")
        print("  'fold', 'call', 'check', 'bet X', 'raise X' - Make action")
        print("  'discuss QUESTION' - Ask agents to discuss strategy")
        print("  'stats' - Show session statistics")
        print("  'reset' - Reset stack and start over")
        print("  'quit' or 'q' - Exit simulator")
        print("=" * 60)

        current_game_state = None
        current_recommendations = None

        while True:
            try:
                command = input("\n🎯 Enter command: ").strip().lower()

                if command in ["quit", "q", "exit"]:
                    print("\n👋 Thanks for playing!")
                    self.show_session_stats()
                    break

                elif command in ["new", "n", "deal"]:
                    current_game_state = self.generate_random_hand()
                    current_recommendations = self.get_agent_recommendations(
                        current_game_state
                    )
                    self.display_hand(current_game_state, current_recommendations)

                elif command == "stats":
                    self.show_session_stats()

                elif command == "reset":
                    self.current_stack = self.starting_stack
                    self.hands_played = 0
                    self.session_hands = []
                    print("🔄 Session reset! Stack back to $100")

                elif command.startswith("discuss "):
                    if current_game_state:
                        question = command[8:]  # Remove 'discuss '
                        print(f"\n💬 AGENT DISCUSSION: {question}")
                        print("-" * 60)
                        discussion = self.get_group_discussion(
                            current_game_state, question
                        )
                        print(discussion)
                    else:
                        print("❌ No active hand! Deal a new hand first with 'new'")

                elif (
                    command in ["fold", "call", "check"]
                    or command.startswith("bet")
                    or command.startswith("raise")
                ):
                    if current_game_state:
                        result = self.process_action(command, current_game_state)
                        self.hands_played += 1

                        # Final summary is already shown in the hand progression
                        print("\n" + "=" * 50)
                        print(f"📊 HAND #{self.hands_played + 1} COMPLETE")
                        print(f"💰 Final Stack: ${result['new_stack']}")
                        print("=" * 50)

                        # Clear current hand
                        current_game_state = None
                        current_recommendations = None

                        # Close any open plots
                        plt.close("all")
                    else:
                        print("❌ No active hand! Deal a new hand first with 'new'")

                elif command in ["help", "h"]:
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
