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
    aliases: List[str]
    tags: List[str]  # Added tags for better search

@dataclass
class SearchResult:
    """Menu search result"""
    item: MenuItem
    score: float
    reason: str

class TacoBellMenuRAG:
    """Enhanced RAG system for Taco Bell menu knowledge"""
    
    def __init__(self, embeddings_cache: str = "data/menu_embeddings_v2.pkl"):
        """Initialize the RAG system with menu data and embeddings"""
        print(f"{Fore.YELLOW}Initializing Enhanced Menu RAG System...")
        
        # Initialize sentence transformer for embeddings
        print(f"{Fore.CYAN}Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.embeddings_cache = embeddings_cache
        self.menu_items = self._load_menu_data()
        self.item_embeddings = self._load_or_create_embeddings()
        
        # Create lookup indices
        self._build_indices()
        
        # Pre-compute special queries
        self._build_special_indices()
        
        print(f"{Fore.GREEN}✓ Enhanced Menu RAG initialized with {len(self.menu_items)} items")
    
    def _load_menu_data(self) -> List[MenuItem]:
        """Load comprehensive Taco Bell menu data with better tags"""
        menu_items = [
            # TACOS
            MenuItem(
                name="Crunchy Taco",
                category="Tacos",
                price=1.49,
                description="A crunchy corn shell filled with seasoned beef, lettuce, and cheese",
                calories=170,
                customizations=["no lettuce", "extra cheese", "add sour cream", "no cheese"],
                aliases=["hard taco", "regular taco", "crispy taco", "crunchy"],
                tags=["crunchy", "beef", "cheap", "classic", "corn shell"]
            ),
            MenuItem(
                name="Soft Taco",
                category="Tacos",
                price=1.49,
                description="A warm flour tortilla filled with seasoned beef, lettuce, and cheese",
                calories=180,
                customizations=["no lettuce", "extra cheese", "add tomatoes", "no cheese"],
                aliases=["flour taco", "regular soft taco"],
                tags=["soft", "beef", "cheap", "classic", "flour tortilla"]
            ),
            MenuItem(
                name="Crunchy Taco Supreme",
                category="Tacos",
                price=1.99,
                description="Crunchy taco with seasoned beef, lettuce, cheese, tomatoes, and sour cream",
                calories=190,
                customizations=["no sour cream", "no tomatoes", "extra cheese"],
                aliases=["supreme taco", "deluxe taco", "loaded taco"],
                tags=["crunchy", "beef", "supreme", "sour cream", "tomatoes", "upgraded"]
            ),
            MenuItem(
                name="Doritos Locos Tacos",
                category="Tacos",
                price=2.19,
                description="Taco with a Nacho Cheese Doritos shell",
                calories=170,
                customizations=["cool ranch", "fiery", "nacho cheese"],
                aliases=["DLT", "dorito taco", "nacho taco", "doritos taco"],
                tags=["crunchy", "beef", "doritos", "nacho", "specialty", "cheese shell", "spicy option"]
            ),
            
            # BURRITOS
            MenuItem(
                name="Bean Burrito",
                category="Burritos",
                price=1.29,
                description="Warm flour tortilla filled with refried beans, cheese, and onions",
                calories=350,
                customizations=["no onions", "add rice", "extra cheese", "add jalapenos"],
                aliases=["beans burrito", "vegetarian burrito", "veggie burrito"],
                tags=["vegetarian", "beans", "cheapest", "no meat", "budget", "value"]
            ),
            MenuItem(
                name="Beef Burrito",
                category="Burritos",
                price=1.79,
                description="Seasoned beef, cheese, and onions wrapped in a flour tortilla",
                calories=430,
                customizations=["no onions", "add lettuce", "extra cheese"],
                aliases=["ground beef burrito", "meat burrito"],
                tags=["beef", "cheap", "simple", "classic"]
            ),
            MenuItem(
                name="Beefy 5-Layer Burrito",
                category="Burritos",
                price=2.49,
                description="Beef, cheese, beans, sour cream, and nacho cheese wrapped in two flour tortillas",
                calories=490,
                customizations=["no sour cream", "no beans", "extra beef"],
                aliases=["five layer", "5 layer", "5-layer"],
                tags=["beef", "hearty", "filling", "multiple layers", "sour cream"]
            ),
            MenuItem(
                name="Crunchwrap Supreme",
                category="Burritos",
                price=4.49,
                description="Hexagonal tortilla with beef, nacho cheese, lettuce, tomatoes, sour cream, and tostada",
                calories=530,
                customizations=["no sour cream", "no tomatoes", "add jalapenos"],
                aliases=["crunch wrap", "crunchy wrap", "hexagon"],
                tags=["crunchy", "beef", "premium", "signature", "tostada", "hexagonal"]
            ),
            
            # DRINKS
            MenuItem(
                name="Soft Drink",
                category="Drinks",
                price=2.29,
                description="Fountain drink - Pepsi, Mountain Dew, Sierra Mist, etc.",
                calories=150,
                customizations=["small", "medium", "large", "no ice", "light ice"],
                aliases=["soda", "coke", "pepsi", "fountain drink", "pop", "cola"],
                tags=["beverage", "fountain", "carbonated", "refreshing"]
            ),
            MenuItem(
                name="Baja Blast",
                category="Drinks",
                price=2.29,
                description="Exclusive Mountain Dew tropical lime flavor",
                calories=170,
                customizations=["small", "medium", "large", "no ice"],
                aliases=["baja", "blast", "blue drink", "mountain dew baja", "tropical"],
                tags=["beverage", "exclusive", "tropical", "lime", "signature drink"]
            ),
            MenuItem(
                name="Baja Blast Freeze",
                category="Drinks",
                price=2.69,
                description="Frozen Baja Blast slush drink",
                calories=190,
                customizations=["regular", "large"],
                aliases=["frozen baja", "baja slush", "blue freeze", "slushie", "frozen drink"],
                tags=["beverage", "frozen", "slush", "cold", "dessert drink"]
            ),
            
            # SIDES
            MenuItem(
                name="Nachos & Cheese",
                category="Sides",
                price=1.39,
                description="Tortilla chips with warm nacho cheese sauce",
                calories=220,
                customizations=["extra cheese", "add jalapenos", "add beans"],
                aliases=["chips and cheese", "nachos", "cheese nachos", "chips"],
                tags=["crunchy", "cheese", "cheap", "snack", "shareable", "vegetarian"]
            ),
            MenuItem(
                name="Nacho Fries",
                category="Sides",
                price=1.49,
                description="Seasoned fries with nacho cheese dipping sauce",
                calories=320,
                customizations=["extra seasoning", "no seasoning", "extra cheese sauce"],
                aliases=["fries", "french fries", "seasoned fries"],
                tags=["fries", "cheese", "seasoned", "limited time", "popular"]
            ),
            MenuItem(
                name="Cinnamon Twists",
                category="Sides",
                price=1.00,
                description="Crispy puffed corn twists dusted with cinnamon sugar",
                calories=170,
                customizations=["extra cinnamon"],
                aliases=["dessert", "sweet", "twists", "cinnamon", "churros"],
                tags=["sweet", "dessert", "cheapest", "cinnamon", "crispy", "vegetarian"]
            ),
            
            # COMBOS
            MenuItem(
                name="Cravings Box",
                category="Combos",
                price=5.00,
                description="Chalupa Supreme, 5-Layer Burrito, Taco, Cinnamon Twists, and drink",
                calories=1290,
                customizations=["swap items", "upgrade drink"],
                aliases=["box", "combo box", "meal deal", "5 dollar box", "$5 box"],
                tags=["combo", "value", "deal", "complete meal", "variety", "best value"]
            ),
            MenuItem(
                name="Combo Meal",
                category="Combos",
                price=7.99,
                description="Any main item with a drink and side",
                calories=800,
                customizations=["choose main", "choose side", "choose drink"],
                aliases=["meal", "combo", "number 1", "number 2"],
                tags=["combo", "customizable", "meal", "drink included"]
            ),
        ]
        
        return menu_items
    
    def _load_or_create_embeddings(self) -> np.ndarray:
        """Load cached embeddings or create new ones"""
        cache_path = Path(self.embeddings_cache)
        
        # Try to load cached embeddings
        if cache_path.exists():
            try:
                print(f"{Fore.CYAN}Loading cached embeddings...")
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    if len(cached_data['embeddings']) == len(self.menu_items):
                        return cached_data['embeddings']
            except:
                print(f"{Fore.YELLOW}Cache corrupted, regenerating...")
        
        # Create embeddings for each menu item
        print(f"{Fore.CYAN}Creating embeddings for menu items...")
        texts_to_encode = []
        
        for item in self.menu_items:
            # Enhanced text representation including tags
            combined_text = (
                f"{item.name} {item.category} {item.description} "
                f"{' '.join(item.aliases)} {' '.join(item.tags)} "
                f"price ${item.price:.2f}"
            )
            texts_to_encode.append(combined_text)
        
        # Encode all at once
        embeddings = self.encoder.encode(texts_to_encode)
        
        # Cache the embeddings
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump({'embeddings': embeddings, 'version': 2}, f)
        
        return embeddings
    
    def _build_indices(self):
        """Build search indices for fast lookup"""
        self.name_to_item = {}
        self.category_to_items = {}
        self.alias_to_item = {}
        self.tag_to_items = {}
        
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
            
            # Tag index
            for tag in item.tags:
                if tag not in self.tag_to_items:
                    self.tag_to_items[tag] = []
                self.tag_to_items[tag].append(item)
    
    def _build_special_indices(self):
        """Build indices for special queries"""
        # Sort by price for cheapest/most expensive queries
        self.items_by_price = sorted(self.menu_items, key=lambda x: x.price)
        
        # Group by dietary restrictions
        self.vegetarian_items = [item for item in self.menu_items 
                                 if 'vegetarian' in item.tags or 'no meat' in item.tags]
        
        # Group by texture/style
        self.crunchy_items = [item for item in self.menu_items if 'crunchy' in item.tags]
        self.spicy_items = [item for item in self.menu_items if 'spicy' in item.tags or 'fiery' in ' '.join(item.customizations)]
    
    def search_menu(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """
        Enhanced search with special query handling
        """
        query_lower = query.lower()
        
        # Handle special queries first
        if 'cheapest' in query_lower or 'lowest price' in query_lower:
            cheapest = self.items_by_price[:3]
            return [SearchResult(item, 1.0 - i*0.1, "Price ranking") 
                   for i, item in enumerate(cheapest)]
        
        if 'most expensive' in query_lower or 'premium' in query_lower:
            expensive = self.items_by_price[-3:][::-1]
            return [SearchResult(item, 1.0 - i*0.1, "Price ranking") 
                   for i, item in enumerate(expensive)]
        
        if 'vegetarian' in query_lower or 'veggie' in query_lower or 'no meat' in query_lower:
            return [SearchResult(item, 0.9, "Vegetarian option") 
                   for item in self.vegetarian_items[:top_k]]
        
        if 'spicy' in query_lower or 'hot' in query_lower:
            # Return Doritos Locos with Fiery option as top result
            dlt = self.name_to_item.get('doritos locos tacos')
            if dlt:
                return [SearchResult(dlt, 0.9, "Has spicy option (Fiery)")]
            return []
        
        if 'crunchy' in query_lower or 'crispy' in query_lower:
            return [SearchResult(item, 0.9, "Crunchy item") 
                   for item in self.crunchy_items[:top_k]]
        
        # Check exact matches
        if query_lower in self.name_to_item:
            item = self.name_to_item[query_lower]
            return [SearchResult(item, 1.0, "Exact name match")]
        
        if query_lower in self.alias_to_item:
            item = self.alias_to_item[query_lower]
            return [SearchResult(item, 0.95, "Alias match")]
        
        # Check tag matches
        matching_items = []
        for word in query_lower.split():
            if word in self.tag_to_items:
                for item in self.tag_to_items[word]:
                    if item not in matching_items:
                        matching_items.append(item)
        
        if matching_items:
            return [SearchResult(item, 0.85, "Tag match") 
                   for item in matching_items[:top_k]]
        
        # Fall back to semantic search
        query_embedding = self.encoder.encode([query])
        similarities = cosine_similarity(query_embedding, self.item_embeddings)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:
                item = self.menu_items[idx]
                score = float(similarities[idx])
                reason = self._get_match_reason(query, item, score)
                results.append(SearchResult(item, score, reason))
        
        return results
    
    def _get_match_reason(self, query: str, item: MenuItem, score: float) -> str:
        """Determine why an item was matched"""
        query_words = set(query.lower().split())
        
        # Check various matching criteria
        if any(word in item.name.lower() for word in query_words):
            return "Name similarity"
        elif any(word in item.tags for word in query_words):
            return "Tag match"
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
        total_price = 0.0
        
        # Analyze current order
        for item_name in current_items:
            item = self.get_item_by_name(item_name)
            if item:
                total_price += item.price
                if item.category == "Drinks":
                    has_drink = True
                elif item.category == "Sides":
                    has_side = True
                elif item.category in ["Tacos", "Burritos"]:
                    has_main = True
        
        # Smart recommendations
        if has_main and not has_drink:
            recommendations.append(self.get_item_by_name("Baja Blast"))
        
        if has_main and not has_side:
            recommendations.append(self.get_item_by_name("Nacho Fries"))
        
        if not has_main:
            recommendations.append(self.get_item_by_name("Crunchy Taco"))
        
        # If order is under $5, suggest the Cravings Box
        if total_price < 5.0 and has_main:
            cravings_box = self.get_item_by_name("Cravings Box")
            if cravings_box:
                recommendations.insert(0, cravings_box)
        
        return [r for r in recommendations if r is not None]
    
    def calculate_order_total(self, items: List[Tuple[str, int]]) -> float:
        """Calculate total price for order"""
        total = 0.0
        for item_name, quantity in items:
            results = self.search_menu(item_name, top_k=1)
            if results:
                total += results[0].item.price * quantity
        return total

# Test the enhanced RAG system
if __name__ == "__main__":
    print(f"{Fore.MAGENTA}Testing Enhanced Menu RAG System\n")
    
    rag = TacoBellMenuRAG()
    
    # Test searches
    test_queries = [
        "cheapest item",
        "vegetarian options", 
        "spicy food",
        "something with beef",
        "crunchy items",
        "drinks",
        "combo meal",
        "most expensive"
    ]
    
    for query in test_queries:
        print(f"\n{Fore.CYAN}Query: '{query}'")
        results = rag.search_menu(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                color = Fore.GREEN if result.score > 0.7 else Fore.YELLOW
                print(f"{color}{i}. {result.item.name} (${result.item.price:.2f})")
                print(f"   Score: {result.score:.2f} - {result.reason}")
                print(f"   {Fore.WHITE}{result.item.description}")
        else:
            print(f"{Fore.RED}No results found")