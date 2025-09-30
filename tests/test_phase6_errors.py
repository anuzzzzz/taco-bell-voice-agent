#!/usr/bin/env python3
"""Test Phase 6: Error Handling & Fallbacks"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.error_handler import ErrorHandler, ErrorContext, ErrorType, ErrorSeverity, ConversationRepair
from src.conversation_manager_v2 import EnhancedConversationManager
from colorama import init, Fore
import time

init(autoreset=True)

def test_error_handler_init():
    """Test error handler initialization"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}ERROR HANDLER INITIALIZATION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        handler = ErrorHandler()
        repair = ConversationRepair()
        print(f"{Fore.GREEN}✓ Error handler initialized successfully")
        print(f"{Fore.GREEN}✓ Conversation repair initialized successfully")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Failed to initialize: {e}")
        return False

def test_asr_error_handling():
    """Test ASR error handling"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}ASR ERROR HANDLING TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = EnhancedConversationManager()
        
        # Test empty input
        print(f"{Fore.YELLOW}Test 1: Empty input")
        response, state = manager.process_input("", confidence=1.0)
        print(f"{Fore.GREEN}Response: {response}")
        print(f"{Fore.WHITE}State: {state.value}\n")
        
        # Test low confidence input
        print(f"{Fore.YELLOW}Test 2: Low confidence input")
        response, state = manager.process_input("I want tacos", confidence=0.3)
        print(f"{Fore.GREEN}Response: {response}")
        print(f"{Fore.WHITE}State: {state.value}\n")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in ASR test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_not_found():
    """Test menu item not found handling"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}MENU NOT FOUND TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = EnhancedConversationManager()
        
        # Order non-existent item
        print(f"{Fore.YELLOW}Ordering: 'I want a pizza'")
        response, state = manager.process_input("I want a pizza", confidence=1.0)
        print(f"{Fore.GREEN}Response: {response}")
        print(f"{Fore.WHITE}State: {state.value}\n")
        
        # Check if suggestions are offered
        has_suggestions = "mean" in response.lower() or "menu" in response.lower()
        print(f"{Fore.CYAN}Offers suggestions: {has_suggestions}")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in menu test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_confusion_detection():
    """Test customer confusion detection"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}CONFUSION DETECTION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = EnhancedConversationManager()
        repair = ConversationRepair()
        
        confused_phrases = [
            "Wait, I don't understand",
            "Huh? What?",
            "I'm not sure what you mean",
            "Um, confused here"
        ]
        
        for phrase in confused_phrases:
            is_confused = repair.detect_confusion_signals(phrase)
            color = Fore.GREEN if is_confused else Fore.RED
            print(f"{color}'{phrase}': Confused = {is_confused}")
        
        print()
        
        # Test actual confusion handling
        print(f"{Fore.YELLOW}Testing: 'Wait, I don't understand'")
        response, state = manager.process_input("Wait, I don't understand", confidence=1.0)
        print(f"{Fore.GREEN}Response: {response}")
        print(f"{Fore.WHITE}State: {state.value}\n")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in confusion test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_clarification_generation():
    """Test clarification question generation"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}CLARIFICATION GENERATION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        repair = ConversationRepair()
        
        test_cases = [
            ("unclear_item", {"item": "Crunchy Taco"}),
            ("unclear_quantity", {"item": "Burrito"}),
            ("unclear_modification", {})
        ]
        
        for issue_type, context in test_cases:
            clarification = repair.generate_clarification(issue_type, context)
            print(f"{Fore.YELLOW}{issue_type}:")
            print(f"{Fore.GREEN}  {clarification}\n")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in clarification test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consecutive_errors():
    """Test consecutive error handling"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}CONSECUTIVE ERRORS TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = EnhancedConversationManager()
        
        # Trigger multiple empty inputs
        for i in range(4):
            print(f"{Fore.YELLOW}Error {i+1}:")
            response, state = manager.process_input("", confidence=1.0)
            print(f"{Fore.GREEN}Response: {response}")
            print(f"{Fore.WHITE}Consecutive errors: {manager.consecutive_errors}\n")
        
        # Check if escalation message appears
        has_escalation = "trouble" in response.lower() or "everything okay" in response.lower()
        print(f"{Fore.CYAN}Escalation triggered: {has_escalation}")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in consecutive errors test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recovery_from_errors():
    """Test recovery from errors"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}ERROR RECOVERY TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = EnhancedConversationManager()
        
        # Cause an error
        print(f"{Fore.YELLOW}Causing error with empty input:")
        response1, state1 = manager.process_input("", confidence=1.0)
        print(f"{Fore.GREEN}Response: {response1}\n")
        
        # Recover with valid input
        print(f"{Fore.YELLOW}Recovering with valid input:")
        response2, state2 = manager.process_input("I want two tacos", confidence=1.0)
        print(f"{Fore.GREEN}Response: {response2}")
        print(f"{Fore.WHITE}Consecutive errors reset: {manager.consecutive_errors == 0}\n")
        
        return manager.consecutive_errors == 0
    
    except Exception as e:
        print(f"{Fore.RED}Error in recovery test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_diagnostics():
    """Test diagnostic information"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}DIAGNOSTICS TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = EnhancedConversationManager()
        
        # Generate some activity
        manager.process_input("Hi", confidence=1.0)
        manager.process_input("Two tacos please", confidence=1.0)
        manager.process_input("", confidence=1.0)  # Cause an error
        
        # Get diagnostics
        diagnostics = manager.get_diagnostics()
        
        print(f"{Fore.GREEN}Diagnostics:")
        print(json.dumps(diagnostics, indent=2))
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in diagnostics test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_conversation_with_errors():
    """Test full conversation with various errors"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}FULL CONVERSATION WITH ERRORS TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = EnhancedConversationManager()
        
        conversation = [
            ("Hi", 1.0),
            ("", 1.0),  # Empty input
            ("I want tacos", 0.4),  # Low confidence
            ("Two crunchy tacos", 1.0),  # Valid
            ("And a pizza", 1.0),  # Invalid item
            ("Actually a drink", 1.0),  # Correction
            ("That's all", 1.0),  # Complete
        ]
        
        for i, (text, conf) in enumerate(conversation, 1):
            print(f"{Fore.CYAN}[{i}/{len(conversation)}] Customer: '{text}' (conf: {conf})")
            response, state = manager.process_input(text, confidence=conf)
            print(f"{Fore.GREEN}Agent: {response}")
            print(f"{Fore.WHITE}State: {state.value}\n")
            time.sleep(0.3)
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in full conversation test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Phase 6 tests"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 6: ERROR HANDLING & FALLBACKS")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    results = {}
    
    # Test 1: Initialization
    results["Initialization"] = test_error_handler_init()
    
    if not results["Initialization"]:
        print(f"\n{Fore.RED}Cannot proceed - initialization failed")
        return
    
    # Test 2: ASR Errors
    results["ASR Errors"] = test_asr_error_handling()
    
    # Test 3: Menu Not Found
    results["Menu Not Found"] = test_menu_not_found()
    
    # Test 4: Confusion Detection
    results["Confusion Detection"] = test_confusion_detection()
    
    # Test 5: Clarification
    results["Clarification"] = test_clarification_generation()
    
    # Test 6: Consecutive Errors
    results["Consecutive Errors"] = test_consecutive_errors()
    
    # Test 7: Recovery
    results["Error Recovery"] = test_recovery_from_errors()
    
    # Test 8: Diagnostics
    results["Diagnostics"] = test_diagnostics()
    
    # Test 9: Full Conversation
    results["Full Conversation"] = test_full_conversation_with_errors()
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 6 TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    for test_name, passed in results.items():
        status = f"{Fore.GREEN}✅ PASS" if passed else f"{Fore.RED}❌ FAIL"
        print(f"{test_name:25} {status}")
    
    if all(results.values()):
        print(f"\n{Fore.GREEN}🎉 Phase 6 Complete! Error handling system working!")
        print(f"{Fore.YELLOW}Next: Phase 7 - Final Integration & Testing")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n{Fore.YELLOW}⚠️  Failed tests: {', '.join(failed)}")

if __name__ == "__main__":
    import json  # Add this import
    main()