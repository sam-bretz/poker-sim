# AG2 Poker Assistant: Multi-Agent No Limit Texas Hold'em Strategy System

An intelligent poker assistant built with AG2 (formerly AutoGen) that provides strategic advice through specialized AI agents collaborating via GroupChat. The system incorporates strategies from Jonathan Little's Weekly Poker Hand series through a RAG (Retrieval Augmented Generation) knowledge base.

## 🎯 Project Overview

This project demonstrates advanced AG2 framework usage by creating a practical poker strategy assistant that:

- **Multi-Agent Collaboration**: Specialized agents discuss and provide strategic recommendations
- **Domain Knowledge Integration**: RAG system with Jonathan Little's poker strategies
- **Interactive Interface**: Jupyter notebook with visualizations and real-time analysis
- **Practical Application**: Solves real poker decision-making challenges

## 🏗️ Architecture

### Core Components

1. **Specialized Agents** (AG2 ConversableAgents)
   - `RulesAgent`: No Limit Texas Hold'em rules and game mechanics
   - `PositionAgent`: Positional strategy and hand ranges
   - `MathAgent`: Pot odds, equity calculations, and EV analysis  
   - `JonathanAgent`: RAG-enabled agent with WPH knowledge base

2. **Knowledge Base** (ChromaDB + RAG)
   - Web scraper for Weekly Poker Hand episodes
   - Vector storage and semantic search
   - Strategic insight extraction and indexing

3. **Game Engine**
   - Simplified poker game simulation
   - Scenario generation and hand analysis
   - Game state management

4. **Visualization System**
   - Matplotlib-based poker table rendering
   - Card and board visualization
   - Agent recommendation display

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key (for agent functionality)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd poker-assistant-ag2
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY to the .env file
   ```

4. **Launch Jupyter notebook:**
   ```bash
   jupyter notebook poker_assistant.ipynb
   ```

### Quick Demo (Without API Keys)

The system includes demo mode with mock agent responses, allowing you to explore functionality without API keys.

## 🎮 Usage Examples

### Interactive Scenario Analysis

```python
# Create a poker scenario
engine = SimplifiedPokerEngine()
game_state = engine.create_scenario("premium_pair")

# Get agent recommendations
recommendations = get_agent_recommendations(game_state)

# Start group discussion
discussion = get_group_discussion(game_state, "What should I do here?")
```

### Strategy Knowledge Search

```python
# Search Jonathan Little's strategies
kb = PokerKnowledgeBase()
results = kb.search_strategies("pocket aces preflop raise")
```

### Custom Scenario Creation

```python
# Define your own poker situation
custom_state = {
    'position': 'BTN',
    'hole_cards': 'AhKs', 
    'board': 'KhQd7c',
    'pot_size': 25.0,
    'stack_size': 95.0,
    'bet_to_call': 10.0
}

# Get expert analysis
recommendations = get_agent_recommendations(custom_state)
```

## 🤖 Agent Specializations

### RulesAgent
- Hand rankings and game mechanics
- Action validation and legal moves
- Tournament vs cash game differences

### PositionAgent  
- Opening ranges by position
- 3-bet and 4-bet analysis
- Positional advantages and strategy

### MathAgent
- Pot odds and implied odds
- Expected value calculations
- Equity estimation and break-even analysis

### JonathanAgent (RAG-Enabled)
- Access to Weekly Poker Hand knowledge base
- Strategic frameworks and concepts
- Real hand examples and analysis

## 📊 Key Features

### Multi-Agent Collaboration
- AG2 GroupChat orchestration
- Specialized agent discussions
- Consensus building and recommendations

### Knowledge Integration
- RAG system with ChromaDB
- Semantic search of poker strategies
- Context-aware strategy retrieval

### Interactive Interface
- Jupyter notebook with ipywidgets
- Real-time poker table visualization
- Scenario builder and analysis tools

### Practical Value
- Evidence-based strategic advice
- Educational poker content
- Decision-making framework

## 🔧 Technical Implementation

### AG2 Framework Usage

**ConversableAgent Implementation:**
```python
class PositionAgent(BasePokerAgent):
    def __init__(self, llm_config):
        system_message = """You are the Position and Range Expert..."""
        super().__init__(
            name="PositionAgent",
            system_message=system_message,
            specialty="Position and Hand Ranges",
            llm_config=llm_config
        )
```

**GroupChat Setup:**
```python
group_chat = GroupChat(
    agents=[rules_agent, position_agent, math_agent, jonathan_agent],
    messages=[],
    max_round=10,
    speaker_selection_method="auto"
)

chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)
```

### RAG Implementation

**Knowledge Base Creation:**
```python
kb = PokerKnowledgeBase()
hands = scraper.scrape_episodes(1, 100)
kb.index_poker_hands(hands)
kb.index_strategies(hands)
```

**Context Retrieval:**
```python
context = kb.get_context_for_situation(
    situation=query,
    position=position,
    stacks=stacks
)
```

## 📁 Project Structure

```
poker-assistant-ag2/
├── README.md                     # This file
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
├── poker_assistant.ipynb         # Main Jupyter interface
├── agents/                       # AG2 agents
│   ├── __init__.py
│   ├── base_agent.py            # Base agent class
│   ├── rules_agent.py           # Rules specialist
│   ├── position_agent.py        # Position specialist  
│   ├── math_agent.py            # Mathematics specialist
│   └── jonathan_agent.py        # RAG-enabled strategy agent
├── game/                        # Game engine
│   ├── __init__.py
│   └── poker_engine.py          # Simplified poker game
├── knowledge/                   # RAG system
│   ├── __init__.py
│   ├── wph_scraper.py          # Web scraper for WPH
│   └── knowledge_base.py        # ChromaDB integration
├── visualization/               # Poker table display
│   ├── __init__.py
│   └── table_view.py           # Matplotlib visualizations
└── utils/                      # Helper functions
    └── __init__.py
```

## 🎯 Interview Demonstration Points

### AG2 Mastery
- **ConversableAgent**: Custom agents with specialized system messages
- **GroupChat**: Multi-agent collaboration and discussion orchestration  
- **LLM Configuration**: Proper model setup and parameter tuning

### Software Engineering
- **Modular Architecture**: Clean separation of concerns
- **Interactive Interface**: User-friendly Jupyter notebook implementation
- **Error Handling**: Graceful degradation and mock functionality
- **Documentation**: Comprehensive README and code comments

### Domain Expertise
- **Practical Application**: Solves real poker strategy challenges
- **Knowledge Integration**: RAG system with domain-specific content
- **User Experience**: Interactive scenarios and visualizations

## 🚀 Next Steps for Production

1. **Enhanced Knowledge Base**
   - Scrape complete WPH episode collection (100+)
   - Add tournament vs cash game strategy differentiation
   - Implement user feedback learning

2. **Advanced Game Engine**
   - Integrate PokerKit for precise hand evaluation
   - Add opponent modeling and hand history tracking
   - Implement ICM calculations for tournaments

3. **Real-world Integration**
   - Connect to online poker platforms
   - Add real-time hand importing
   - Implement bankroll management advice

4. **Performance Optimization**
   - Cache frequent queries
   - Optimize agent response times
   - Implement batch processing

## 📝 Interview Notes

This project showcases:

- **AG2 Framework Proficiency**: Proper use of ConversableAgent, GroupChat, and GroupChatManager
- **Multi-Agent System Design**: Specialized agents with clear roles and collaboration patterns
- **RAG Implementation**: Domain knowledge integration with semantic search
- **Software Engineering**: Clean architecture, error handling, and documentation
- **Practical Value**: Solves real-world poker strategy challenges

**Time Investment**: ~2 hours for core implementation, following interview requirements

## 🤝 Contributing

This project was created as an interview demonstration. For production use, consider:

1. Adding comprehensive testing
2. Implementing proper logging and monitoring  
3. Adding configuration management
4. Scaling the knowledge base
5. Enhancing the user interface

## 📄 License

MIT License - Feel free to use this project as a learning reference for AG2 and multi-agent systems.

---

**Built with AG2 for intelligent multi-agent poker strategy** 🎰🤖