
#!/usr/bin/env python3
"""Integration test for all components"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice_pipeline import VoicePipeline
from src.intent_detector_llm import TacoBellIntentDetector, OrderIntent
from colorama import init, Fore
import time
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

def test_tts_only():
    """Test only TTS functionality"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}TTS TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        voice = VoicePipeline(model_size="tiny")
        
        test_phrases = [
            "Welcome to Taco Bell!",
            "Would you like to try our new crunchy tacos?",
            "Your total is fifteen dollars and forty-nine cents",
        ]
        
        for phrase in test_phrases:
            print(f"{Fore.YELLOW}Testing: '{phrase}'")
            voice.speak(phrase)
            time.sleep(1)
            
        print(f"{Fore.GREEN}✓ TTS test complete!")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}TTS Error: {e}")
        return False

def test_asr_only():
    """Test only ASR functionality"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}ASR TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        voice = VoicePipeline(model_size="tiny")
        
        print(f"{Fore.YELLOW}Please say: 'I want two tacos'")
        text, confidence = voice.process_voice_input()
        
        if text:
            print(f"{Fore.GREEN}✓ Heard: '{text}' (confidence: {confidence:.2%})")
            return True
        else:
            print(f"{Fore.RED}✗ No transcription received")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}ASR Error: {e}")
        return False

def test_llm_only():
    """Test only LLM functionality"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}LLM TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"{Fore.YELLOW}No API key found in .env")
            return False
            
        detector = TacoBellIntentDetector()
        
        test_inputs = [
            "I'd like three crunchy tacos",
            "No lettuce please",
            "That's all"
        ]
        
        for text in test_inputs:
            print(f"{Fore.YELLOW}Testing: '{text}'")
            result = detector.detect_intent(text)
            print(f"{Fore.GREEN}  Intent: {result.intent.value} ({result.confidence:.0%})")
            print(f"{Fore.BLUE}  Response: {result.suggested_response}\n")
            time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}LLM Error: {e}")
        return False

def test_full_pipeline():
    """Test complete integrated pipeline"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}FULL PIPELINE TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        # Initialize all components
        print(f"{Fore.YELLOW}Initializing components...")
        voice = VoicePipeline(model_size="tiny")
        detector = TacoBellIntentDetector()
        
        print(f"{Fore.GREEN}✓ All components initialized!\n")
        
        # Simulate a conversation
        voice.speak("Welcome to Taco Bell! What can I get for you today?")
        
        conversation_history = []
        order_items = []
        
        for round_num in range(3):
            print(f"\n{Fore.CYAN}[Round {round_num + 1}/3]")
            print(f"{Fore.YELLOW}Listening for your order...")
            
            # Get voice input
            text, asr_confidence = voice.process_voice_input()
            
            if not text:
                voice.speak("I didn't catch that. Could you please repeat?")
                continue
            
            # Process with LLM
            result = detector.detect_intent(text, conversation_history)
            conversation_history.append(text)
            
            # Track order
            if result.entities.get('items'):
                order_items.extend(result.entities['items'])
            
            # Respond
            voice.speak(result.suggested_response)
            
            # Check if order is complete
            if result.intent == OrderIntent.CONFIRM_ORDER:
                if order_items:
                    voice.speak(f"Perfect! You ordered {len(order_items)} items. Thank you!")
                break
        
        print(f"\n{Fore.GREEN}✓ Full pipeline test complete!")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Pipeline Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print(f"{Fore.MAGENTA}╔{'═'*58}╗")
    print(f"{Fore.MAGENTA}║  TACO BELL VOICE AGENT - INTEGRATION TEST SUITE         ║")
    print(f"{Fore.MAGENTA}╚{'═'*58}╝\n")
    
    results = {
        "TTS": False,
        "ASR": False,
        "LLM": False,
        "Pipeline": False
    }
    
    # Test 1: TTS
    if input(f"{Fore.YELLOW}Test Text-to-Speech? (y/n): ").lower() == 'y':
        results["TTS"] = test_tts_only()
    
    # Test 2: ASR
    if input(f"{Fore.YELLOW}Test Speech Recognition? (y/n): ").lower() == 'y':
        results["ASR"] = test_asr_only()
    
    # Test 3: LLM
    if input(f"{Fore.YELLOW}Test LLM Intent Detection? (y/n): ").lower() == 'y':
        results["LLM"] = test_llm_only()
    
    # Test 4: Full Pipeline
    if input(f"{Fore.YELLOW}Test Full Pipeline? (y/n): ").lower() == 'y':
        results["Pipeline"] = test_full_pipeline()
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    for component, passed in results.items():
        status = f"{Fore.GREEN}✅ PASS" if passed else f"{Fore.RED}❌ FAIL"
        print(f"{component:10} {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print(f"\n{Fore.GREEN}🎉 ALL TESTS PASSED! Ready for Phase 3!")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n{Fore.YELLOW}⚠️  Failed components: {', '.join(failed)}")

if __name__ == "__main__":
    main()