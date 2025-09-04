"""
Weekly Poker Hand (WPH) Scraper for Jonathan Little's poker strategy content.
Extracts hand analysis, strategic insights, and learning points from WPH articles.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import os
from typing import List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PokerHand:
    """Represents a poker hand analysis from WPH"""

    episode_number: int
    title: str
    url: str
    situation: str
    action_sequence: List[str]
    strategic_analysis: str
    key_learnings: List[str]
    position_info: str
    stack_sizes: str
    pot_size: str


class WPHScraper:
    """Scraper for Jonathan Little's Weekly Poker Hand articles"""

    def __init__(
        self, base_url: str = "https://jonathanlittlepoker.com", delay: float = 1.0
    ):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

    def generate_wph_urls(
        self, start_episode: int = 1, end_episode: int = 100
    ) -> List[str]:
        """Generate URLs for WPH episodes"""
        urls = []

        # Newer episodes (500+) have better content with actual hand analysis
        # Older episodes are often just audio/video links
        for episode in range(start_episode, end_episode + 1):
            # Modern URL pattern for newer episodes
            if episode >= 500:
                # Try hyphenated pattern (most common for newer episodes)
                url = f"{self.base_url}/wph-{episode}/"
                urls.append(url)
            else:
                # Older episodes use different patterns
                url = f"{self.base_url}/wph{episode}/"
                urls.append(url)

                # Very old episodes might have this pattern
                if episode <= 10:
                    alt_url = f"{self.base_url}/weekly-poker-hand-episode-{episode}/"
                    urls.append(alt_url)

        return urls

    def extract_hand_content(
        self, soup: BeautifulSoup, url: str
    ) -> Optional[PokerHand]:
        """Extract poker hand content from a WPH page"""
        try:
            # Extract episode number from URL
            episode_match = re.search(r"wph-?(\d+)", url)
            episode_number = int(episode_match.group(1)) if episode_match else 0

            # Get title
            title_elem = soup.find("h1", class_="entry-title") or soup.find("h1")
            title = title_elem.get_text().strip() if title_elem else "Unknown Episode"

            # Extract main content - more specific selector
            content_div = soup.find("div", class_="entry-content")

            if not content_div:
                logger.warning(f"Could not find content for {url}")
                return None

            # Get paragraphs to avoid comments/sidebars
            paragraphs = content_div.find_all("p")  # type: ignore

            # Filter out comment prompts and non-strategy content
            strategy_paragraphs = []
            for p in paragraphs:
                text = p.get_text().strip()
                # Skip if it's a comment prompt or too short
                if len(text) > 50 and not any(
                    skip in text.lower()
                    for skip in [
                        "comment",
                        "subscribe",
                        "audiobook",
                        "itunes",
                        "podcast",
                        "free.",
                        "download",
                        "click here",
                    ]
                ):
                    strategy_paragraphs.append(text)

            # Join the filtered paragraphs
            content_text = "\n".join(strategy_paragraphs)

            # Validate we have actual poker content
            poker_terms = [
                "flop",
                "turn",
                "river",
                "preflop",
                "bet",
                "raise",
                "call",
                "fold",
                "stack",
                "pot",
                "position",
                "blind",
            ]
            if not any(term in content_text.lower() for term in poker_terms):
                logger.warning(f"No poker content found in {url}")
                return None

            # Extract key components using patterns
            situation = self._extract_situation(content_text)
            action_sequence = self._extract_action_sequence(content_text)
            strategic_analysis = self._extract_strategic_analysis(content_text)
            key_learnings = self._extract_key_learnings(content_text)
            position_info = self._extract_position_info(content_text)
            stack_sizes = self._extract_stack_info(content_text)
            pot_size = self._extract_pot_info(content_text)

            return PokerHand(
                episode_number=episode_number,
                title=title,
                url=url,
                situation=situation,
                action_sequence=action_sequence,
                strategic_analysis=strategic_analysis,
                key_learnings=key_learnings,
                position_info=position_info,
                stack_sizes=stack_sizes,
                pot_size=pot_size,
            )

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def _extract_situation(self, text: str) -> str:
        """Extract the hand situation/setup"""
        # Look for the opening paragraph describing the scenario
        lines = text.split("\n")

        # Check first few paragraphs for setup info
        for line in lines[:5]:
            if len(line) > 100:  # Substantial paragraph
                # Check if it contains setup information
                setup_indicators = [
                    "flop",
                    "professional poker",
                    "cash game",
                    "tournament",
                    "stakes",
                    "blinds",
                    "high stakes",
                    "lodge",
                    "hustler",
                ]
                if any(indicator in line.lower() for indicator in setup_indicators):
                    return line.strip()[:300]

        # Fallback to specific patterns
        situation_patterns = [
            r"(?i)(blinds?|stakes?)[\s:]+(\$?\d+[/-]\$?\d+)",
            r"(?i)(effective stacks?|stack sizes?)[\s:]+([^\n]+)",
            r"(?i)(tournament|cash game|sit.?n.?go)(.{0,100})",
        ]

        for pattern in situation_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()[:200]

        # Last fallback: first substantial sentence
        sentences = text.split(".")[:5]
        for sentence in sentences:
            if len(sentence) > 50:
                return sentence.strip()[:200]

        return "Hand setup information not available"

    def _extract_action_sequence(self, text: str) -> List[str]:
        """Extract the betting action sequence"""
        actions = []

        # Look for preflop, flop, turn, river sections
        street_patterns = [
            r"(?i)preflop:?\s*(.+?)(?=flop|turn|river|\n\n)",
            r"(?i)flop[^\n]*:?\s*(.+?)(?=turn|river|\n\n)",
            r"(?i)turn[^\n]*:?\s*(.+?)(?=river|\n\n)",
            r"(?i)river[^\n]*:?\s*(.+?)(?=\n\n|$)",
        ]

        for pattern in street_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                street_action = match.group(1).strip()
                if street_action:
                    actions.append(street_action[:300])  # Limit length

        # Also look for action keywords
        action_keywords = [
            "raises",
            "calls",
            "folds",
            "checks",
            "bets",
            "shoves",
            "all-in",
        ]
        sentences = text.split(".")

        for sentence in sentences[:15]:  # Check first 15 sentences
            if any(keyword in sentence.lower() for keyword in action_keywords):
                actions.append(sentence.strip()[:200])

        return actions[:10]  # Limit to 10 actions

    def _extract_strategic_analysis(self, text: str) -> str:
        """Extract Jonathan Little's strategic analysis"""
        # Look for paragraphs with strategic discussion
        paragraphs = text.split("\n")
        strategic_paragraphs = []

        strategic_indicators = [
            "when you",
            "you should",
            "you need to",
            "generally",
            "optimal",
            "correct play",
            "best",
            "strategy",
            "equity",
            "pot odds",
            "range",
            "value bet",
            "bluff",
            "position",
            "stack to pot ratio",
            "outs",
        ]

        for para in paragraphs:
            if len(para) > 100:  # Substantial paragraph
                # Count strategic terms in paragraph
                strategic_count = sum(
                    1 for term in strategic_indicators if term in para.lower()
                )
                if strategic_count >= 2:  # At least 2 strategic terms
                    strategic_paragraphs.append(para.strip())

        # Join the most strategic paragraphs
        if strategic_paragraphs:
            return " ".join(strategic_paragraphs[:2])[:600]

        # Fallback to sentence-based extraction
        sentences = text.split(".")
        strategic_sentences = []

        for sentence in sentences:
            if any(term in sentence.lower() for term in strategic_indicators[:10]):
                strategic_sentences.append(sentence.strip())

        if strategic_sentences:
            return ". ".join(strategic_sentences[:3])[:500] + "."

        return "Strategic analysis not available for this hand"

    def _extract_key_learnings(self, text: str) -> List[str]:
        """Extract key learning points"""
        learnings = []

        # Look for sentences with strategic advice
        sentences = text.split(".")

        for sentence in sentences:
            sentence = sentence.strip()

            # Skip comments/questions/promotional content
            skip_terms = [
                "comment",
                "question",
                "subscribe",
                "download",
                "free",
                "audiobook",
            ]
            if any(skip in sentence.lower() for skip in skip_terms):
                continue

            # Look for instructional content
            learning_indicators = [
                "you should",
                "you need to",
                "always",
                "never",
                "generally",
                "important to",
                "key is",
                "remember",
                "when facing",
                "if you have",
            ]

            if any(indicator in sentence.lower() for indicator in learning_indicators):
                if len(sentence) > 40 and len(sentence) < 300:
                    learnings.append(sentence)

        # If we found good learnings, return them
        if learnings:
            return learnings[:5]

        # Fallback: extract strategic principles
        principle_sentences = []
        for sentence in sentences:
            if any(
                term in sentence.lower()
                for term in ["equity", "position", "pot odds", "value", "bluff"]
            ):
                if 40 < len(sentence) < 250:
                    principle_sentences.append(sentence.strip())

        return principle_sentences[:5]

    def _extract_position_info(self, text: str) -> str:
        """Extract position information"""
        position_terms = [
            "UTG",
            "EP",
            "MP",
            "CO",
            "BTN",
            "SB",
            "BB",
            "button",
            "big blind",
            "small blind",
        ]

        for term in position_terms:
            pattern = rf"(?i){term}[^\n]*"
            match = re.search(pattern, text)
            if match:
                return match.group(0)[:100]

        return "Position not specified"

    def _extract_stack_info(self, text: str) -> str:
        """Extract stack size information"""
        stack_patterns = [
            r"(?i)(effective stacks?|stack sizes?)[:\s]*([^\n]+)",
            r"(?i)(\d+)\s*(BB|big blinds?)",
            r"(?i)\$(\d+,?\d*)\s*(effective|stack)",
        ]

        for pattern in stack_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)[:100]

        return "Stack sizes not specified"

    def _extract_pot_info(self, text: str) -> str:
        """Extract pot size information"""
        pot_patterns = [
            r"(?i)pot[:\s]*\$?(\d+,?\d*)",
            r"(?i)\$(\d+,?\d*)\s*(pot|in the pot)",
        ]

        for pattern in pot_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)[:50]

        return "Pot size not specified"

    def scrape_episode(self, url: str) -> Optional[PokerHand]:
        """Scrape a single WPH episode"""
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                hand = self.extract_hand_content(soup, url)

                if hand:
                    logger.info(
                        f"Successfully scraped episode {hand.episode_number}: {hand.title}"
                    )
                    return hand
                else:
                    logger.warning(f"No content extracted from {url}")
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")

        return None

    def scrape_episodes(
        self, start_episode: int = 1, end_episode: int = 100
    ) -> List[PokerHand]:
        """Scrape multiple WPH episodes"""
        hands = []
        urls = self.generate_wph_urls(start_episode, end_episode)

        for url in urls:
            hand = self.scrape_episode(url)
            if hand:
                hands.append(hand)

            # Be respectful with delays
            time.sleep(self.delay)

            # Progress logging every 10 episodes
            if len(hands) % 10 == 0 and len(hands) > 0:
                logger.info(f"Scraped {len(hands)} hands so far...")

        logger.info(f"Scraping complete. Total hands scraped: {len(hands)}")
        return hands

    def save_to_json(self, hands: List[PokerHand], filename: str):
        """Save scraped hands to JSON file"""
        import json
        from dataclasses import asdict

        data = [asdict(hand) for hand in hands]

        # Save to specified filename
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Also save to data directory with episode range in filename
        os.makedirs("data", exist_ok=True)

        # Get episode range from the hands
        if hands:
            episode_numbers = [h.episode_number for h in hands]
            min_episode = min(episode_numbers)
            max_episode = max(episode_numbers)
            # Use episode range in filename for clarity
            git_filename = f"data/wph_episodes_{min_episode}_{max_episode}.json"
        else:
            min_episode = 0
            max_episode = 0
            git_filename = f"data/wph_episodes_{len(hands)}_hands.json"

        with open(git_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Save a summary file for easy inspection
        summary = {
            "scrape_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_hands": len(hands),
            "episodes": [hand.episode_number for hand in hands],
            "titles": [
                f"Episode {hand.episode_number}: {hand.title}" for hand in hands
            ],
            "sample_hand": asdict(hands[0]) if hands else None,
        }

        # Use episode range in summary filename too
        if hands:
            summary_filename = (
                f"data/wph_scrape_summary_{min_episode}_{max_episode}.json"
            )
        else:
            summary_filename = f"data/wph_scrape_summary_{len(hands)}_hands.json"

        with open(summary_filename, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(hands)} hands to {filename}")
        logger.info(f"Git-friendly copy saved to {git_filename}")
        logger.info(f"Summary saved to {summary_filename}")

        return git_filename, summary_filename


if __name__ == "__main__":
    # Test the scraper
    scraper = WPHScraper()

    # Test with a single episode
    test_hand = scraper.scrape_episode(
        "https://jonathanlittlepoker.com/wph-573-mariano-poker-gets-owned/"
    )
    if test_hand:
        print(f"Episode: {test_hand.episode_number}")
        print(f"Title: {test_hand.title}")
        print(f"Situation: {test_hand.situation}")
        print(f"Actions: {test_hand.action_sequence[:2]}")  # First 2 actions
        print(f"Analysis: {test_hand.strategic_analysis[:200]}...")  # First 200 chars
