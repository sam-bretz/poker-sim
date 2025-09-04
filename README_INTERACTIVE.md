# Interactive Poker Simulator

A command-line poker simulation with AI agents and real-time visualizations.

## Features

🎰 **Interactive Poker Hands**
- Generate random poker scenarios
- Visual poker table with cards, pot, and positions
- Real-time agent recommendations with confidence scores

🤖 **AI Agent Integration**
- Rules Agent: Game mechanics and legality
- Math Agent: Pot odds and probability calculations
- Position Agent: Positional strategy and ranges
- Jonathan Agent: Strategies from WPH episodes (RAG-powered)

📊 **Rich Visualizations**
- Professional poker table graphics
- Player positions, hole cards, and community cards
- Agent recommendations panel
- Action buttons and game state display

📈 **Session Tracking**
- Stack management and P&L tracking
- Win rate and performance statistics
- Hand history with outcomes

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Ollama (for AI agents)
```bash
ollama serve
ollama pull llama3.2
```

### 3. Run Interactive Simulator
```bash
python3 interactive_poker_simulator.py
```

## Commands

### Basic Gameplay
- `new` or `n` - Deal a new hand
- `fold` - Fold current hand
- `call` - Call the current bet
- `check` - Check (if no bet to call)
- `bet 15` - Bet $15
- `raise 25` - Raise to $25

### Agent Interaction
- `discuss "Should I 3-bet here?"` - Ask agents to analyze strategy
- `discuss "What's my equity?"` - Get mathematical analysis
- `discuss "How does position affect this?"` - Positional discussion

### Session Management
- `stats` - Show session statistics
- `reset` - Reset stack to $100 and clear history
- `quit` or `q` - Exit simulator

## Example Session

```
🎯 Enter command: new
📊 HAND #1
Street: PREFLOP
Position: BTN
Hole Cards: Kh Qc
Stack: $100.0
Pot: $12.5
Bet to Call: $5.0
Opponents: 2

🤖 AGENT RECOMMENDATIONS:
1. MathAgent: CALL - good pot odds (78.0%)
2. PositionAgent: RAISE - late position advantage (85.0%)
3. JonathanAgent: Build pot with strong hand (88.0%)

[Poker table visualization appears]

🎯 Enter command: discuss "Should I raise or call with KQ here?"

💬 AGENT DISCUSSION: Should I raise or call with KQ here?
RulesAgent: Both raising and calling are legal options here.
MathAgent: KQ has good equity against typical ranges. Raising builds pot with drawing potential.
PositionAgent: Button position gives us post-flop advantage. Raising is preferred.
JonathanAgent: Similar to WPH #45 - KQ suited plays well aggressively in position.
Consensus: RAISE for value and position.

🎯 Enter command: raise 15

🎲 RESULT:
Action: raise 15
Outcome: win
Stack Change: +$27.50
New Stack: $127.50

🎯 Enter command: stats
📊 SESSION STATS:
Hands Played: 1
Starting Stack: $100.0
Current Stack: $127.50
Profit/Loss: +$27.50
Win Rate: 100.0%

📝 RECENT HANDS:
Hand 1: raise 15 → win ✅ (+$27.50)
```

## Visualization Features

### Poker Table Elements
- **Green felt background** with professional appearance
- **Player positions** clearly marked (UTG, MP, CO, BTN, SB, BB)
- **Hole cards** shown face-up for hero, face-down for opponents
- **Community cards** displayed in center when dealt
- **Pot size** prominently displayed
- **Stack sizes** for all players
- **Action buttons** showing available moves

### Agent Recommendations Panel
- **Agent names** and specialties
- **Recommendations** with confidence percentages
- **Color-coded** for easy reading
- **Truncated text** for clean display

## Advanced Features

### Smart Data Loading
- Automatically loads existing WPH episode data
- No re-scraping if data exists on disk
- RAG-powered strategy recommendations

### Session Persistence
- Track performance across multiple hands
- Detailed statistics and win rates
- Hand history with outcomes

### Agent Discussion Mode
- Ask open-ended strategy questions
- Multi-agent collaborative analysis
- Real-time strategy discussions

## File Structure

```
├── interactive_poker_simulator.py    # Main interactive script
├── simple_poker_visualizer.py       # Simple visualization demo
├── test_visualization.py            # Test visualization system
├── visualization/
│   └── table_view.py                # Poker table visualization
├── agents/                          # AI agent implementations
├── game/
│   └── poker_engine.py             # Game logic and scenarios
└── knowledge/                       # RAG knowledge base
```

## Troubleshooting

### No Agent Responses
- Check Ollama is running: `ollama serve`
- Verify model is installed: `ollama pull llama3.2`
- Agents will fall back to mock responses if unavailable

### Visualization Issues
- Ensure matplotlib is installed: `pip install matplotlib`
- On headless systems, images are saved as PNG files
- Close matplotlib windows to free memory

### Knowledge Base Issues
- Check internet connection for scraping
- Existing data files will be used if available
- System works without RAG if knowledge base fails

## Tips for Best Experience

1. **Start with simple commands** like `new` and `call/fold`
2. **Use discussion mode** to learn strategy: `discuss "Why fold here?"`
3. **Check stats regularly** to track your performance
4. **Try different scenarios** - each hand is randomly generated
5. **Experiment with bet sizes** - `bet 10`, `raise 25`, etc.

Enjoy playing poker with AI agents! 🃏🤖