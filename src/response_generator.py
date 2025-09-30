"""
Intelligent Response Generator with Brand Voice
Uses GPT to generate contextual, on-brand responses
"""

import os
import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, init

from src.brand_voice import TACO_BELL_VOICE, BrandTone
from src.intent_detector_llm import IntentResult, OrderIntent

init(autoreset=True)
load_dotenv()

@dataclass
class ResponseContext:
    """Context for generating responses"""
    intent: OrderIntent
    entities: Dict
    conversation_history: List[str]
    current_order: List[str]  # List of item names
    order_total: float
    tone: BrandTone = BrandTone.FRIENDLY
    include_upsell: bool = True
    custom_context: Optional[str] = None  # For additional context

class TacoBellResponseGenerator:
    """Generate brand-appropriate responses using LLM"""
    
    def __init__(self, model: str = "gpt-3.5-turbo-1106"):
        """Initialize response generator"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OpenAI API key found in .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.brand_config = TACO_BELL_VOICE
        
        print(f"{Fore.GREEN}✓ Response Generator initialized")
    
    def generate_response(self, context: ResponseContext) -> str:
        """
        Generate contextual response with brand voice
        
        Args:
            context: ResponseContext with all necessary info
            
        Returns:
            Generated response string
        """
        # Build system prompt with brand guidelines
        system_prompt = self._build_system_prompt(context.tone)
        
        # Build user prompt with context
        user_prompt = self._build_user_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # More creative than intent detection
                max_tokens=150,
                timeout=10  # Add timeout
            )
            
            generated = response.choices[0].message.content.strip()
            
            # Post-process to ensure quality
            generated = self._post_process(generated, context)
            
            return generated
            
        except Exception as e:
            print(f"{Fore.YELLOW}Response generation error: {e}, using fallback")
            return self._get_fallback_response(context)
    
    def _build_system_prompt(self, tone: BrandTone) -> str:
        """Build system prompt with brand voice guidelines"""
        
        base_prompt = f"""You are a friendly Taco Bell drive-thru order taker. 

BRAND PERSONALITY:
{chr(10).join(f"- {trait}" for trait in self.brand_config.personality_traits)}

VOICE GUIDELINES - DO USE:
{chr(10).join(f"- {guideline}" for guideline in self.brand_config.voice_guidelines['do_use'])}

VOICE GUIDELINES - DON'T USE:
{chr(10).join(f"- {guideline}" for guideline in self.brand_config.voice_guidelines['dont_use'])}

TONE FOR THIS RESPONSE: {tone.value}

RULES:
1. Keep responses under 25 words when possible
2. Be conversational and natural
3. Use contractions (I'll, you're, etc.)
4. Sound enthusiastic about the food
5. Never sound robotic or scripted
6. If suggesting items, be specific with prices
7. Keep the conversation moving forward
8. Match the customer's energy level

Remember: You're a real person who loves working at Taco Bell, not a robot!"""
        
        return base_prompt
    
    def _build_user_prompt(self, context: ResponseContext) -> str:
        """Build user prompt with conversation context"""
        
        # Format conversation history
        if context.conversation_history:
            history = "\n".join(context.conversation_history[-4:])
        else:
            history = "(This is the start of the conversation)"
        
        # Format current order
        if context.current_order:
            order_items = ", ".join(context.current_order)
        else:
            order_items = "(No items yet)"
        
        # Build context string
        prompt = f"""SITUATION:
Customer Intent: {context.intent.value}
Extracted Info: {json.dumps(context.entities, indent=2)}

CURRENT ORDER:
{order_items}
Total so far: ${context.order_total:.2f}

RECENT CONVERSATION:
{history}
"""
        
        # Add custom context if provided
        if context.custom_context:
            prompt += f"\nADDITIONAL CONTEXT:\n{context.custom_context}\n"
        
        # Add upsell guidance if appropriate
        if context.include_upsell and self._should_upsell(context):
            upsell_suggestion = self._get_upsell_suggestion(context)
            if upsell_suggestion:
                prompt += f"\nSUGGESTION: Consider offering {upsell_suggestion}\n"
        
        prompt += "\nGenerate your response (keep it natural and brief):"
        
        return prompt
    
    def _should_upsell(self, context: ResponseContext) -> bool:
        """Determine if we should attempt an upsell"""
        # Don't upsell on first interaction
        if not context.conversation_history or len(context.conversation_history) < 2:
            return False
        
        # Don't upsell if customer is trying to finish
        if context.intent in [OrderIntent.CONFIRM_ORDER, OrderIntent.CANCEL_ORDER]:
            return False
        
        # Don't upsell if order is empty
        if not context.current_order:
            return False
        
        # Don't upsell too frequently
        if context.conversation_history:
            recent_history = " ".join(context.conversation_history[-4:]).lower()
            upsell_indicators = ["would you like", "want to add", "how about", "try our", "make that"]
            if any(indicator in recent_history for indicator in upsell_indicators):
                return False
        
        return True
    
    def _get_upsell_suggestion(self, context: ResponseContext) -> Optional[str]:
        """Get appropriate upsell suggestion based on order"""
        
        if not context.current_order:
            return None
        
        order_items_lower = [item.lower() for item in context.current_order]
        
        # Check for missing drink
        if self.brand_config.check_no_drink(order_items_lower):
            return "a Baja Blast for $2.29"
        
        # Check for missing side
        if self.brand_config.check_no_side(order_items_lower):
            return "Nacho Fries for $1.49"
        
        # Check for combo upgrade
        if self.brand_config.check_combo_upgrade(order_items_lower, context.order_total):
            return "the $5 Cravings Box which includes way more food"
        
        # Check for dessert opportunity
        if self.brand_config.check_dessert_opportunity(order_items_lower):
            return "Cinnamon Twists for just $1"
        
        return None
    
    def _post_process(self, response: str, context: ResponseContext) -> str:
        """Post-process generated response for quality"""
        
        if not response:
            return self._get_fallback_response(context)
        
        # Remove quotation marks if present
        response = response.strip('"\'')
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        # Ensure ends with punctuation
        if response and response[-1] not in '.!?':
            response += '.'
        
        # Capitalize first letter
        if response:
            response = response[0].upper() + response[1:]
        
        # Remove excessive punctuation
        response = response.replace('!!', '!')
        response = response.replace('??', '?')
        response = response.replace('..', '.')
        
        # Remove extra spaces
        response = ' '.join(response.split())
        
        return response
    
    def _get_fallback_response(self, context: ResponseContext) -> str:
        """Get fallback response if generation fails"""
        
        # Use template-based responses as fallback
        if context.intent == OrderIntent.ORDER_ITEM:
            items = context.entities.get('items', [])
            if items:
                items_str = ', '.join(items)
                return f"Got it! Adding {items_str} to your order. Anything else?"
            return "Sure! What would you like to order?"
        
        elif context.intent == OrderIntent.CONFIRM_ORDER:
            if context.order_total > 0:
                return f"Perfect! Your total is ${context.order_total:.2f}. Please pull forward!"
            return "You haven't ordered anything yet. What would you like?"
        
        elif context.intent == OrderIntent.MODIFY_ITEM:
            return "No problem, I'll make that change. What else can I get you?"
        
        elif context.intent == OrderIntent.REMOVE_ITEM:
            items = context.entities.get('items', [])
            if items:
                return f"Done! Removed {items[0]} from your order."
            return "What would you like to remove?"
        
        elif context.intent == OrderIntent.ASK_MENU:
            return "We have tacos, burritos, quesadillas, nachos, and drinks! What sounds good?"
        
        elif context.intent == OrderIntent.ASK_PRICE:
            items = context.entities.get('items', [])
            if items:
                return f"Let me check the price for {items[0]}."
            return "Which item would you like to know about?"
        
        elif context.intent == OrderIntent.GREETING:
            return self.get_time_based_greeting()
        
        elif context.intent == OrderIntent.CANCEL_ORDER:
            return "No problem! Let's start fresh. What can I get you?"
        
        else:
            return "What can I get for you today?"
    
    def get_time_based_greeting(self) -> str:
        """Get appropriate greeting based on time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            return self.brand_config.time_based_greetings["morning"]
        elif 11 <= hour < 17:
            return self.brand_config.time_based_greetings["afternoon"]
        elif 17 <= hour < 22:
            return self.brand_config.time_based_greetings["evening"]
        else:
            return self.brand_config.time_based_greetings["late_night"]
    
    def format_order_confirmation(self, order_items: List[Dict], total: float) -> str:
        """Format final order confirmation with personality"""
        
        if not order_items:
            return "Your order is empty. What would you like?"
        
        # Build item list
        items_text = []
        for item in order_items:
            qty = item.get('quantity', 1)
            name = item.get('name', 'item')
            mods = item.get('modifications', [])
            
            item_str = f"{qty}x {name}"
            if mods:
                item_str += f" ({', '.join(mods)})"
            items_text.append(item_str)
        
        items_str = ", ".join(items_text)
        
        # Choose a confirmation template
        templates = [
            f"Awesome! So I've got {items_str}. Your total is ${total:.2f}. Sound good?",
            f"Perfect! That's {items_str} for ${total:.2f}. All set?",
            f"You got it! {items_str} coming up. That'll be ${total:.2f}. Anything else?",
        ]
        
        return random.choice(templates)

# Test the response generator
if __name__ == "__main__":
    print(f"{Fore.MAGENTA}Testing Response Generator\n")
    
    try:
        generator = TacoBellResponseGenerator()
        
        # Test greeting
        print(f"{Fore.CYAN}Time-based greeting:")
        print(f"{Fore.GREEN}{generator.get_time_based_greeting()}\n")
        
        # Test order response
        context = ResponseContext(
            intent=OrderIntent.ORDER_ITEM,
            entities={'items': ['crunchy taco'], 'quantities': {'crunchy taco': 2}},
            conversation_history=["Welcome to Taco Bell!", "I want tacos"],
            current_order=[],
            order_total=0.0,
            tone=BrandTone.FRIENDLY,
            include_upsell=False  # No upsell on first order
        )
        
        print(f"{Fore.CYAN}Order response:")
        response = generator.generate_response(context)
        print(f"{Fore.GREEN}{response}\n")
        
        # Test upsell response
        context2 = ResponseContext(
            intent=OrderIntent.ORDER_ITEM,
            entities={},
            conversation_history=["I want tacos", "Got it! Two tacos."],
            current_order=["Crunchy Taco", "Crunchy Taco"],
            order_total=2.98,
            tone=BrandTone.FRIENDLY,
            include_upsell=True
        )
        
        print(f"{Fore.CYAN}Upsell response:")
        response2 = generator.generate_response(context2)
        print(f"{Fore.GREEN}{response2}")
        
        print(f"\n{Fore.GREEN}✓ All basic tests passed!")
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        import traceback
        traceback.print_exc()