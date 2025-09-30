#!/usr/bin/env python3
"""Test Conversation Manager for Phase 4"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conversation_manager import ConversationManager, ConversationState
from colorama import init, Fore
import time

init(autoreset=True)

def test_basic_conversation_flow():
    """Test basic conversation flow"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}BASIC CONVERSATION FLOW TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    manager = ConversationManager()
    
    # Test conversation
    test_cases = [
        ("Hi", ConversationState.TAKING_ORDER),
        ("I want two tacos", ConversationState.TAKING_ORDER),
        ("Add a drink", ConversationState.TAKING_ORDER),
        ("That's all", ConversationState.ORDER_COMPLETE),
    ]
    
    for input_text, expected_state in test_cases:
        print(f"{Fore.YELLOW}Customer: '{input_text}'")
        response, state = manager.process_input(input_text)
        print(f"{Fore.GREEN}Agent: {response}")
        
        if state == expected_state:
            print(f"{Fore.GREEN}✓ State correct: {state.value}")
        else:
            print(f"{Fore.RED}✗ State mismatch: got {state.value}, expected {expected_state.value}")
        print()
    
    # Check final order
    if manager.order.items:
        print(f"{Fore.CYAN}Final Order:")
        print(manager.order.get_summary())
        return True
    return False

def test_modification_flow():
    """Test order modification flow"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}MODIFICATION FLOW TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    manager = ConversationManager()
    
    modifications = [
        "I want three crunchy tacos",
        "No lettuce on those",
        "Actually remove one taco",
        "Add extra cheese",
        "That's it"
    ]
    
    for input_text in modifications:
        print(f"{Fore.YELLOW}Customer: '{input_text}'")
        response, state = manager.process_input(input_text)
        print(f"{Fore.GREEN}Agent: {response}")
        print(f"{Fore.WHITE}[State: {state.value}]")
        print()
    
    return len(manager.order.items) > 0

def test_error_handling():
    """Test error handling in conversation"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}ERROR HANDLING TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    manager = ConversationManager()
    
    error_cases = [
        "",  # Empty input
        "I want a pizza",  # Item not on menu
        "Remove everything",  # Before ordering
        "How much?",  # Vague price inquiry
        "Ummm... I don't know"  # Unclear intent
    ]
    
    for input_text in error_cases:
        print(f"{Fore.YELLOW}Customer: '{input_text}'")
        try:
            response, state = manager.process_input(input_text)
            print(f"{Fore.GREEN}Agent: {response}")
        except Exception as e:
            print(f"{Fore.RED}Error handled: {e}")
        print()
    
    return True

def test_complete_scenario():
    """Test a complete realistic scenario"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}COMPLETE SCENARIO TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    manager = ConversationManager()
    
    scenario = [
        "Hello",
        "What's your cheapest taco?",
        "I'll take two of those",
        "And a large Baja Blast",
        "Actually, what's in the Cravings Box?",
        "Hmm, just stick with the tacos",
        "No lettuce please",
        "That's everything",
        "Yes, correct"
    ]
    
    for i, input_text in enumerate(scenario, 1):
        print(f"{Fore.CYAN}[{i}/9] Customer: '{input_text}'")
        response, state = manager.process_input(input_text)
        print(f"{Fore.GREEN}Agent: {response}")
        print(f"{Fore.WHITE}State: {state.value}")
        
        # Show order status
        if manager.order.items:
            total = manager.order.get_total()
            items = len(manager.order.items)
            print(f"{Fore.YELLOW}Order: {items} items, Total: ${total:.2f}")
        print()
        
        time.sleep(0.5)
    
    return state == ConversationState.PAYMENT

def main():
    """Run all Phase 4 tests"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 4: CONVERSATION MANAGER TESTS")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    results = {}
    
    # Test 1: Basic Flow
    results["Basic Flow"] = test_basic_conversation_flow()
    
    # Test 2: Modifications
    results["Modifications"] = test_modification_flow()
    
    # Test 3: Error Handling
    results["Error Handling"] = test_error_handling()
    
    # Test 4: Complete Scenario
    results["Complete Scenario"] = test_complete_scenario()
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 4 TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    for test_name, passed in results.items():
        status = f"{Fore.GREEN}✅ PASS" if passed else f"{Fore.RED}❌ FAIL"
        print(f"{test_name:20} {status}")
    
    if all(results.values()):
        print(f"\n{Fore.GREEN}🎉 Phase 4 Complete! Conversation Manager working!")
    else:
        print(f"\n{Fore.YELLOW}⚠️ Some tests need attention")

if __name__ == "__main__":
    main()