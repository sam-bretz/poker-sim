# AG2 Poker Assistant 

Interactive poker simulator with AI agents powered by AG2/AutoGen framework.

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

## How It Works

**Four AI agents give you poker strategy advice:**
- **Rules Agent**: Validates legal moves
- **Math Agent**: Calculates pot odds and equity  
- **Position Agent**: Advises based on table position
- **Jonathan Agent**: Uses scraped poker training content

**Interactive commands:**
- `new` - Deal a new hand
- `fold/call/raise 25` - Make poker actions
- `discuss "Should I bluff?"` - Ask agents for advice
- `stats` - View your session performance

## Project Structure

```
poker-assistant-ag2/
├── agents/           # AI agents (4 specialized agents)
├── game/            # Poker game engine  
├── knowledge/       # RAG knowledge base
├── visualization/   # Poker table graphics
├── interactive_poker_simulator.py  # Main app
└── requirements.txt # Dependencies
```

## Key Features

- **Visual poker table** with cards and recommendations
- **Session tracking** with win/loss statistics  
- **Real-time agent discussions** about strategy
- **RAG-powered insights** from poker training content
- **Simple command interface** - easy to demo and explain

## Tech Stack

- **AG2**: Multi-agent framework
- **Ollama**: Local LLM (no API keys needed)
- **ChromaDB**: Vector database for strategy knowledge
- **Matplotlib**: Poker visualization

## Demo Commands

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

## Architecture

- **`agents/`**: Four specialized AG2 agents for poker strategy
- **`game/`**: Simplified poker engine for hand generation
- **`knowledge/`**: RAG system with scraped poker training content
- **`visualization/`**: Matplotlib poker table graphics
- **`interactive_poker_simulator.py`**: Main CLI application

---

*Built to demonstrate AG2 multi-agent systems in a practical, visual application.*