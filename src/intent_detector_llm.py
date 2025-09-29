import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from colorama import Fore, init
import time

init(autoreset=True)
load_dotenv()

class OrderIntent(Enum):
    """Types of customer intents"""
    ORDER_ITEM = "order_item"
    MODIFY_ITEM = "modify_item"
    REMOVE_ITEM = "remove_item"
    CONFIRM_ORDER = "confirm_order"
    CANCEL_ORDER = "cancel_order"
    ASK_MENU = "ask_menu"
    ASK_PRICE = "ask_price"
    REPEAT_ORDER = "repeat_order"
    GREETING = "greeting"
    UNCLEAR = "unclear"

class IntentOutput(BaseModel):
    """Structured output from LLM"""
    intent: str = Field(description="Primary intent")
    confidence: float = Field(description="Confidence 0-1")
    items: List[str] = Field(default_factory=list, description="Menu items")
    quantities: Dict[str, int] = Field(default_factory=dict, description="Item quantities")
    modifications: List[Dict[str, str]] = Field(default_factory=list, description="Modifications")
    response_tone: str = Field(default="friendly", description="Suggested response tone")

@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: OrderIntent
    confidence: float
    entities: Dict[str, any]
    raw_text: str
    suggested_response: Optional[str] = None

class TacoBellIntentDetector:
    """GPT-based intent detection for Taco Bell drive-thru"""
    
    def __init__(self, model: str = "gpt-3.5-turbo-1106"):
        """
        Initialize GPT-based intent detector
        Using gpt-3.5-turbo-1106 for JSON mode support
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OpenAI API key found in .env file")

        self.client = OpenAI()
        self.model = model
        
        # Taco Bell menu for context
        self.menu_context = """
        TACO BELL MENU:
        
        TACOS:
        - Crunchy Taco ($1.49)
        - Soft Taco ($1.49) 
        - Crunchy Taco Supreme ($1.99)
        - Soft Taco Supreme ($1.99)
        - Doritos Locos Tacos ($2.19) - Nacho Cheese, Cool Ranch, Fiery
        
        BURRITOS:
        - Bean Burrito ($1.29)
        - Beef Burrito ($1.79)
        - Beefy 5-Layer Burrito ($2.49)
        - Crunchwrap Supreme ($4.49)
        - Cheesy Bean and Rice Burrito ($1.00)
        
        DRINKS:
        - Soft Drinks ($2.29/$2.59/$2.79) - S/M/L
        - Baja Blast Freeze ($2.69/$2.89/$3.09)
        - Regular Freeze ($2.69/$2.89/$3.09)
        
        SIDES:
        - Nachos & Cheese ($1.39)
        - Nacho Fries ($1.49)
        - Cinnamon Twists ($1.00)
        - Chips & Salsa ($1.49)
        
        COMBOS:
        - Combo meals include: Main item + drink + side ($6.99-$8.99)
        """
        
        print(f"{Fore.GREEN}✓ Taco Bell Intent Detector initialized")
        print(f"{Fore.CYAN}  Model: {model}")
        print(f"{Fore.CYAN}  API Key: ...{api_key[-4:]}")
    
    def detect_intent(self, text: str, conversation_history: List[str] = None) -> IntentResult:
        """
        Detect intent using GPT
        
        Args:
            text: Customer's speech
            conversation_history: Previous conversation context
        """
        start_time = time.time()
        
        # Build context from history
        history_context = ""
        if conversation_history:
            history_context = "\n".join([f"Previous: {h}" for h in conversation_history[-3:]])
        
        # Create the prompt
        messages = [
            {
                "role": "system",
                "content": f"""You are an AI assistant for a Taco Bell drive-thru. 
                Analyze customer speech and extract their intent.
                
                {self.menu_context}
                
                Respond with JSON containing:
                - intent: one of [order_item, modify_item, remove_item, confirm_order, cancel_order, ask_menu, ask_price, repeat_order, greeting, unclear]
                - confidence: 0.0 to 1.0
                - items: list of menu items mentioned
                - quantities: dict of item:quantity
                - modifications: list of modifications (e.g., no lettuce, extra cheese)
                - response_tone: friendly, clarifying, or confirming
                
                Be very careful with quantities - if they say "two tacos", quantities should be {{"taco": 2}}
                Extract specific menu items when possible.
                """
            },
            {
                "role": "user",
                "content": f"""
                {history_context}
                
                Customer just said: "{text}"
                
                Analyze intent and extract all relevant information.
                """
            }
        ]
        
        try:
            # Call GPT with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={ "type": "json_object" },
                temperature=0.1,  # Low for consistency
                max_tokens=300
            )
            
            # Parse response
            result_json = json.loads(response.choices[0].message.content)
            
            # Map to enum
            try:
                intent_enum = OrderIntent(result_json['intent'])
            except:
                intent_enum = OrderIntent.UNCLEAR
            
            # Create suggested response based on intent
            suggested_response = self._generate_response(intent_enum, result_json)
            
            # Build result
            entities = {
                'items': result_json.get('items', []),
                'quantities': result_json.get('quantities', {}),
                'modifications': result_json.get('modifications', []),
                'tone': result_json.get('response_tone', 'friendly')
            }
            
            result = IntentResult(
                intent=intent_enum,
                confidence=result_json.get('confidence', 0.5),
                entities=entities,
                raw_text=text,
                suggested_response=suggested_response
            )
            
            # Log the detection
            elapsed = time.time() - start_time
            self._log_detection(result, elapsed)
            
            return result
            
        except Exception as e:
            print(f"{Fore.RED}GPT Error: {e}")
            return IntentResult(
                intent=OrderIntent.UNCLEAR,
                confidence=0.0,
                entities={},
                raw_text=text,
                suggested_response="I'm sorry, could you please repeat that?"
            )
    
    def _generate_response(self, intent: OrderIntent, data: dict) -> str:
        """Generate appropriate response based on intent"""
        
        if intent == OrderIntent.ORDER_ITEM:
            items = data.get('items', [])
            quantities = data.get('quantities', {})
            
            if items:
                # Build order confirmation
                order_parts = []
                for item in items:
                    qty = quantities.get(item, 1)
                    if qty > 1:
                        order_parts.append(f"{qty} {item}s")
                    else:
                        order_parts.append(f"a {item}")
                
                return f"Alright, I've got {', '.join(order_parts)}. Would you like anything else?"
            else:
                return "Sure! What would you like to order today?"
        
        elif intent == OrderIntent.MODIFY_ITEM:
            mods = data.get('modifications', [])
            if mods and isinstance(mods, list) and len(mods) > 0:
                if isinstance(mods[0], dict):
                    mod_text = mods[0].get('description', 'that modification')
                else:
                    mod_text = str(mods[0])
                return f"Got it, {mod_text}. Anything else?"
            return "No problem, I'll make that change. Anything else?"
        
        elif intent == OrderIntent.CONFIRM_ORDER:
            return "Perfect! Your total will be displayed on the screen. Please pull forward to the window."
        
        elif intent == OrderIntent.ASK_MENU:
            return "We have tacos, burritos, crunchwraps, nachos, and drinks. What sounds good today?"
        
        elif intent == OrderIntent.ASK_PRICE:
            items = data.get('items', [])
            if items:
                return f"Let me check the price for {items[0]} for you."
            return "Which item would you like to know the price for?"
        
        elif intent == OrderIntent.GREETING:
            return "Welcome to Taco Bell! What can I get started for you today?"
        
        elif intent == OrderIntent.CANCEL_ORDER:
            return "No problem, let's start over. What would you like today?"
        
        elif intent == OrderIntent.REPEAT_ORDER:
            return "Let me repeat your order back to you..."
        
        else:
            return "I'm sorry, could you please repeat that?"
    
    def _log_detection(self, result: IntentResult, elapsed_time: float):
        """Log detection results"""
        color = Fore.GREEN if result.confidence > 0.7 else Fore.YELLOW
        
        print(f"\n{Fore.CYAN}═══ Intent Detection ═══")
        print(f"Input: '{result.raw_text}'")
        print(f"{color}Intent: {result.intent.value} ({result.confidence:.1%} confidence)")
        
        if result.entities.get('items'):
            print(f"{Fore.MAGENTA}Items: {result.entities['items']}")
        if result.entities.get('quantities'):
            print(f"{Fore.MAGENTA}Quantities: {result.entities['quantities']}")
        if result.entities.get('modifications'):
            print(f"{Fore.MAGENTA}Mods: {result.entities['modifications']}")
        
        print(f"{Fore.BLUE}Response: '{result.suggested_response}'")
        print(f"{Fore.WHITE}Time: {elapsed_time:.2f}s")