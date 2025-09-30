"""
Enhanced Conversation Manager with Error Handling
Adds robust error handling to the conversation flow
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import json  # ADD THIS
from colorama import Fore, init

from src.intent_detector_llm import TacoBellIntentDetector, OrderIntent, IntentResult
from src.menu_rag import TacoBellMenuRAG, MenuItem
from src.response_generator import TacoBellResponseGenerator, ResponseContext
from src.brand_voice import BrandTone
from src.error_handler import (
    ErrorHandler, 
    ErrorContext, 
    ErrorType, 
    ErrorSeverity, 
    ConversationRepair
)

init(autoreset=True)

# ... rest of the code remains the same ...

class ConversationState(Enum):
    """States of the drive-thru conversation"""
    GREETING = "greeting"
    TAKING_ORDER = "taking_order"
    CONFIRMING_ITEM = "confirming_item"
    MODIFYING_ORDER = "modifying_order"
    ORDER_COMPLETE = "order_complete"
    CLARIFYING = "clarifying"  # NEW: For clarification loops
    ERROR_RECOVERY = "error_recovery"  # NEW: For error recovery
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
    confidence: float = 1.0  # NEW: Track confidence
    
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
    pending_clarification: Optional[str] = None  # NEW: Track what needs clarification
    
    def add_item(self, item: OrderItem):
        """Add or update item in order"""
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
    
    def has_low_confidence_items(self) -> bool:
        """Check if any items have low confidence"""
        return any(item.confidence < 0.7 for item in self.items)

class EnhancedConversationManager:
    """Enhanced conversation manager with error handling"""
    
    def __init__(self):
        """Initialize enhanced conversation manager"""
        self.state = ConversationState.GREETING
        self.order = Order()
        self.conversation_history = []
        self.context_window = 5
        
        # Initialize components
        self.intent_detector = TacoBellIntentDetector()
        self.menu_rag = TacoBellMenuRAG()
        self.response_generator = TacoBellResponseGenerator()
        self.error_handler = ErrorHandler()  # NEW
        self.conversation_repair = ConversationRepair()  # NEW
        
        # Error tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        self.last_successful_state = ConversationState.GREETING
        
        print(f"{Fore.GREEN}✓ Enhanced Conversation Manager initialized")
    
    def process_input(
        self, 
        user_input: str, 
        confidence: float = 1.0
    ) -> Tuple[str, ConversationState]:
        """
        Process user input with error handling
        
        Args:
            user_input: Customer's speech/text
            confidence: ASR confidence score
            
        Returns:
            Tuple of (response, new_state)
        """
        # Check for empty or low-quality input
        if not user_input or not user_input.strip():
            return self._handle_empty_input()
        
        # Check if confidence is too low
        if confidence < 0.5:
            return self._handle_low_confidence_input(user_input, confidence)
        
        # Check for confusion signals
        if self.conversation_repair.detect_confusion_signals(user_input):
            return self._handle_customer_confusion(user_input)
        
        try:
            # Add to history
            self.conversation_history.append(f"Customer: {user_input}")
            
            # Get intent with error handling
            intent_result = self._get_intent_with_retry(user_input)
            
            if not intent_result:
                return self._handle_intent_failure()
            
            # Process based on current state and intent
            response = self._handle_state_intent(intent_result)
            
            # Add response to history
            self.conversation_history.append(f"Agent: {response}")
            
            # Reset error counter on success
            self.consecutive_errors = 0
            self.last_successful_state = self.state
            
            # Log state
            self._log_state()
            
            return response, self.state
            
        except Exception as e:
            return self._handle_unexpected_error(e)
    
    def _get_intent_with_retry(self, user_input: str) -> Optional[IntentResult]:
        """Get intent with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                intent_result = self.intent_detector.detect_intent(
                    user_input,
                    self.conversation_history[-self.context_window:]
                )
                return intent_result
                
            except Exception as e:
                print(f"{Fore.YELLOW}Intent detection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    error_context = ErrorContext(
                        error_type=ErrorType.API_TIMEOUT,
                        severity=ErrorSeverity.MEDIUM,
                        message=str(e),
                        retry_count=attempt
                    )
                    self.error_handler.handle_error(error_context)
                else:
                    return None
        
        return None
    
    def _handle_empty_input(self) -> Tuple[str, ConversationState]:
        """Handle empty or silent input"""
        self.consecutive_errors += 1
        
        error_context = ErrorContext(
            error_type=ErrorType.ASR_FAILURE,
            severity=ErrorSeverity.LOW,
            message="No input received",
            retry_count=self.consecutive_errors
        )
        
        _, message = self.error_handler.handle_error(error_context)
        
        if self.consecutive_errors >= self.max_consecutive_errors:
            return "I'm having trouble hearing you. Is everything okay?", self.state
        
        return message, self.state
    
    def _handle_low_confidence_input(
        self, 
        user_input: str, 
        confidence: float
    ) -> Tuple[str, ConversationState]:
        """Handle low confidence ASR"""
        print(f"{Fore.YELLOW}Low confidence input: {confidence:.2f}")
        
        error_context = ErrorContext(
            error_type=ErrorType.ASR_LOW_CONFIDENCE,
            severity=ErrorSeverity.LOW,
            message=f"Low confidence: {confidence}",
            retry_count=0
        )
        
        # Still try to process but ask for confirmation
        try:
            intent_result = self.intent_detector.detect_intent(user_input)
            
            if intent_result and intent_result.entities.get('items'):
                items = intent_result.entities['items']
                clarification = self.conversation_repair.generate_clarification(
                    "unclear_item",
                    {"item": items[0]}
                )
                self.state = ConversationState.CLARIFYING
                return clarification, self.state
        except:
            pass
        
        _, message = self.error_handler.handle_error(error_context)
        return message, self.state
    
    def _handle_customer_confusion(self, user_input: str) -> Tuple[str, ConversationState]:
        """Handle customer confusion"""
        print(f"{Fore.CYAN}Customer appears confused")
        
        # Offer to restart or clarify
        recovery_message = self.conversation_repair.suggest_recovery_path(
            self.state.value
        )
        
        self.state = ConversationState.ERROR_RECOVERY
        return recovery_message, self.state
    
    def _handle_intent_failure(self) -> Tuple[str, ConversationState]:
        """Handle intent detection failure"""
        self.consecutive_errors += 1
        
        error_context = ErrorContext(
            error_type=ErrorType.API_TIMEOUT,
            severity=ErrorSeverity.HIGH,
            message="Intent detection failed",
            retry_count=self.consecutive_errors
        )
        
        _, message = self.error_handler.handle_error(error_context)
        
        return message, self.state
    
    def _handle_unexpected_error(self, exception: Exception) -> Tuple[str, ConversationState]:
        """Handle unexpected errors"""
        print(f"{Fore.RED}Unexpected error: {exception}")
        import traceback
        traceback.print_exc()
        
        self.consecutive_errors += 1
        
        error_context = ErrorContext(
            error_type=ErrorType.UNKNOWN_ERROR,
            severity=ErrorSeverity.HIGH,
            message=str(exception),
            retry_count=self.consecutive_errors
        )
        
        _, message = self.error_handler.handle_error(error_context)
        
        # Attempt to recover to last known good state
        if self.consecutive_errors >= self.max_consecutive_errors:
            self.state = self.last_successful_state
            return "Let's start fresh. What can I get for you?", self.state
        
        return message, self.state
    
    def _handle_state_intent(self, intent_result: IntentResult) -> str:
        """Handle intent based on current state (with error handling)"""
        
        try:
            if self.state == ConversationState.GREETING:
                return self._handle_greeting(intent_result)
            
            elif self.state == ConversationState.TAKING_ORDER:
                return self._handle_taking_order(intent_result)
            
            elif self.state == ConversationState.CLARIFYING:
                return self._handle_clarifying(intent_result)
            
            elif self.state == ConversationState.ERROR_RECOVERY:
                return self._handle_error_recovery_state(intent_result)
            
            elif self.state == ConversationState.ORDER_COMPLETE:
                return self._handle_order_complete(intent_result)
            
            elif self.state == ConversationState.PAYMENT:
                return self._handle_payment(intent_result)
            
            else:
                return "Thank you for choosing Taco Bell!"
                
        except Exception as e:
            print(f"{Fore.RED}Error in state handler: {e}")
            return "Let me help you with that. What would you like?"
    
    def _handle_greeting(self, intent: IntentResult) -> str:
        """Handle greeting state"""
        self.state = ConversationState.TAKING_ORDER
        
        if intent.intent == OrderIntent.ORDER_ITEM:
            return self._process_order_item(intent)
        else:
            return self.response_generator.get_time_based_greeting()
    
    def _handle_taking_order(self, intent: IntentResult) -> str:
        """Handle order-taking state"""
        
        if intent.intent == OrderIntent.ORDER_ITEM:
            return self._process_order_item(intent)
        
        elif intent.intent == OrderIntent.CONFIRM_ORDER:
            if self.order.items:
                # Check for low confidence items before confirming
                if self.order.has_low_confidence_items():
                    self.state = ConversationState.CLARIFYING
                    return "Just to make sure I got everything right - " + self.order.get_summary()
                
                self.state = ConversationState.ORDER_COMPLETE
                return f"{self.order.get_summary()}\n\nIs that correct?"
            else:
                return "You haven't ordered anything yet. What would you like?"
        
        elif intent.intent == OrderIntent.REMOVE_ITEM:
            return self._handle_remove_item(intent)
        
        else:
            return "What would you like to order?"
    
    def _handle_clarifying(self, intent: IntentResult) -> str:
        """Handle clarification state"""
        # User confirmed or denied something
        if intent.intent == OrderIntent.CONFIRM_ORDER or "yes" in intent.raw_text.lower():
            self.state = ConversationState.TAKING_ORDER
            return "Great! Anything else?"
        
        # User wants to correct something
        self.state = ConversationState.TAKING_ORDER
        return "No problem. What should it be?"
    
    def _handle_error_recovery_state(self, intent: IntentResult) -> str:
        """Handle error recovery state"""
        # Try to get back on track
        self.state = self.last_successful_state
        
        if intent.intent == OrderIntent.ORDER_ITEM:
            return self._process_order_item(intent)
        else:
            return "What can I get for you?"
    
    def _process_order_item(self, intent: IntentResult) -> str:
        """Process order item with error handling"""
        items_added = []
        items_not_found = []
        
        mentioned_items = intent.entities.get('items', [])
        quantities = intent.entities.get('quantities', {})
        
        for item_name in mentioned_items:
            try:
                search_results = self.menu_rag.search_menu(item_name, top_k=1)
                
                if search_results and search_results[0].score > 0.5:
                    menu_item = search_results[0].item
                    qty = quantities.get(item_name, 1)
                    
                    # Mark confidence based on search score
                    confidence = search_results[0].score
                    
                    order_item = OrderItem(
                        name=menu_item.name,
                        quantity=qty,
                        price=menu_item.price,
                        confidence=confidence
                    )
                    
                    self.order.add_item(order_item)
                    items_added.append(f"{qty} {menu_item.name}")
                else:
                    items_not_found.append(item_name)
                    
            except Exception as e:
                print(f"{Fore.RED}Error processing item {item_name}: {e}")
                items_not_found.append(item_name)
        
        # Build response
        if items_added:
            response = f"I've added {', '.join(items_added)} to your order."
            
            # Add recommendation
            current_item_names = [item.name for item in self.order.items]
            recommendations = self.menu_rag.get_recommendations(current_item_names)
            
            if recommendations:
                rec = recommendations[0]
                response += f" Would you like to add a {rec.name} for ${rec.price:.2f}?"
            else:
                response += " Anything else?"
        else:
            # Handle menu item not found
            error_context = ErrorContext(
                error_type=ErrorType.MENU_ITEM_NOT_FOUND,
                severity=ErrorSeverity.LOW,
                message=f"Items not found: {items_not_found}"
            )
            _, error_msg = self.error_handler.handle_error(error_context)
            
            response = error_msg
            
            if mentioned_items:
                search_results = self.menu_rag.search_menu(mentioned_items[0], top_k=3)
                if search_results:
                    suggestions = [r.item.name for r in search_results]
                    response += f" Did you mean {', '.join(suggestions)}?"
        
        return response
    
    def _handle_remove_item(self, intent: IntentResult) -> str:
        """Handle item removal"""
        items = intent.entities.get('items', [])
        
        if not items:
            return "What would you like to remove?"
        
        removed = []
        for item_name in items:
            for order_item in self.order.items[:]:
                if item_name.lower() in order_item.name.lower():
                    self.order.items.remove(order_item)
                    removed.append(order_item.name)
                    break
        
        if removed:
            return f"I've removed {', '.join(removed)} from your order. Anything else?"
        else:
            return "I couldn't find that item in your order."
    
    def _handle_order_complete(self, intent: IntentResult) -> str:
        """Handle completed order state"""
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
        print(f"{Fore.WHITE}Consecutive errors: {self.consecutive_errors}")
        
        if self.order.items:
            print(f"{Fore.MAGENTA}Current order:")
            for item in self.order.items:
                conf_indicator = "✓" if item.confidence > 0.7 else "?"
                print(f"  {conf_indicator} {item.to_string()} - ${item.get_total_price():.2f}")
            print(f"{Fore.GREEN}Total: ${self.order.get_total():.2f}")
    
    def get_diagnostics(self) -> dict:
        """Get diagnostic information"""
        return {
            "state": self.state.value,
            "order_items": len(self.order.items),
            "consecutive_errors": self.consecutive_errors,
            "error_stats": self.error_handler.get_error_stats(),
            "conversation_length": len(self.conversation_history)
        }
    
    def reset(self):
        """Reset conversation for new customer"""
        self.state = ConversationState.GREETING
        self.order = Order()
        self.conversation_history = []
        self.consecutive_errors = 0
        print(f"{Fore.MAGENTA}Conversation reset for new customer")