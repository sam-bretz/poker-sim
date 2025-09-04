# AG2 Poker Assistant - Codebase Guide

Interactive poker simulator with AI agents powered by AG2/AutoGen framework.

## What It Does

This is an **interactive poker simulator** that provides strategic advice through specialized AI agents. It creates a command-line poker game where you can deal hands, make decisions, and get real-time strategy recommendations from four different AI poker experts.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama (local AI)
ollama serve
ollama pull llama3.2

# 3. Run simulator
python3 interactive_poker_simulator.py
```

## Core Architecture

### 🤖 Four Specialized AI Agents
- **RulesAgent**: Validates legal moves and game mechanics
- **MathAgent**: Calculates pot odds, equity, and probability
- **PositionAgent**: Analyzes table position and range strategy
- **JonathanAgent**: Applies Jonathan Little's tournament strategy (with RAG)

### 🎮 Interactive Game Loop
```
Deal Hand → Get Agent Advice → Make Decision → See Results → Repeat
```

### 🧠 Knowledge System
- **RAG Integration**: Scrapes real poker training episodes from Jonathan Little's site
- **ChromaDB**: Vector database storing poker strategies and hand analyses
- **Contextual Advice**: Agents reference actual poker content for recommendations

## How It Works

### 1. **Initialization Phase**
```python
# Sets up knowledge base by scraping poker episodes
setup_knowledge_base() → ChromaDB with real strategy content

# Creates 4 AI agents using Ollama (local LLM)
setup_agents() → [RulesAgent, MathAgent, PositionAgent, JonathanAgent]
```

### 2. **Game Session**
```python
# Generate realistic poker scenario
generate_random_hand() → {position, cards, pot_size, opponents}

# Get recommendations from all agents
get_agent_recommendations() → [4 strategic recommendations]

# Display visual poker table
visualize_game_state() → matplotlib poker table with advice
```

### 3. **Decision Making**
- **User Input**: `fold`, `call`, `raise 25`, `discuss "Should I bluff?"`
- **Agent Collaboration**: Group discussions via AutoGen's GroupChat
- **Outcome Simulation**: Realistic win/loss results based on actions

### 4. **Learning Loop**
- **Session Tracking**: Win rate, profit/loss, hand history
- **Strategy Insights**: Real poker content via RAG system
- **Visual Feedback**: Live poker table visualization

## Interactive Commands

```bash
# Start the simulator
python3 interactive_poker_simulator.py

# In the simulator:
new                           # Deal new hand
fold                         # Fold current hand  
call                         # Call the bet
raise 25                     # Raise to $25
discuss "Should I bluff?"    # Ask agents for advice
stats                        # View session stats
quit                         # Exit
```

## Codebase Walkthrough Guide

### 📚 Learning Path: From Beginner to Expert

#### Phase 1: Understanding the Big Picture (5-10 minutes)
1. **Start Here**: `README.md` (this file) - Project purpose and architecture
2. **Dependencies**: `requirements.txt` - Technologies used
3. **Entry Point**: `interactive_poker_simulator.py` - Main application

#### Phase 2: The AI Agents (15-20 minutes)
1. **Base Foundation**: `agents/base_agent.py` - Common agent framework
2. **Specialist Example**: `agents/math_agent.py` - Mathematical analysis
3. **Other Agents**: `agents/rules_agent.py`, `agents/position_agent.py`, `agents/jonathan_agent.py`

#### Phase 3: Game Engine (10-15 minutes)
1. **Poker Logic**: `game/poker_engine.py` - Hand generation and scenarios
2. **Game States**: How poker situations are created and managed

#### Phase 4: Knowledge System (15-20 minutes)
1. **RAG System**: `knowledge/knowledge_base.py` - Vector database and retrieval
2. **Web Scraping**: `knowledge/wph_scraper.py` - Collecting poker training content
3. **Setup**: `setup/knowledge_base_setup.py` - System initialization

#### Phase 5: Visualization (10 minutes)
1. **Poker Table**: `visualization/table_view.py` - Matplotlib graphics

### 🔍 Key Code Patterns

#### Agent Pattern
```python
class SpecialistAgent(BaseAgent):
    def __init__(self, llm_config):
        self.specialty = "specific domain"
    
    def get_recommendation(self, game_state):
        # Analyze situation
        # Return structured advice
```

#### Error Resilience Pattern
```python
try:
    # Try the ideal approach
    result = complex_operation()
except Exception as e:
    # Graceful fallback
    result = simple_fallback()
    print(f"⚠️ Warning: {e}")
```

#### Mock Data Pattern
```python
if not self.real_system_available:
    # Provide realistic mock data
    return mock_realistic_response()
```

## Project Structure

```
poker-assistant-ag2/
├── agents/                    # AI agent implementations (4 specialists)
│   ├── base_agent.py         # Base agent class (3.2K)
│   ├── jonathan_agent.py     # Jonathan Little strategy (8.8K)
│   ├── math_agent.py         # Mathematical analysis (10K)
│   ├── position_agent.py     # Position strategy (9.8K)
│   └── rules_agent.py        # Game rules validation (5.9K)
├── game/
│   └── poker_engine.py       # Simplified poker engine (12K)
├── knowledge/
│   ├── knowledge_base.py     # RAG knowledge base (17K)
│   └── wph_scraper.py        # WPH episode scraper (17K)
├── setup/
│   └── knowledge_base_setup.py  # KB initialization (9K)
├── visualization/
│   └── table_view.py         # Poker table graphics (14K)
├── interactive_poker_simulator.py  # Main CLI app (18K)
├── requirements.txt          # Dependencies
└── README.md                # This guide
```

## Technical Stack

- **AG2/AutoGen**: Multi-agent conversation framework
- **Ollama**: Local LLM (llama3.2) - no API keys needed
- **ChromaDB**: Vector database for poker knowledge
- **Matplotlib**: Real-time poker table visualization
- **BeautifulSoup**: Web scraping for training content
- **Sentence Transformers**: Text embeddings for RAG

## Example User Experience

```bash
🎯 Enter command: new
📊 HAND #1
Position: BTN (Button)
Hole Cards: Ac Kd
Pot: $12, Bet to Call: $5

🤖 AGENT RECOMMENDATIONS:
1. RulesAgent: All actions legal - proceed with strategy (95%)
2. MathAgent: CALL - good pot odds (85%) 
3. PositionAgent: AGGRESSIVE play - late position advantage (82%)
4. JonathanAgent: Apply GTO principles with value betting (90%)

🎯 Enter command: raise 15
🎲 RESULT: WIN - Stack Change: +$27
```

## Smart Features

- **Mock Mode**: Works without AI agents for testing
- **Rate Limiting**: Respects scraping limits on poker sites
- **Error Recovery**: Graceful fallbacks when components fail
- **Session Persistence**: Tracks performance across hands
- **Consolidated Recommendations**: Agents provide unified advice

## For New Developers

### The Elevator Pitch (30 seconds)
"This is a poker learning tool. You play poker hands, and four AI experts give you advice on what to do. It's like having poker coaches watching over your shoulder."

### Common Stumbling Points
1. **AG2/AutoGen**: Multi-agent framework - multiple AIs collaborating
2. **RAG System**: Retrieval-Augmented Generation - AI with knowledge lookup
3. **Mock vs Real**: Fallbacks everywhere for component failures
4. **Poker Domain**: Basic poker knowledge helpful but not required
5. **Async Patterns**: Background operations like web scraping

### Next Steps After Understanding
1. **Run the System**: Experience the interactive interface
2. **Modify an Agent**: Change recommendation logic
3. **Add Features**: Implement new poker scenarios
4. **Debug Issues**: Practice error handling patterns
5. **Extend Knowledge**: Add new RAG data sources

---

*Built to demonstrate AG2 multi-agent systems in a practical, visual application with real-world poker strategy integration.*