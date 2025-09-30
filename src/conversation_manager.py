from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import json
from colorama import Fore, init

from src.intent_detector_llm import TacoBellIntentDetector, OrderIntent, IntentResult
from src.menu_rag import TacoBellMenuRAG, MenuItem

init(autoreset=True)

class ConversationState(Enum):
    """States of the drive-thru conversation"""
    GREETING = "greeting"
    TAKING_ORDER = "taking_order"
    CONFIRMING_ITEM = "confirming_item"
    MODIFYING_ORDER = "modifying_order"
    ORDER_COMPLETE = "order_complete"
    PAYMENT = "payment"
    GOODBYE = "goodbye"

@dataclass
class OrderItem:
    """Represents an item in the order"""
    name: str
    quantity: int
    price: float
    modifications: List[str] = field(default_factory=list)
    confirmed: bool = False
    
    def get_total_price(self) -> float:
        return self.price * self.quantity
    
    def to_string(self) -> str:
        """Convert to readable string"""
        mods = f" ({', '.join(self.modifications)})" if self.modifications else ""
        return f"{self.quantity}x {self.name}{mods}"

@dataclass
class Order:
    """Represents the complete order"""
    items: List[OrderItem] = field(default_factory=list)
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    special_requests: List[str] = field(default_factory=list)
    
    def add_item(self, item: OrderItem):
        """Add or update item in order"""
        # Check if item already exists
        for existing in self.items:
            if existing.name == item.name and existing.modifications == item.modifications:
                existing.quantity += item.quantity
                return
        self.items.append(item)
    
    def remove_item(self, item_name: str) -> bool:
        """Remove item from order"""
        for i, item in enumerate(self.items):
            if item.name.lower() == item_name.lower():
                self.items.pop(i)
                return True
        return False
    
    def get_total(self) -> float:
        """Calculate total price"""
        return sum(item.get_total_price() for item in self.items)
    
    def get_summary(self) -> str:
        """Get order summary"""
        if not self.items:
            return "No items in order"
        
        summary = "Your order:\n"
        for item in self.items:
            summary += f"  • {item.to_string()} - ${item.get_total_price():.2f}\n"
        summary += f"Total: ${self.get_total():.2f}"
        return summary

class ConversationManager:
    """Manages the drive-thru conversation flow"""
    
    def __init__(self):
        """Initialize conversation manager"""
        self.state = ConversationState.GREETING
        self.order = Order()
        self.conversation_history = []
        self.context_window = 5  # Keep last 5 exchanges
        
        # Initialize components
        self.intent_detector = TacoBellIntentDetector()
        self.menu_rag = TacoBellMenuRAG()
        
        # State transition rules
        self.transitions = {
            ConversationState.GREETING: [ConversationState.TAKING_ORDER],
            ConversationState.TAKING_ORDER: [
                ConversationState.CONFIRMING_ITEM,
                ConversationState.MODIFYING_ORDER,
                ConversationState.ORDER_COMPLETE
            ],
            ConversationState.CONFIRMING_ITEM: [
                ConversationState.TAKING_ORDER,
                ConversationState.MODIFYING_ORDER
            ],
            ConversationState.MODIFYING_ORDER: [
                ConversationState.TAKING_ORDER,
                ConversationState.ORDER_COMPLETE
            ],
            ConversationState.ORDER_COMPLETE: [
                ConversationState.PAYMENT,
                ConversationState.MODIFYING_ORDER
            ],
            ConversationState.PAYMENT: [ConversationState.GOODBYE],
            ConversationState.GOODBYE: []
        }
        
        print(f"{Fore.GREEN}✓ Conversation Manager initialized")
    
    def process_input(self, user_input: str) -> Tuple[str, ConversationState]:
        """
        Process user input and return response with new state
        
        Args:
            user_input: Customer's speech/text
            
        Returns:
            Tuple of (response, new_state)
        """
        # Add to history
        self.conversation_history.append(f"Customer: {user_input}")
        
        # Get intent
        intent_result = self.intent_detector.detect_intent(
            user_input, 
            self.conversation_history[-self.context_window:]
        )
        
        # Process based on current state and intent
        response = self._handle_state_intent(intent_result)
        
        # Add response to history
        self.conversation_history.append(f"Agent: {response}")
        
        # Log state
        self._log_state()
        
        return response, self.state
    
    def _handle_state_intent(self, intent_result: IntentResult) -> str:
        """Handle intent based on current state"""
        
        if self.state == ConversationState.GREETING:
            return self._handle_greeting(intent_result)
        
        elif self.state == ConversationState.TAKING_ORDER:
            return self._handle_taking_order(intent_result)
        
        elif self.state == ConversationState.CONFIRMING_ITEM:
            return self._handle_confirming(intent_result)
        
        elif self.state == ConversationState.MODIFYING_ORDER:
            return self._handle_modification(intent_result)
        
        elif self.state == ConversationState.ORDER_COMPLETE:
            return self._handle_order_complete(intent_result)
        
        elif self.state == ConversationState.PAYMENT:
            return self._handle_payment(intent_result)
        
        else:
            return "Thank you for choosing Taco Bell!"
    
    def _handle_greeting(self, intent: IntentResult) -> str:
        """Handle greeting state"""
        self.state = ConversationState.TAKING_ORDER
        
        if intent.intent == OrderIntent.ORDER_ITEM:
            # Customer jumped straight to ordering
            return self._process_order_item(intent)
        else:
            return "Welcome to Taco Bell! What can I get started for you today?"
    
    def _handle_taking_order(self, intent: IntentResult) -> str:
        """Handle order-taking state"""
        
        if intent.intent == OrderIntent.ORDER_ITEM:
            return self._process_order_item(intent)
        
        elif intent.intent == OrderIntent.ASK_MENU:
            items = self.menu_rag.get_category_items("Tacos")[:3]
            menu_str = ", ".join([f"{item.name} (${item.price:.2f})" for item in items])
            return f"We have {menu_str}, and much more! What sounds good?"
        
        elif intent.intent == OrderIntent.ASK_PRICE:
            return self._handle_price_inquiry(intent)
        
        elif intent.intent == OrderIntent.CONFIRM_ORDER:
            if self.order.items:
                self.state = ConversationState.ORDER_COMPLETE
                return f"{self.order.get_summary()}\n\nIs that correct?"
            else:
                return "You haven't ordered anything yet. What would you like?"
        
        elif intent.intent == OrderIntent.REMOVE_ITEM:
            return self._handle_remove_item(intent)
        
        elif intent.intent == OrderIntent.MODIFY_ITEM:
            self.state = ConversationState.MODIFYING_ORDER
            return self._handle_modification(intent)
        
        else:
            return "What would you like to order?"
    
    def _process_order_item(self, intent: IntentResult) -> str:
        """Process an order item request"""
        items_added = []
        items_not_found = []
        
        # Extract items and quantities
        mentioned_items = intent.entities.get('items', [])
        quantities = intent.entities.get('quantities', {})
        
        for item_name in mentioned_items:
            # Search for item in menu
            search_results = self.menu_rag.search_menu(item_name, top_k=1)
            
            if search_results and search_results[0].score > 0.5:
                menu_item = search_results[0].item
                
                # Get quantity
                qty = quantities.get(item_name, 1)
                
                # Create order item
                order_item = OrderItem(
                    name=menu_item.name,
                    quantity=qty,
                    price=menu_item.price
                )
                
                self.order.add_item(order_item)
                items_added.append(f"{qty} {menu_item.name}")
            else:
                items_not_found.append(item_name)
        
        # Build response
        if items_added:
            response = f"I've added {', '.join(items_added)} to your order."
            
            # Get recommendations
            current_item_names = [item.name for item in self.order.items]
            recommendations = self.menu_rag.get_recommendations(current_item_names)
            
            if recommendations:
                rec = recommendations[0]
                response += f" Would you like to add a {rec.name} for ${rec.price:.2f}?"
            else:
                response += " Anything else?"
        else:
            response = "I couldn't find those items on our menu. "
            
            # Suggest similar items
            if mentioned_items:
                search_results = self.menu_rag.search_menu(mentioned_items[0], top_k=3)
                if search_results:
                    suggestions = [r.item.name for r in search_results]
                    response += f"Did you mean {', '.join(suggestions)}?"
        
        return response
    
    def _handle_modification(self, intent: IntentResult) -> str:
        """Handle order modifications"""
        modifications = intent.entities.get('modifications', [])
        
        if not self.order.items:
            return "You haven't ordered anything yet. What would you like?"
        
        # Apply modifications to last item
        last_item = self.order.items[-1]
        
        for mod in modifications:
            if isinstance(mod, dict):
                mod_text = f"{mod.get('type', '')} {mod.get('item', '')}"
            else:
                mod_text = str(mod)
            last_item.modifications.append(mod_text)
        
        self.state = ConversationState.TAKING_ORDER
        return f"Got it, {', '.join(last_item.modifications)} for your {last_item.name}. Anything else?"
    
    def _handle_remove_item(self, intent: IntentResult) -> str:
        """Handle item removal"""
        items = intent.entities.get('items', [])
        
        if not items:
            return "What would you like to remove?"
        
        removed = []
        for item_name in items:
            if self.order.remove_item(item_name):
                removed.append(item_name)
        
        if removed:
            return f"I've removed {', '.join(removed)} from your order. Anything else?"
        else:
            return "I couldn't find that item in your order."
    
    def _handle_price_inquiry(self, intent: IntentResult) -> str:
        """Handle price inquiries"""
        items = intent.entities.get('items', [])
        
        if items:
            search_results = self.menu_rag.search_menu(items[0], top_k=1)
            if search_results:
                item = search_results[0].item
                return f"Our {item.name} is ${item.price:.2f}. Would you like to add it?"
        
        return "Which item would you like to know the price for?"
    
    def _handle_confirming(self, intent: IntentResult) -> str:
        """Handle order confirmation"""
        if intent.intent == OrderIntent.CONFIRM_ORDER:
            self.state = ConversationState.ORDER_COMPLETE
            return f"Perfect! {self.order.get_summary()}\n\nPlease pull forward to the window."
        else:
            self.state = ConversationState.MODIFYING_ORDER
            return "What would you like to change?"
    
    def _handle_order_complete(self, intent: IntentResult) -> str:
        """Handle completed order state"""
        if intent.intent == OrderIntent.MODIFY_ITEM or intent.intent == OrderIntent.REMOVE_ITEM:
            self.state = ConversationState.MODIFYING_ORDER
            return self._handle_modification(intent)
        else:
            self.state = ConversationState.PAYMENT
            return f"Your total is ${self.order.get_total():.2f}. Please pull forward to the window."
    
    def _handle_payment(self, intent: IntentResult) -> str:
        """Handle payment state"""
        self.state = ConversationState.GOODBYE
        return "Thank you! Your order will be ready at the window."
    
    def _log_state(self):
        """Log current conversation state"""
        print(f"{Fore.CYAN}State: {self.state.value}")
        print(f"{Fore.YELLOW}Order items: {len(self.order.items)}")
        if self.order.items:
            print(f"{Fore.GREEN}Total: ${self.order.get_total():.2f}")
    
    def reset(self):
        """Reset conversation for new customer"""
        self.state = ConversationState.GREETING
        self.order = Order()
        self.conversation_history = []
        print(f"{Fore.MAGENTA}Conversation reset for new customer")

# Test the conversation manager
if __name__ == "__main__":
    print(f"{Fore.MAGENTA}Testing Conversation Manager\n")
    
    manager = ConversationManager()
    
    # Simulate a conversation
    test_inputs = [
        "Hi there",
        "I'd like two crunchy tacos please",
        "Add a large baja blast",
        "Actually make that three tacos",
        "No lettuce on any of them",
        "How much is the crunchwrap?",
        "Add one crunchwrap",
        "That's all",
        "Yes that's correct"
    ]
    
    for user_input in test_inputs:
        print(f"\n{Fore.CYAN}Customer: {user_input}")
        response, state = manager.process_input(user_input)
        print(f"{Fore.GREEN}Agent: {response}")
        print(f"{Fore.YELLOW}[State: {state.value}]")