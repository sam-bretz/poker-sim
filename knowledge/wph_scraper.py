"""
Weekly Poker Hand (WPH) Scraper for Jonathan Little's poker strategy content.
Extracts hand analysis, strategic insights, and learning points from WPH articles.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional
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
    
    def __init__(self, base_url: str = "https://jonathanlittlepoker.com", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def generate_wph_urls(self, start_episode: int = 1, end_episode: int = 100) -> List[str]:
        """Generate URLs for WPH episodes"""
        urls = []
        
        # Some episodes use different URL patterns
        for episode in range(start_episode, end_episode + 1):
            # Try the main pattern first
            url = f"{self.base_url}/wph{episode}/"
            urls.append(url)
            
            # Some episodes might have different patterns
            if episode <= 10:
                alt_url = f"{self.base_url}/weekly-poker-hand-episode-{episode}/"
                urls.append(alt_url)
        
        return urls
    
    def extract_hand_content(self, soup: BeautifulSoup, url: str) -> Optional[PokerHand]:
        """Extract poker hand content from a WPH page"""
        try:
            # Extract episode number from URL
            episode_match = re.search(r'wph-?(\d+)', url)
            episode_number = int(episode_match.group(1)) if episode_match else 0
            
            # Get title
            title_elem = soup.find('h1', class_=['entry-title', 'post-title']) or soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else "Unknown Episode"
            
            # Extract main content
            content_div = soup.find('div', class_=['entry-content', 'post-content', 'content']) or soup.find('article')
            
            if not content_div:
                logger.warning(f"Could not find content for {url}")
                return None
            
            content_text = content_div.get_text()
            
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
                pot_size=pot_size
            )
        
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _extract_situation(self, text: str) -> str:
        """Extract the hand situation/setup"""
        situation_patterns = [
            r"(?i)(situation|setup|hand setup|the hand):\s*(.+?)(?=\n|action|flop|turn|river)",
            r"(?i)(blinds?|stakes?):\s*([^\n]+)",
            r"(?i)(effective stacks?|stack sizes?):\s*([^\n]+)"
        ]
        
        for pattern in situation_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(2).strip()[:200]  # Limit length
        
        # Fallback: extract first paragraph that mentions poker terms
        poker_terms = ['blinds', 'stack', 'position', 'button', 'UTG', 'raise', 'call', 'fold']
        sentences = text.split('.')[:10]  # Check first 10 sentences
        
        for sentence in sentences:
            if any(term in sentence.lower() for term in poker_terms):
                return sentence.strip()[:200]
        
        return "Situation not clearly identified"
    
    def _extract_action_sequence(self, text: str) -> List[str]:
        """Extract the betting action sequence"""
        actions = []
        
        # Look for preflop, flop, turn, river sections
        street_patterns = [
            r"(?i)preflop:?\s*(.+?)(?=flop|turn|river|\n\n)",
            r"(?i)flop[^\n]*:?\s*(.+?)(?=turn|river|\n\n)",
            r"(?i)turn[^\n]*:?\s*(.+?)(?=river|\n\n)",
            r"(?i)river[^\n]*:?\s*(.+?)(?=\n\n|$)"
        ]
        
        for pattern in street_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                street_action = match.group(1).strip()
                if street_action:
                    actions.append(street_action[:300])  # Limit length
        
        # Also look for action keywords
        action_keywords = ['raises', 'calls', 'folds', 'checks', 'bets', 'shoves', 'all-in']
        sentences = text.split('.')
        
        for sentence in sentences[:15]:  # Check first 15 sentences
            if any(keyword in sentence.lower() for keyword in action_keywords):
                actions.append(sentence.strip()[:200])
        
        return actions[:10]  # Limit to 10 actions
    
    def _extract_strategic_analysis(self, text: str) -> str:
        """Extract Jonathan Little's strategic analysis"""
        analysis_patterns = [
            r"(?i)(analysis|strategy|reasoning|thought process|should|optimal|mistake|correct play):?\s*(.+?)(?=\n\n|\.|key|conclusion)",
            r"(?i)(Jonathan|Little) (says|explains|recommends|suggests):?\s*(.+?)(?=\n\n)",
            r"(?i)(the correct play|best play|optimal strategy):?\s*(.+?)(?=\n\n)"
        ]
        
        for pattern in analysis_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                analysis = match.group(-1).strip()  # Get last group
                if len(analysis) > 50:  # Must be substantial
                    return analysis[:500]
        
        # Fallback: look for strategic keywords
        strategic_terms = ['equity', 'position', 'range', 'value', 'bluff', 'pot odds', 'implied odds']
        sentences = text.split('.')
        
        strategic_sentences = []
        for sentence in sentences:
            if any(term in sentence.lower() for term in strategic_terms):
                strategic_sentences.append(sentence.strip())
        
        return ' '.join(strategic_sentences[:3])[:500] if strategic_sentences else "Analysis not clearly identified"
    
    def _extract_key_learnings(self, text: str) -> List[str]:
        """Extract key learning points"""
        learnings = []
        
        learning_patterns = [
            r"(?i)(key takeaway|lesson|learning|remember|important):?\s*(.+?)(?=\n|$)",
            r"(?i)(always|never|when you|if you):?\s*(.+?)(?=\n|$)"
        ]
        
        for pattern in learning_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                learning = match.group(2).strip()
                if len(learning) > 20:  # Must be substantial
                    learnings.append(learning[:200])
        
        return learnings[:5]  # Limit to 5 key learnings
    
    def _extract_position_info(self, text: str) -> str:
        """Extract position information"""
        position_terms = ['UTG', 'EP', 'MP', 'CO', 'BTN', 'SB', 'BB', 'button', 'big blind', 'small blind']
        
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
            r"(?i)\$(\d+,?\d*)\s*(effective|stack)"
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
            r"(?i)\$(\d+,?\d*)\s*(pot|in the pot)"
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
                soup = BeautifulSoup(response.content, 'html.parser')
                hand = self.extract_hand_content(soup, url)
                
                if hand:
                    logger.info(f"Successfully scraped episode {hand.episode_number}: {hand.title}")
                    return hand
                else:
                    logger.warning(f"No content extracted from {url}")
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return None
    
    def scrape_episodes(self, start_episode: int = 1, end_episode: int = 100) -> List[PokerHand]:
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
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(hands)} hands to {filename}")

if __name__ == "__main__":
    # Test the scraper
    scraper = WPHScraper()
    
    # Test with a single episode
    test_hand = scraper.scrape_episode("https://jonathanlittlepoker.com/wph-573-mariano-poker-gets-owned/")
    if test_hand:
        print(f"Episode: {test_hand.episode_number}")
        print(f"Title: {test_hand.title}")
        print(f"Situation: {test_hand.situation}")
        print(f"Actions: {test_hand.action_sequence[:2]}")  # First 2 actions
        print(f"Analysis: {test_hand.strategic_analysis[:200]}...")  # First 200 chars