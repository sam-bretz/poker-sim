"""
Knowledge Base for Jonathan Little's poker strategies using ChromaDB.
Implements RAG (Retrieval Augmented Generation) for poker strategy lookup.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import json
import os
import logging
from .wph_scraper import PokerHand, WPHScraper

logger = logging.getLogger(__name__)


class PokerKnowledgeBase:
    """RAG knowledge base for poker strategies from WPH episodes"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)

        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )

        # Create collections
        self.hands_collection = self._get_or_create_collection("poker_hands")
        self.strategies_collection = self._get_or_create_collection("poker_strategies")

    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.client.get_collection(
                name, embedding_function=self.embedding_function  # type: ignore
            )
        except Exception:
            return self.client.create_collection(
                name, embedding_function=self.embedding_function  # type: ignore
            )

    def index_poker_hands(self, hands: List[PokerHand]):
        """Index poker hands in the knowledge base"""
        logger.info(f"Indexing {len(hands)} poker hands...")

        documents = []
        metadatas = []
        ids = []

        for hand in hands:
            # Create comprehensive document text
            doc_text = self._create_hand_document(hand)
            documents.append(doc_text)

            # Create metadata
            metadata = {
                "episode": hand.episode_number,
                "title": hand.title,
                "url": hand.url,
                "position": hand.position_info,
                "stacks": hand.stack_sizes,
                "pot": hand.pot_size,
                "type": "hand_analysis",
            }
            metadatas.append(metadata)

            # Create unique ID using episode number and title hash to avoid duplicates
            title_hash = (
                hash(hand.title) % 1000
            )  # Simple hash to differentiate same episode numbers
            unique_id = f"hand_{hand.episode_number}_{title_hash}"
            ids.append(unique_id)

        # Add to collection
        self.hands_collection.add(documents=documents, metadatas=metadatas, ids=ids)

        logger.info(f"Successfully indexed {len(hands)} hands")

    def index_strategies(self, hands: List[PokerHand]):
        """Index strategic insights separately for better retrieval"""
        logger.info(f"Indexing strategic insights from {len(hands)} hands...")

        documents = []
        metadatas = []
        ids = []

        for hand in hands:
            # Index key learnings
            for i, learning in enumerate(hand.key_learnings):
                if learning and len(learning.strip()) > 20:
                    documents.append(learning)
                    metadatas.append(
                        {
                            "episode": hand.episode_number,
                            "title": hand.title,
                            "type": "key_learning",
                            "context": hand.situation[:100],  # Brief context
                        }
                    )
                    title_hash = hash(hand.title) % 1000
                    ids.append(f"learning_{hand.episode_number}_{title_hash}_{i}")

            # Index strategic analysis
            if hand.strategic_analysis and len(hand.strategic_analysis.strip()) > 50:
                documents.append(hand.strategic_analysis)
                metadatas.append(
                    {
                        "episode": hand.episode_number,
                        "title": hand.title,
                        "type": "strategic_analysis",
                        "position": hand.position_info,
                        "stacks": hand.stack_sizes,
                    }
                )
                title_hash = hash(hand.title) % 1000
                ids.append(f"analysis_{hand.episode_number}_{title_hash}")

        # Add to strategies collection
        if documents:
            self.strategies_collection.add(
                documents=documents, metadatas=metadatas, ids=ids
            )
            logger.info(f"Successfully indexed {len(documents)} strategic insights")

    def _create_hand_document(self, hand: PokerHand) -> str:
        """Create a comprehensive document from a poker hand"""
        doc_parts = [
            f"Episode {hand.episode_number}: {hand.title}",
            f"Situation: {hand.situation}",
            f"Position: {hand.position_info}",
            f"Stack Sizes: {hand.stack_sizes}",
            f"Pot Size: {hand.pot_size}",
            "",
            "Action Sequence:",
        ]

        for i, action in enumerate(hand.action_sequence):
            doc_parts.append(f"  {i + 1}. {action}")

        doc_parts.extend(
            ["", "Strategic Analysis:", hand.strategic_analysis, "", "Key Learnings:"]
        )

        for learning in hand.key_learnings:
            doc_parts.append(f"  - {learning}")

        return "\n".join(doc_parts)

    def search_similar_hands(
        self, query: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar poker hands based on query"""
        try:
            results = self.hands_collection.query(
                query_texts=[query], n_results=n_results
            )

            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i]
                        if results["metadatas"]
                        else {},
                        "distance": results["distances"][0][i]
                        if results["distances"]
                        else 0,
                    }
                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching hands: {e}")
            return []

    def search_strategies(
        self, query: str, n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for strategic insights based on query"""
        try:
            results = self.strategies_collection.query(
                query_texts=[query], n_results=n_results
            )

            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i]
                        if results["metadatas"]
                        else {},
                        "distance": results["distances"][0][i]
                        if results["distances"]
                        else 0,
                    }
                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching strategies: {e}")
            return []

    def get_context_for_situation(
        self, situation: str, position: str = "", stacks: str = "", pot_odds: str = ""
    ) -> str:
        """Get relevant context for a specific poker situation"""

        # Build query from situation components
        query_parts = [situation]
        if position:
            query_parts.append(f"position {position}")
        if stacks:
            query_parts.append(f"stacks {stacks}")
        if pot_odds:
            query_parts.append(f"pot odds {pot_odds}")

        query = " ".join(query_parts)

        # Search both hands and strategies
        hand_results = self.search_similar_hands(query, n_results=3)
        strategy_results = self.search_strategies(query, n_results=5)

        # Build context string
        context_parts = []

        if hand_results:
            context_parts.append("=== Similar Hand Examples ===")
            for i, result in enumerate(hand_results[:2]):  # Top 2 hands
                context_parts.append(
                    f"\nExample {i + 1} (Episode {result['metadata'].get('episode', 'Unknown')}):"
                )
                context_parts.append(result["content"][:300] + "...")

        if strategy_results:
            context_parts.append("\n\n=== Relevant Strategic Insights ===")
            for i, result in enumerate(strategy_results[:3]):  # Top 3 strategies
                episode = result["metadata"].get("episode", "Unknown")
                insight_type = result["metadata"].get("type", "insight")
                context_parts.append(
                    f"\n{insight_type.replace('_', ' ').title()} (Episode {episode}):"
                )
                context_parts.append(result["content"])

        return "\n".join(context_parts)

    def load_and_index_from_file(self, json_file: str):
        """Load hands from JSON file and index them"""
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                hand_data = json.load(f)

            # Convert to PokerHand objects
            hands = []
            for data in hand_data:
                hand = PokerHand(**data)
                hands.append(hand)

            # Index both hands and strategies
            self.index_poker_hands(hands)
            self.index_strategies(hands)

            logger.info(f"Loaded and indexed {len(hands)} hands from {json_file}")
            return hands

        except Exception as e:
            logger.error(f"Error loading from file {json_file}: {e}")
            return []

    def setup_knowledge_base(
        self, start_episode: int = 1, end_episode: int = 10, force_refresh: bool = False
    ):
        """Complete setup of the knowledge base - scrapes real WPH episodes"""

        # Check multiple possible data file locations
        # Prioritize files with episode range in name for clarity
        possible_files = [
            f"data/wph_episodes_{start_episode}_{end_episode}.json",  # Primary naming convention
            f"wph_episodes_{start_episode}_{end_episode}.json",  # Root directory fallback
        ]

        # Also check for any existing quality data files in data directory
        if os.path.exists("data"):
            # Look for files with episode ranges (e.g., wph_episodes_550_560.json)
            for file in os.listdir("data"):
                if file.startswith("wph_episodes_") and file.endswith(".json"):
                    # Skip backup files
                    if "backup" not in file and "summary" not in file:
                        possible_files.append(f"data/{file}")

        # Try to load existing data if not forcing refresh
        if not force_refresh:
            for json_file in possible_files:
                if os.path.exists(json_file):
                    logger.info(f"📁 Found existing data file: {json_file}")
                    try:
                        hands = self.load_and_index_from_file(json_file)
                        if hands:
                            logger.info(
                                f"✅ Successfully loaded {len(hands)} hands from existing data"
                            )
                            logger.info(
                                f"💾 Skipping scraping - using cached data from {json_file}"
                            )
                            return hands
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Failed to load {json_file}, trying next file: {e}"
                        )
                        continue

            logger.info("📭 No usable existing data files found")
        else:
            logger.info("🔄 Force refresh requested - will scrape fresh data")

        # Scrape fresh data - this is required, no fallback
        logger.info(f"🕷️ Scraping episodes {start_episode} to {end_episode}...")
        logger.info(
            "⏱️ This may take a few minutes depending on the number of episodes..."
        )

        try:
            scraper = WPHScraper()
            hands = scraper.scrape_episodes(start_episode, end_episode)

            if not hands:
                raise Exception(
                    "No hands were successfully scraped. Check internet connection and site accessibility."
                )

            # Save scraped data (returns git-friendly paths)
            main_json_file = f"wph_episodes_{start_episode}_{end_episode}.json"
            git_file, summary_file = scraper.save_to_json(hands, main_json_file)

            # Index the data
            self.index_poker_hands(hands)
            self.index_strategies(hands)

            logger.info(f"Successfully set up knowledge base with {len(hands)} hands")
            logger.info(f"Data saved for git commit: {git_file}")
            logger.info(f"Summary available: {summary_file}")

            return hands

        except Exception as e:
            logger.error(f"Failed to scrape episodes: {e}")
            logger.error(
                "Knowledge base setup requires successful scraping of WPH episodes."
            )
            raise Exception(f"Knowledge base setup failed: {e}")

    def quick_setup(self):
        """Quick setup with quality episodes that have actual strategy content"""
        # Use newer episodes (550+) which have real strategic content
        # Older episodes (1-100) often just have audio/video links
        return self.setup_knowledge_base(start_episode=550, end_episode=560)

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            hands_count = self.hands_collection.count()
            strategies_count = self.strategies_collection.count()

            return {
                "hands_indexed": hands_count,
                "strategies_indexed": strategies_count,
                "total_documents": hands_count + strategies_count,
            }
        except Exception:
            return {"error": "Could not retrieve stats"}

    def get_available_data_files(self) -> Dict[str, Any]:
        """Check what data files are available on disk"""
        available_files = []

        # Check root directory
        for pattern in ["wph_episodes_*.json"]:
            import glob

            for file in glob.glob(pattern):
                try:
                    stat = os.stat(file)
                    available_files.append(
                        {
                            "file": file,
                            "size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "modified": stat.st_mtime,
                            "location": "root",
                        }
                    )
                except OSError:
                    pass

        # Check data directory
        if os.path.exists("data"):
            for file in os.listdir("data"):
                if file.startswith("wph_") and file.endswith(".json"):
                    filepath = f"data/{file}"
                    try:
                        stat = os.stat(filepath)
                        available_files.append(
                            {
                                "file": filepath,
                                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                "modified": stat.st_mtime,
                                "location": "data",
                            }
                        )
                    except OSError:
                        pass

        return {
            "total_files": len(available_files),
            "files": available_files,
            "has_data": len(available_files) > 0,
        }


if __name__ == "__main__":
    # Test the knowledge base
    kb = PokerKnowledgeBase()

    # Test search
    results = kb.search_strategies("pocket kings preflop raise")
    print(f"Found {len(results)} relevant strategies")

    for i, result in enumerate(results[:3]):
        print(
            f"\n{i + 1}. Episode {result['metadata'].get('episode')}: {result['content'][:100]}..."
        )
