"""
Error Handling and Recovery System
Handles failures gracefully and implements retry logic
"""

import time
from typing import Optional, Callable, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from colorama import Fore, init

init(autoreset=True)

class ErrorType(Enum):
    """Types of errors the system can encounter"""
    ASR_FAILURE = "asr_failure"              # Speech recognition failed
    ASR_LOW_CONFIDENCE = "asr_low_confidence"  # Low confidence transcription
    API_TIMEOUT = "api_timeout"               # OpenAI API timeout
    API_RATE_LIMIT = "api_rate_limit"         # Rate limit hit
    NETWORK_ERROR = "network_error"           # Network connection issue
    MENU_ITEM_NOT_FOUND = "menu_item_not_found"  # Item not in menu
    AMBIGUOUS_ORDER = "ambiguous_order"       # Unclear what customer wants
    EMPTY_ORDER = "empty_order"               # No items in order
    INVALID_STATE = "invalid_state"           # Conversation state error
    UNKNOWN_ERROR = "unknown_error"           # Catch-all

class ErrorSeverity(Enum):
    """Severity levels for errors"""
    LOW = "low"          # Minor issue, can continue
    MEDIUM = "medium"    # Needs attention, can recover
    HIGH = "high"        # Serious issue, may need restart
    CRITICAL = "critical"  # System failure

@dataclass
class ErrorContext:
    """Context information about an error"""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    retry_count: int = 0
    max_retries: int = 3
    user_facing_message: Optional[str] = None
    recovery_action: Optional[str] = None

class ErrorHandler:
    """Centralized error handling and recovery"""
    
    def __init__(self):
        """Initialize error handler"""
        self.error_counts = {}  # Track error frequency
        self.last_error_time = {}  # Track when errors occurred
        
        # Recovery strategies for each error type
        self.recovery_strategies = {
            ErrorType.ASR_FAILURE: self._recover_asr_failure,
            ErrorType.ASR_LOW_CONFIDENCE: self._recover_low_confidence,
            ErrorType.API_TIMEOUT: self._recover_api_timeout,
            ErrorType.API_RATE_LIMIT: self._recover_rate_limit,
            ErrorType.NETWORK_ERROR: self._recover_network_error,
            ErrorType.MENU_ITEM_NOT_FOUND: self._recover_menu_not_found,
            ErrorType.AMBIGUOUS_ORDER: self._recover_ambiguous_order,
            ErrorType.EMPTY_ORDER: self._recover_empty_order,
        }
        
        # User-facing messages for each error type
        self.user_messages = {
            ErrorType.ASR_FAILURE: "I didn't catch that. Could you repeat?",
            ErrorType.ASR_LOW_CONFIDENCE: "Sorry, I didn't quite hear that. What did you say?",
            ErrorType.API_TIMEOUT: "Give me just a second...",
            ErrorType.API_RATE_LIMIT: "One moment please...",
            ErrorType.NETWORK_ERROR: "Having a little technical issue. Let me try that again.",
            ErrorType.MENU_ITEM_NOT_FOUND: "I couldn't find that on our menu. What else can I get you?",
            ErrorType.AMBIGUOUS_ORDER: "Just to clarify - what would you like?",
            ErrorType.EMPTY_ORDER: "What can I get started for you today?",
        }
        
        print(f"{Fore.GREEN}✓ Error Handler initialized")
    
    def handle_error(self, error_context: ErrorContext) -> Tuple[bool, str]:
        """
        Handle an error and attempt recovery
        
        Args:
            error_context: Context about the error
            
        Returns:
            Tuple of (success, user_message)
        """
        # Log the error
        self._log_error(error_context)
        
        # Track error frequency
        self._track_error(error_context.error_type)
        
        # Get user-facing message
        user_message = error_context.user_facing_message or \
                      self.user_messages.get(error_context.error_type, 
                                            "Let me try that again.")
        
        # Attempt recovery if strategy exists
        recovery_strategy = self.recovery_strategies.get(error_context.error_type)
        
        if recovery_strategy and error_context.retry_count < error_context.max_retries:
            success = recovery_strategy(error_context)
            return success, user_message
        
        # If no recovery or max retries reached
        if error_context.retry_count >= error_context.max_retries:
            print(f"{Fore.RED}Max retries reached for {error_context.error_type.value}")
            return False, "I'm having trouble processing that. Let's try something else."
        
        return False, user_message
    
    def _track_error(self, error_type: ErrorType):
        """Track error occurrence for monitoring"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        
        self.error_counts[error_type] += 1
        self.last_error_time[error_type] = time.time()
    
    def _log_error(self, context: ErrorContext):
        """Log error details"""
        severity_colors = {
            ErrorSeverity.LOW: Fore.YELLOW,
            ErrorSeverity.MEDIUM: Fore.YELLOW,
            ErrorSeverity.HIGH: Fore.RED,
            ErrorSeverity.CRITICAL: Fore.RED
        }
        
        color = severity_colors.get(context.severity, Fore.YELLOW)
        print(f"{color}[ERROR] {context.error_type.value}")
        print(f"{color}  Severity: {context.severity.value}")
        print(f"{color}  Message: {context.message}")
        if context.retry_count > 0:
            print(f"{color}  Retry: {context.retry_count}/{context.max_retries}")
    
    # Recovery strategies
    
    def _recover_asr_failure(self, context: ErrorContext) -> bool:
        """Recover from ASR failure"""
        print(f"{Fore.CYAN}Attempting ASR recovery...")
        # In real implementation, might try:
        # - Adjusting microphone gain
        # - Increasing silence threshold
        # - Using backup ASR model
        return True  # Allow retry
    
    def _recover_low_confidence(self, context: ErrorContext) -> bool:
        """Recover from low confidence transcription"""
        print(f"{Fore.CYAN}Handling low confidence transcription...")
        # Strategy: Ask for clarification rather than acting on uncertain input
        return True
    
    def _recover_api_timeout(self, context: ErrorContext) -> bool:
        """Recover from API timeout"""
        print(f"{Fore.CYAN}Recovering from API timeout...")
        time.sleep(1)  # Brief delay before retry
        return True
    
    def _recover_rate_limit(self, context: ErrorContext) -> bool:
        """Recover from rate limit"""
        print(f"{Fore.CYAN}Handling rate limit...")
        wait_time = min(2 ** context.retry_count, 10)  # Exponential backoff
        time.sleep(wait_time)
        return True
    
    def _recover_network_error(self, context: ErrorContext) -> bool:
        """Recover from network error"""
        print(f"{Fore.CYAN}Recovering from network error...")
        time.sleep(2)  # Wait before retry
        return True
    
    def _recover_menu_not_found(self, context: ErrorContext) -> bool:
        """Recover from menu item not found"""
        print(f"{Fore.CYAN}Handling menu item not found...")
        # Strategy: Suggest similar items or ask for clarification
        return True
    
    def _recover_ambiguous_order(self, context: ErrorContext) -> bool:
        """Recover from ambiguous order"""
        print(f"{Fore.CYAN}Clarifying ambiguous order...")
        # Strategy: Ask clarifying questions
        return True
    
    def _recover_empty_order(self, context: ErrorContext) -> bool:
        """Recover from empty order"""
        print(f"{Fore.CYAN}Handling empty order...")
        return True
    
    def get_error_stats(self) -> dict:
        """Get error statistics for monitoring"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "by_type": {
                error_type.value: count  # Convert ErrorType enum to string
                for error_type, count in self.error_counts.items()
            },
            "last_errors": {
                error_type.value: time.time() - timestamp
                for error_type, timestamp in self.last_error_time.items()
            }
        }
    
    def should_escalate(self, error_type: ErrorType) -> bool:
        """Determine if error should be escalated to human"""
        # Escalate if same error occurs too frequently
        count = self.error_counts.get(error_type, 0)
        
        if count >= 5:  # 5 of same error type
            print(f"{Fore.RED}Escalating: Too many {error_type.value} errors")
            return True
        
        # Escalate critical errors immediately
        if error_type == ErrorType.CRITICAL:
            return True
        
        return False


class RetryHandler:
    """Handles retry logic with exponential backoff"""
    
    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 10.0
    ) -> Any:
        """
        Retry a function with exponential backoff
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for each retry
            max_delay: Maximum delay between retries
            
        Returns:
            Result from function or None if all retries failed
        """
        delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"{Fore.RED}All retries failed: {e}")
                    return None
                
                print(f"{Fore.YELLOW}Attempt {attempt + 1} failed, retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
        
        return None


class ConversationRepair:
    """Strategies for repairing broken conversations"""
    
    def __init__(self):
        """Initialize conversation repair"""
        self.clarification_templates = {
            "unclear_item": [
                "Just to make sure - did you say {item}?",
                "I want to get this right - you said {item}, correct?",
                "Quick question - is that {item}?"
            ],
            "unclear_quantity": [
                "How many {item} would you like?",
                "Did you want one {item} or more?",
                "Just to confirm - how many {item}s?"
            ],
            "unclear_modification": [
                "What changes would you like to make?",
                "What would you like to add or remove?",
                "How would you like to modify that?"
            ]
        }
    
    def generate_clarification(self, issue_type: str, context: dict) -> str:
        """
        Generate a clarification question
        
        Args:
            issue_type: Type of clarification needed
            context: Context information (item name, quantity, etc.)
            
        Returns:
            Clarification question
        """
        templates = self.clarification_templates.get(issue_type, [
            "Could you repeat that?",
            "I didn't quite catch that. What did you say?"
        ])
        
        import random
        template = random.choice(templates)
        
        # Fill in context variables
        try:
            return template.format(**context)
        except KeyError:
            return template
    
    def detect_confusion_signals(self, text: str) -> bool:
        """Detect if customer seems confused"""
        confusion_signals = [
            "what", "huh", "wait", "uh", "um", "confused",
            "don't understand", "not sure", "i don't know"
        ]
        
        text_lower = text.lower()
        return any(signal in text_lower for signal in confusion_signals)
    
    def suggest_recovery_path(self, conversation_state: str) -> str:
        """Suggest how to recover based on conversation state"""
        recovery_paths = {
            "greeting": "Let's start over. Welcome to Taco Bell! What can I get you?",
            "taking_order": "No problem! What would you like to order?",
            "confirming_item": "Let me know what you'd like, and I'll make sure I get it right.",
            "order_complete": "Your order is ready. Would you like to change anything?"
        }
        
        return recovery_paths.get(conversation_state, 
                                 "Let's try that again. What can I help you with?")


# Test the error handler
if __name__ == "__main__":
    print(f"{Fore.MAGENTA}Testing Error Handler\n")
    
    handler = ErrorHandler()
    repair = ConversationRepair()
    
    # Test error handling
    print(f"{Fore.CYAN}Test 1: ASR Failure")
    error = ErrorContext(
        error_type=ErrorType.ASR_FAILURE,
        severity=ErrorSeverity.MEDIUM,
        message="No audio detected",
        retry_count=0
    )
    success, message = handler.handle_error(error)
    print(f"Recovery: {success}, Message: {message}\n")
    
    # Test clarification
    print(f"{Fore.CYAN}Test 2: Clarification Generation")
    clarification = repair.generate_clarification(
        "unclear_item",
        {"item": "Crunchy Taco"}
    )
    print(f"Clarification: {clarification}\n")
    
    # Test confusion detection
    print(f"{Fore.CYAN}Test 3: Confusion Detection")
    confused_text = "Wait, I don't understand"
    is_confused = repair.detect_confusion_signals(confused_text)
    print(f"Confused: {is_confused}\n")
    
    # Test error stats
    print(f"{Fore.CYAN}Test 4: Error Statistics")
    stats = handler.get_error_stats()
    print(f"Stats: {stats}")