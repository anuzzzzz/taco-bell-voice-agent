import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from colorama import Fore, init
import pickle
from pathlib import Path

init(autoreset=True)

@dataclass
class MenuItem:
    """Represents a menu item"""
    name: str
    category: str
    price: float
    description: str
    calories: int
    customizations: List[str]
    aliases: List[str]  # Alternative names customers might use

@dataclass
class SearchResult:
    """Menu search result"""
    item: MenuItem
    score: float
    reason: str  # Why this was matched

class TacoBellMenuRAG:
    """RAG system for Taco Bell menu knowledge"""
    
    def __init__(self, embeddings_cache: str = "data/menu_embeddings.pkl"):
        """Initialize the RAG system with menu data and embeddings"""
        print(f"{Fore.YELLOW}Initializing Menu RAG System...")
        
        # Initialize sentence transformer for embeddings
        print(f"{Fore.CYAN}Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast, good quality
        
        self.embeddings_cache = embeddings_cache
        self.menu_items = self._load_menu_data()
        self.item_embeddings = self._load_or_create_embeddings()
        
        # Create lookup indices
        self._build_indices()
        
        print(f"{Fore.GREEN}✓ Menu RAG initialized with {len(self.menu_items)} items")
    
    def _load_menu_data(self) -> List[MenuItem]:
        """Load comprehensive Taco Bell menu data"""
        menu_items = [
            # TACOS
            MenuItem(
                name="Crunchy Taco",
                category="Tacos",
                price=1.49,
                description="A crunchy corn shell filled with seasoned beef, lettuce, and cheese",
                calories=170,
                customizations=["no lettuce", "extra cheese", "add sour cream", "no cheese"],
                aliases=["hard taco", "regular taco", "crispy taco"]
            ),
            MenuItem(
                name="Soft Taco",
                category="Tacos",
                price=1.49,
                description="A warm flour tortilla filled with seasoned beef, lettuce, and cheese",
                calories=180,
                customizations=["no lettuce", "extra cheese", "add tomatoes", "no cheese"],
                aliases=["flour taco", "regular soft taco"]
            ),
            MenuItem(
                name="Crunchy Taco Supreme",
                category="Tacos",
                price=1.99,
                description="Crunchy taco with seasoned beef, lettuce, cheese, tomatoes, and sour cream",
                calories=190,
                customizations=["no sour cream", "no tomatoes", "extra cheese"],
                aliases=["supreme taco", "deluxe taco"]
            ),
            MenuItem(
                name="Doritos Locos Tacos",
                category="Tacos",
                price=2.19,
                description="Taco with a Nacho Cheese Doritos shell",
                calories=170,
                customizations=["cool ranch", "fiery", "nacho cheese"],
                aliases=["DLT", "dorito taco", "nacho taco"]
            ),
            
            # BURRITOS
            MenuItem(
                name="Bean Burrito",
                category="Burritos",
                price=1.29,
                description="Warm flour tortilla filled with refried beans, cheese, and onions",
                calories=350,
                customizations=["no onions", "add rice", "extra cheese", "add jalapenos"],
                aliases=["beans burrito", "vegetarian burrito"]
            ),
            MenuItem(
                name="Beef Burrito",
                category="Burritos",
                price=1.79,
                description="Seasoned beef, cheese, and onions wrapped in a flour tortilla",
                calories=430,
                customizations=["no onions", "add lettuce", "extra cheese"],
                aliases=["ground beef burrito", "meat burrito"]
            ),
            MenuItem(
                name="Beefy 5-Layer Burrito",
                category="Burritos",
                price=2.49,
                description="Beef, cheese, beans, sour cream, and nacho cheese wrapped in two flour tortillas",
                calories=490,
                customizations=["no sour cream", "no beans", "extra beef"],
                aliases=["five layer", "5 layer"]
            ),
            MenuItem(
                name="Crunchwrap Supreme",
                category="Burritos",
                price=4.49,
                description="Hexagonal tortilla filled with beef, nacho cheese, lettuce, tomatoes, sour cream, and a tostada shell",
                calories=530,
                customizations=["no sour cream", "no tomatoes", "add jalapenos"],
                aliases=["crunch wrap", "crunchy wrap"]
            ),
            
            # DRINKS
            MenuItem(
                name="Soft Drink",
                category="Drinks",
                price=2.29,
                description="Fountain drink - Pepsi, Mountain Dew, Sierra Mist, etc.",
                calories=150,
                customizations=["small", "medium", "large", "no ice", "light ice"],
                aliases=["soda", "coke", "pepsi", "fountain drink", "pop"]
            ),
            MenuItem(
                name="Baja Blast",
                category="Drinks",
                price=2.29,
                description="Exclusive Mountain Dew tropical flavor",
                calories=170,
                customizations=["small", "medium", "large", "no ice"],
                aliases=["baja", "blast", "blue drink", "mountain dew baja"]
            ),
            MenuItem(
                name="Baja Blast Freeze",
                category="Drinks",
                price=2.69,
                description="Frozen Baja Blast slush drink",
                calories=190,
                customizations=["regular", "large"],
                aliases=["frozen baja", "baja slush", "blue freeze", "slushie"]
            ),
            
            # SIDES
            MenuItem(
                name="Nachos & Cheese",
                category="Sides",
                price=1.39,
                description="Tortilla chips with warm nacho cheese sauce",
                calories=220,
                customizations=["extra cheese", "add jalapenos", "add beans"],
                aliases=["chips and cheese", "nachos", "cheese nachos"]
            ),
            MenuItem(
                name="Nacho Fries",
                category="Sides",
                price=1.49,
                description="Seasoned fries with nacho cheese dipping sauce",
                calories=320,
                customizations=["extra seasoning", "no seasoning", "extra cheese sauce"],
                aliases=["fries", "french fries", "seasoned fries"]
            ),
            MenuItem(
                name="Cinnamon Twists",
                category="Sides",
                price=1.00,
                description="Crispy puffed corn twists dusted with cinnamon sugar",
                calories=170,
                customizations=["extra cinnamon"],
                aliases=["dessert", "sweet", "twists", "cinnamon"]
            ),
            
            # COMBOS
            MenuItem(
                name="Cravings Box",
                category="Combos",
                price=5.00,
                description="Includes a Chalupa Supreme, Beefy 5-Layer Burrito, Crunchy Taco, Cinnamon Twists, and a drink",
                calories=1290,
                customizations=["swap items", "upgrade drink"],
                aliases=["box", "combo box", "meal deal", "5 dollar box"]
            ),
            MenuItem(
                name="Combo Meal",
                category="Combos",
                price=7.99,
                description="Any main item with a drink and side",
                calories=800,
                customizations=["choose main", "choose side", "choose drink"],
                aliases=["meal", "combo", "number 1", "number 2"]
            ),
        ]
        
        return menu_items
    
    def _load_or_create_embeddings(self) -> np.ndarray:
        """Load cached embeddings or create new ones"""
        cache_path = Path(self.embeddings_cache)
        
        # Try to load cached embeddings
        if cache_path.exists():
            print(f"{Fore.CYAN}Loading cached embeddings...")
            with open(cache_path, 'rb') as f:
                embeddings = pickle.load(f)
                if len(embeddings) == len(self.menu_items):
                    return embeddings
                else:
                    print(f"{Fore.YELLOW}Cache size mismatch, regenerating...")
        
        # Create embeddings for each menu item
        print(f"{Fore.CYAN}Creating embeddings for menu items...")
        texts_to_encode = []
        
        for item in self.menu_items:
            # Combine all relevant text for better embedding
            combined_text = f"{item.name} {item.category} {item.description} {' '.join(item.aliases)}"
            texts_to_encode.append(combined_text)
        
        # Encode all at once (more efficient)
        embeddings = self.encoder.encode(texts_to_encode)
        
        # Cache the embeddings
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump(embeddings, f)
        
        return embeddings
    
    def _build_indices(self):
        """Build search indices for fast lookup"""
        self.name_to_item = {}
        self.category_to_items = {}
        self.alias_to_item = {}
        
        for item in self.menu_items:
            # Name index
            self.name_to_item[item.name.lower()] = item
            
            # Category index
            if item.category not in self.category_to_items:
                self.category_to_items[item.category] = []
            self.category_to_items[item.category].append(item)
            
            # Alias index
            for alias in item.aliases:
                self.alias_to_item[alias.lower()] = item
    
    def search_menu(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """
        Search menu using semantic similarity
        
        Args:
            query: Customer's query
            top_k: Number of results to return
        """
        # First try exact match
        query_lower = query.lower()
        
        # Check direct name match
        if query_lower in self.name_to_item:
            item = self.name_to_item[query_lower]
            return [SearchResult(item, 1.0, "Exact name match")]
        
        # Check alias match
        if query_lower in self.alias_to_item:
            item = self.alias_to_item[query_lower]
            return [SearchResult(item, 0.95, "Alias match")]
        
        # Semantic search using embeddings
        query_embedding = self.encoder.encode([query])
        similarities = cosine_similarity(query_embedding, self.item_embeddings)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Threshold for relevance
                item = self.menu_items[idx]
                score = float(similarities[idx])
                reason = self._get_match_reason(query, item, score)
                results.append(SearchResult(item, score, reason))
        
        return results
    
    def _get_match_reason(self, query: str, item: MenuItem, score: float) -> str:
        """Determine why an item was matched"""
        query_words = set(query.lower().split())
        
        if any(word in item.name.lower() for word in query_words):
            return "Name similarity"
        elif any(word in item.description.lower() for word in query_words):
            return "Description match"
        elif any(word in ' '.join(item.aliases).lower() for word in query_words):
            return "Alias match"
        elif score > 0.6:
            return "High semantic similarity"
        else:
            return "Partial match"
    
    def get_item_by_name(self, name: str) -> Optional[MenuItem]:
        """Get menu item by exact name"""
        return self.name_to_item.get(name.lower())
    
    def get_category_items(self, category: str) -> List[MenuItem]:
        """Get all items in a category"""
        return self.category_to_items.get(category, [])
    
    def get_recommendations(self, current_items: List[str]) -> List[MenuItem]:
        """Get recommendations based on current order"""
        recommendations = []
        has_drink = False
        has_side = False
        has_main = False
        
        # Analyze current order
        for item_name in current_items:
            item = self.get_item_by_name(item_name)
            if item:
                if item.category == "Drinks":
                    has_drink = True
                elif item.category == "Sides":
                    has_side = True
                elif item.category in ["Tacos", "Burritos"]:
                    has_main = True
        
        # Recommend missing components
        if has_main and not has_drink:
            recommendations.append(self.get_item_by_name("Baja Blast"))
        
        if has_main and not has_side:
            recommendations.append(self.get_item_by_name("Nacho Fries"))
        
        if not has_main:
            recommendations.append(self.get_item_by_name("Crunchy Taco"))
        
        # Filter out None values
        return [r for r in recommendations if r is not None]
    
    def calculate_order_total(self, items: List[Tuple[str, int]]) -> float:
        """Calculate total price for order"""
        total = 0.0
        for item_name, quantity in items:
            item = self.search_menu(item_name, top_k=1)
            if item:
                total += item[0].item.price * quantity
        return total

# Test the RAG system
if __name__ == "__main__":
    print(f"{Fore.MAGENTA}Testing Menu RAG System\n")
    
    rag = TacoBellMenuRAG()
    
    # Test searches
    test_queries = [
        "crunchy taco",
        "something with beef",
        "vegetarian options",
        "cheapest item",
        "drinks",
        "spicy food",
        "combo meal",
        "dorito shell"
    ]
    
    for query in test_queries:
        print(f"\n{Fore.CYAN}Query: '{query}'")
        results = rag.search_menu(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"{Fore.GREEN}{i}. {result.item.name} (${result.item.price:.2f})")
            print(f"   Score: {result.score:.2f} - {result.reason}")
            print(f"   {Fore.WHITE}{result.item.description}")
    
    # Test recommendations
    print(f"\n{Fore.YELLOW}Testing recommendations for order: ['Crunchy Taco']")
    recs = rag.get_recommendations(["Crunchy Taco"])
    for rec in recs:
        print(f"  Recommend: {rec.name} - {rec.description}")