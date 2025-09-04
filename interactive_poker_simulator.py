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
from game.poker_engine import SimplifiedPokerEngine
from visualization.table_view import PokerTableVisualizer
from setup import KnowledgeBaseSetup

# Try to import agents and autogen - fallback to None if not available
try:
    from agents import RulesAgent, PositionAgent, MathAgent, JonathanAgent
    from autogen import GroupChat, GroupChatManager  # type: ignore
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AG2/AutoGen not available: {e}")
    print("📝 AG2/AutoGen not available - simulator requires real agents")
    RulesAgent = PositionAgent = MathAgent = JonathanAgent = None
    GroupChat = GroupChatManager = None
    AGENTS_AVAILABLE = False


class InteractivePokerSimulator:
    """Interactive poker simulation with AI agents and visualization"""

    def __init__(self):
        self.engine = SimplifiedPokerEngine()
        self.visualizer = PokerTableVisualizer()
        self.agents = None
        self.chat_manager = None
        self.kb = None
        self.session_hands = []
        self.current_hand_history = []  # Track progression within current hand

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
        if not AGENTS_AVAILABLE:
            print("📝 Agents not available - AG2/AutoGen setup required")
            return
            
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

            # Create agents (type ignore needed because of conditional import)
            rules_agent = RulesAgent(llm_config)  # type: ignore
            position_agent = PositionAgent(llm_config)  # type: ignore
            math_agent = MathAgent(llm_config)  # type: ignore
            jonathan_agent = JonathanAgent(llm_config, knowledge_base=self.kb)  # type: ignore

            self.agents = [rules_agent, position_agent, math_agent, jonathan_agent]

            # Create GroupChat (type ignore needed because of conditional import)
            group_chat = GroupChat(  # type: ignore
                agents=self.agents,
                messages=[],
                max_round=4,  # Short focused discussions
                speaker_selection_method="auto", 
                allow_repeat_speaker=True,  # Allow follow-up for consensus
            )

            self.chat_manager = GroupChatManager(  # type: ignore
                groupchat=group_chat, llm_config=llm_config
            )

            print(f"✅ Created {len(self.agents)} AI agents with GroupChat")

        except Exception as e:
            print(f"⚠️ Agent setup failed: {e}")
            print("💡 Diagnostic info:")
            print("   • Check if AG2/AutoGen is installed: pip install ag2")
            print("   • Check if Ollama is running: curl http://localhost:11434")
            print("   • Check if llama3.2 model is available: ollama list")
            print("   • Real agent setup required - simulator will not function without agents")
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

    def generate_hand_with_progression(self) -> Dict[str, Any]:
        """Generate a poker hand with complete street-by-street progression"""
        # Generate the final state
        final_state = self.generate_random_hand()
        
        # Build progression history
        self.current_hand_history = []
        
        # Preflop
        preflop_state = {
            "street": "preflop",
            "position": final_state["position"],
            "hole_cards": final_state["hole_cards"],
            "stack_size": final_state["stack_size"],
            "pot_size": 3.0,  # Blinds
            "bet_to_call": 2.0,  # Big blind
            "opponents": final_state["opponents"]
        }
        
        # Build realistic action descriptions based on hole cards
        hole_cards = final_state.get("hole_cards", "")
        position = final_state.get("position", "BTN")
        
        # If we have a board, build the progression
        if final_state.get("board"):
            board_cards = final_state["board"].split()
            
            # Preflop action
            if "9" in hole_cards:
                preflop_state["action"] = f"Called from {position} with pocket 9s, 3 opponents see flop"
            else:
                preflop_state["action"] = f"Called from {position}, 3 opponents see flop"
            
            # Flop
            if len(board_cards) >= 3:
                flop_cards = " ".join(board_cards[:3])
                flop_state = preflop_state.copy()
                flop_state.update({
                    "street": "flop",
                    "board": flop_cards,
                    "pot_size": final_state["pot_size"] * 0.4,
                    "bet_to_call": final_state["bet_to_call"] * 0.3
                })
                
                # Determine flop action based on board texture
                if "9" in flop_cards and "9" in hole_cards:
                    flop_state["action"] = "Hit bottom set on flop! Called opponent's bet"
                else:
                    flop_state["action"] = "Checked, opponent bet, called"
                
                self.current_hand_history.append(flop_state)
            
            # Turn
            if len(board_cards) >= 4:
                turn_cards = " ".join(board_cards[:4])
                turn_state = flop_state.copy() if 'flop_state' in locals() else preflop_state.copy()
                turn_state.update({
                    "street": "turn", 
                    "board": turn_cards,
                    "pot_size": final_state["pot_size"] * 0.7,
                    "bet_to_call": final_state["bet_to_call"] * 0.6
                })
                
                # Check for paired board (full house potential)
                board_ranks = [card[0] for card in board_cards[:4]]
                if len(set(board_ranks)) < len(board_ranks):
                    turn_state["action"] = "Turn pairs the board - now have full house! Opponent bets"
                else:
                    turn_state["action"] = "Turn card changes nothing, opponent bets again"
                
                self.current_hand_history.append(turn_state)
            
            # River (final state)
            if len(board_cards) == 5:
                river_cards = " ".join(board_cards)
                board_ranks = [card[0] for card in board_cards]
                
                # Check for full house potential
                if "9" in hole_cards and board_ranks.count("9") >= 1:
                    final_state["action"] = "River: Full house (9s full) - opponent makes large bet"
                elif len(set(board_ranks)) < len(board_ranks):
                    final_state["action"] = "River: Strong hand with paired board - opponent bets"
                else:
                    final_state["action"] = "River: Opponent makes final bet"
        else:
            preflop_state["action"] = f"Preflop decision from {position}"
            
        # Add states in chronological order: preflop, flop, turn, river
        history = [preflop_state]
        
        # Add intermediate states if they exist
        if 'flop_state' in locals():
            history.append(flop_state)
        if 'turn_state' in locals():
            history.append(turn_state)
        
        # Add final state
        history.append(final_state)
        
        self.current_hand_history = history
        
        return final_state

    def get_agent_recommendations(
        self, game_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get recommendations from AI agents - requires real agents"""
        if not self.agents:
            raise Exception("No agents available. Agent recommendations require AG2/AutoGen setup.")

        # Enhance game state with hand history for better agent context
        enhanced_game_state = game_state.copy()
        if self.current_hand_history:
            enhanced_game_state["hand_history"] = self.current_hand_history

        # Get real agent recommendations
        recommendations = []
        for agent in self.agents:
            try:
                rec = agent.get_recommendation(enhanced_game_state)
                recommendations.append(rec)
            except Exception as e:
                print(f"⚠️ Error from {agent.name}: {e}")
                # Agent error - but still include it in results for transparency
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


    def get_group_discussion(self, game_state: Dict[str, Any], question: str) -> str:
        """Get collaborative agent discussion - requires real agents"""
        
        # Check if agents are available
        if not self.chat_manager or not self.agents:
            return "❌ Real agent discussions require AG2/AutoGen setup. Use 'agents' command for setup instructions."
        
        if len(self.agents) == 0:
            return "❌ No agents initialized for discussion"

        # Create context for multi-agent discussion with hand history
        context = f"""
POKER HAND ANALYSIS REQUEST:

CURRENT SITUATION:
Position: {game_state.get('position', 'Unknown')}
Hole Cards: {game_state.get('hole_cards', 'Unknown')}
Board: {game_state.get('board', 'Preflop')}
Street: {game_state.get('street', 'preflop')}
Pot Size: ${game_state.get('pot_size', 0)}
Stack Size: ${game_state.get('stack_size', 0)}
Bet to Call: ${game_state.get('bet_to_call', 0)}
Opponents: {game_state.get('opponents', 1)}

HAND PROGRESSION HISTORY:"""
        
        # Add hand history if available
        if self.current_hand_history and len(self.current_hand_history) > 1:
            context += "\n"
            for i, state in enumerate(self.current_hand_history[:-1], 1):  # Exclude current state
                street = state.get('street', 'unknown').upper()
                action = state.get('action', 'No action recorded')
                pot = state.get('pot_size', 0)
                bet = state.get('bet_to_call', 0)
                board = state.get('board', '')
                
                context += f"{i}. {street}: {action}\n"
                if board:
                    context += f"   Board: {board} | Pot: ${pot:.1f} | Bet: ${bet:.1f}\n"
                else:
                    context += f"   Pot: ${pot:.1f} | Bet: ${bet:.1f}\n"
        else:
            context += " No previous streets (preflop action)\n"
        
        context += f"""
QUESTION: {question}

DISCUSSION INSTRUCTIONS:
1. ONLY discuss the provided hand situation above - do not invent new scenarios
2. Each agent should provide their specialized analysis of the current decision
3. Work together to reach a FINAL CONSENSUS RECOMMENDATION  
4. End with a clear action: FOLD, CALL, or RAISE (with amount)
5. Keep responses concise and focused on the question

IMPORTANT: Stay focused on the provided hand details and question. Do not create new hands or scenarios.
"""

        try:
            print("🤖 Initiating MultiAgent Discussion...")
            
            # Start group discussion using the GroupChatManager
            chat_result = self.agents[0].initiate_chat(
                recipient=self.chat_manager,
                message=context,
                max_turns=6,  # Shorter discussion to force quick consensus  
                silent=False   # Show the conversation
            )
            
            # Extract the conversation
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                conversation = []
                for msg in chat_result.chat_history:
                    if hasattr(msg, 'content') and hasattr(msg, 'name'):
                        conversation.append(f"**{msg.name}**: {msg.content}")
                    elif isinstance(msg, dict):
                        agent_name = msg.get('name', msg.get('role', 'Agent'))
                        content = msg.get('content', str(msg))
                        conversation.append(f"**{agent_name}**: {content}")
                
                if conversation:
                    result = "💬 MULTI-AGENT DISCUSSION:\n"
                    result += "=" * 60 + "\n"
                    result += "\n".join(conversation)
                    
                    # Try to extract consensus/recommendation from the last few messages
                    consensus = self._extract_consensus(conversation)
                    if consensus:
                        result += "\n" + "-" * 60 + "\n"
                        result += f"🎯 CONSENSUS RECOMMENDATION: {consensus}"
                    
                    result += "\n" + "=" * 60
                    return result
            
            # Fallback if chat_history format is different
            if chat_result:
                return f"💬 AGENT DISCUSSION RESULT:\n{str(chat_result)}"
            else:
                raise Exception("No discussion result returned")
                
        except Exception as e:
            return f"❌ MultiAgent discussion failed: {e}\nPlease check AG2/Ollama setup using 'agents' command."
    
    def _extract_consensus(self, conversation):
        """Extract consensus recommendation from agent conversation"""
        # Look for key phrases in the last few messages
        search_text = " ".join(conversation[-3:]).lower()  # Last 3 messages
        
        # Look for consensus/recommendation keywords
        if "consensus" in search_text or "recommend" in search_text:
            # Extract action words
            if "fold" in search_text:
                return "FOLD - Agents agreed to fold"
            elif "raise" in search_text and "$" in search_text:
                # Try to extract raise amount
                import re
                amounts = re.findall(r'\$(\d+\.?\d*)', search_text)
                if amounts:
                    return f"RAISE to ${amounts[-1]} - Agents agreed to raise"
                else:
                    return "RAISE - Agents agreed to raise"
            elif "call" in search_text:
                return "CALL - Agents agreed to call"
        
        # Fallback: look for any action mentioned
        if "call" in search_text:
            return "CALL - Most recent agent suggestion"
        elif "fold" in search_text:
            return "FOLD - Most recent agent suggestion"
        elif "raise" in search_text:
            return "RAISE - Most recent agent suggestion"
            
        return None

    def display_hand(
        self, game_state: Dict[str, Any], recommendations: List[Dict[str, Any]]
    ):
        """Display the poker hand with visualization and progression history"""
        print("\n" + "=" * 60)
        print(f"📊 HAND #{self.hands_played + 1}")
        print("=" * 60)

        # Show hand progression history if available
        if self.current_hand_history and len(self.current_hand_history) > 1:
            print("📚 HAND PROGRESSION HISTORY:")
            print("-" * 50)
            
            street_emojis = {"preflop": "🃏", "flop": "🎯", "turn": "🔄", "river": "🎰"}
            
            for state in self.current_hand_history[:-1]:  # All except current
                street = state.get('street', 'preflop')
                emoji = street_emojis.get(street, "🃏")
                action = state.get('action', f'{street.title()} action')
                pot = state.get('pot_size', 0)
                bet = state.get('bet_to_call', 0)
                board = state.get('board', '')
                
                print(f"{emoji} {street.upper()}: {action}")
                if board:
                    print(f"   Board: {board} | Pot: ${pot:.1f} | Bet to Call: ${bet:.1f}")
                else:
                    print(f"   Pot: ${pot:.1f} | Bet to Call: ${bet:.1f}")
                print()
            print("-" * 50)

        # Current game state info
        print(f"CURRENT STREET: {game_state.get('street', 'preflop').upper()}")
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
        
        # Generate board cards for remaining streets based on current state
        all_cards = []
        if not board_cards:  # Starting preflop
            # Generate a progressive board (we'll add cards as streets progress)
            all_cards = self.generate_board()  # This could be 3, 4, or 5 cards
        else:
            # Use existing board cards and generate additional ones if needed
            all_cards = board_cards.copy()
            # Add cards as needed for progression
            needed_cards = 5 - len(all_cards)
            if needed_cards > 0:
                additional_cards = self.generate_board()
                # Take only the cards we need
                all_cards.extend(additional_cards[:needed_cards])
        
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
                if len(all_cards) > 3:  # Only proceed if we have a turn card
                    board_cards = all_cards[:4]
                    turn_card = all_cards[3]
                    current_pot += random.uniform(5, 15)  # Betting action
                    street_msg = f"🃏 TURN: {turn_card} (pot: ${current_pot:.0f})"
                    progression.append(street_msg)
                    print(street_msg)
                else:
                    # Skip turn if no turn card available
                    print("⏩ Turn skipped - no turn card available")
                
            elif next_street == "river" and len(board_cards) == 4:
                if len(all_cards) > 4:  # Only proceed if we have a river card
                    board_cards = all_cards[:5]
                    river_card = all_cards[4]
                    current_pot += random.uniform(10, 25)  # Final betting
                    street_msg = f"🃏 RIVER: {river_card} (pot: ${current_pot:.0f})"
                    progression.append(street_msg)
                    print(street_msg)
                else:
                    # Skip river if no river card available
                    print("⏩ River skipped - no river card available")
                
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

    def check_agent_status(self) -> str:
        """Check the status of agents and provide diagnostic information"""
        status = "🔍 AGENT STATUS DIAGNOSTIC:\n"
        status += "=" * 50 + "\n"
        
        if self.agents and self.chat_manager:
            status += f"✅ Agents: {len(self.agents)} agents active\n"
            status += "✅ ChatManager: GroupChatManager initialized\n"
            status += "✅ MultiAgent Discussion: Available\n"
            for i, agent in enumerate(self.agents):
                status += f"   {i+1}. {agent.name} - Ready\n"
        elif self.agents and not self.chat_manager:
            status += f"⚠️ Agents: {len(self.agents)} agents created\n"
            status += "❌ ChatManager: Failed to initialize\n"
            status += "❌ MultiAgent Discussion: Not available\n"
        else:
            status += "❌ Agents: Not initialized - AG2/AutoGen required\n"
            status += "❌ ChatManager: Not available\n"
            status += "❌ MultiAgent Discussion: Not available\n"
            
        status += "\n📋 Requirements for real agents:\n"
        status += "   • AG2/AutoGen installed: pip install ag2\n"
        status += "   • Ollama running on localhost:11434\n"
        status += "   • llama3.2:latest model downloaded\n"
        status += "   • Knowledge base initialized (optional)\n"
        
        return status

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
        print("  'agents' - Check agent status and diagnostics")
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
                    current_game_state = self.generate_hand_with_progression()
                    try:
                        current_recommendations = self.get_agent_recommendations(
                            current_game_state
                        )
                        self.display_hand(current_game_state, current_recommendations)
                    except Exception as e:
                        print(f"❌ Cannot deal new hand: {e}")
                        print("💡 Setup AG2/AutoGen to enable gameplay. Use 'agents' command for instructions.")

                elif command == "stats":
                    self.show_session_stats()

                elif command == "agents":
                    print(self.check_agent_status())

                elif command == "reset":
                    self.current_stack = self.starting_stack
                    self.hands_played = 0
                    self.session_hands = []
                    self.current_hand_history = []  # Clear hand progression
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
                    print("  discuss QUESTION - MultiAgent discussion")
                    print("  stats - Session statistics")
                    print("  agents - Agent status and diagnostics")
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
