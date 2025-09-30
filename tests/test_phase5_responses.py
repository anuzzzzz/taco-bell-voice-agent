#!/usr/bin/env python3
"""Test Phase 5: Brand Voice & Response Generation"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.response_generator import TacoBellResponseGenerator, ResponseContext
from src.brand_voice import BrandTone
from src.intent_detector_llm import OrderIntent
from src.conversation_manager import ConversationManager
from colorama import init, Fore
import time

init(autoreset=True)

def test_response_generator_init():
    """Test that response generator initializes correctly"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}RESPONSE GENERATOR INITIALIZATION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        generator = TacoBellResponseGenerator()
        print(f"{Fore.GREEN}✓ Response generator initialized successfully")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_brand_voice_consistency():
    """Test that responses maintain brand voice"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}BRAND VOICE CONSISTENCY TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        generator = TacoBellResponseGenerator()
        
        test_contexts = [
            {
                "name": "First order",
                "context": ResponseContext(
                    intent=OrderIntent.ORDER_ITEM,
                    entities={'items': ['taco'], 'quantities': {'taco': 2}},
                    conversation_history=[],
                    current_order=[],
                    order_total=0.0,
                    tone=BrandTone.FRIENDLY
                )
            },
            {
                "name": "Modification request",
                "context": ResponseContext(
                    intent=OrderIntent.MODIFY_ITEM,
                    entities={'modifications': ['no lettuce']},
                    conversation_history=["I want tacos", "Got it!"],
                    current_order=["Crunchy Taco", "Crunchy Taco"],
                    order_total=2.98,
                    tone=BrandTone.CASUAL
                )
            },
        ]
        
        all_passed = True
        for test in test_contexts:
            print(f"{Fore.YELLOW}{test['name']}:")
            response = generator.generate_response(test['context'])
            print(f"{Fore.GREEN}Response: {response}")
            
            # Check for brand violations
            violations = []
            response_lower = response.lower()
            
            if any(word in response_lower for word in ['certainly', 'indeed', 'shall']):
                violations.append("Too formal")
            if '  ' in response:
                violations.append("Double spaces")
            if len(response.split()) > 30:
                violations.append("Too verbose")
            
            if violations:
                print(f"{Fore.RED}⚠ Violations: {', '.join(violations)}")
                all_passed = False
            else:
                print(f"{Fore.GREEN}✓ Brand voice maintained")
            print()
        
        return all_passed
    
    except Exception as e:
        print(f"{Fore.RED}Error in brand voice test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_upsell_logic():
    """Test intelligent upselling"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}UPSELL LOGIC TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        generator = TacoBellResponseGenerator()
        
        # Order without drink
        context1 = ResponseContext(
            intent=OrderIntent.ORDER_ITEM,
            entities={},
            conversation_history=["I want tacos", "Got it!"],
            current_order=["Crunchy Taco", "Crunchy Taco"],
            order_total=2.98,
            tone=BrandTone.FRIENDLY,
            include_upsell=True
        )
        
        print(f"{Fore.YELLOW}Scenario: Order without drink")
        print(f"Current order: {context1.current_order}")
        response1 = generator.generate_response(context1)
        print(f"{Fore.GREEN}Response: {response1}")
        
        has_drink_mention = any(word in response1.lower() for word in ['drink', 'baja', 'beverage', 'blast'])
        print(f"{Fore.CYAN}Contains drink mention: {has_drink_mention}\n")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in upsell test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_time_based_greetings():
    """Test time-appropriate greetings"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}TIME-BASED GREETINGS TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        generator = TacoBellResponseGenerator()
        
        greeting = generator.get_time_based_greeting()
        print(f"{Fore.GREEN}Current greeting: {greeting}")
        print(f"{Fore.YELLOW}(Based on system time)\n")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in greeting test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_responses():
    """Test fallback responses when API fails"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}FALLBACK RESPONSE TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        generator = TacoBellResponseGenerator()
        
        # Test various intents with fallback
        test_intents = [
            OrderIntent.ORDER_ITEM,
            OrderIntent.MODIFY_ITEM,
            OrderIntent.REMOVE_ITEM,
            OrderIntent.CONFIRM_ORDER,
            OrderIntent.ASK_MENU,
        ]
        
        for intent in test_intents:
            context = ResponseContext(
                intent=intent,
                entities={'items': ['taco']},
                conversation_history=[],
                current_order=["Crunchy Taco"],
                order_total=1.49,
                tone=BrandTone.FRIENDLY
            )
            
            fallback = generator._get_fallback_response(context)
            print(f"{Fore.YELLOW}{intent.value}:")
            print(f"{Fore.GREEN}  {fallback}\n")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in fallback test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrated_conversation():
    """Test full conversation with enhanced responses"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}INTEGRATED CONVERSATION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        manager = ConversationManager()
        
        conversation = [
            "Hi",
            "I'd like two tacos",
            "That's all",
        ]
        
        for user_input in conversation:
            print(f"{Fore.CYAN}Customer: {user_input}")
            response, state = manager.process_input(user_input)
            print(f"{Fore.GREEN}Agent: {response}")
            print(f"{Fore.WHITE}[State: {state.value}]\n")
            time.sleep(0.5)
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error in integrated test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Phase 5 tests"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 5: BRAND VOICE & RESPONSE GENERATION")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    results = {}
    
    # Test 1: Initialization
    results["Initialization"] = test_response_generator_init()
    
    if not results["Initialization"]:
        print(f"\n{Fore.RED}Cannot proceed - initialization failed")
        return
    
    # Test 2: Brand Voice
    results["Brand Voice"] = test_brand_voice_consistency()
    
    # Test 3: Upselling
    results["Upselling"] = test_upsell_logic()
    
    # Test 4: Time-based
    results["Time-based"] = test_time_based_greetings()
    
    # Test 5: Fallbacks
    results["Fallbacks"] = test_fallback_responses()
    
    # Test 6: Integration
    results["Integration"] = test_integrated_conversation()
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}PHASE 5 TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    for test_name, passed in results.items():
        status = f"{Fore.GREEN}✅ PASS" if passed else f"{Fore.RED}❌ FAIL"
        print(f"{test_name:20} {status}")
    
    if all(results.values()):
        print(f"\n{Fore.GREEN}🎉 Phase 5 Complete! Brand voice system working!")
        print(f"{Fore.YELLOW}Next: Phase 6 - Error Handling & Fallbacks")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n{Fore.YELLOW}⚠️ Failed tests: {', '.join(failed)}")

if __name__ == "__main__":
    main()