#!/usr/bin/env python3
"""Test LLM-based intent detection for Phase 2"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.intent_detector_llm import TacoBellIntentDetector, OrderIntent
from src.voice_pipeline import VoicePipeline
from colorama import init, Fore
import time

init(autoreset=True)

def test_gpt_intent_detection():
    """Test GPT intent detection with various inputs"""
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}GPT INTENT DETECTION TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    try:
        detector = TacoBellIntentDetector()
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}")
        print(f"{Fore.YELLOW}Make sure your .env file contains OPENAI_API_KEY")
        return
    
    # Test cases - real drive-thru scenarios
    test_cases = [
        "Hi there",
        "I'd like two crunchy tacos please",
        "Can I get a large Baja Blast with that?",
        "Actually make it three tacos",
        "No lettuce on any of them",
        "How much is the crunchwrap supreme?",
        "Add a crunchwrap to my order",
        "That's all for me",
    ]
    
    print(f"{Fore.YELLOW}Testing natural language understanding...\n")
    conversation_history = []
    
    for i, text in enumerate(test_cases, 1):
        print(f"{Fore.CYAN}[{i}/8] Customer: '{text}'")
        
        result = detector.detect_intent(text, conversation_history)
        conversation_history.append(text)
        
        # Display results with colors
        conf_color = Fore.GREEN if result.confidence > 0.7 else Fore.YELLOW
        print(f"  {conf_color}→ {result.intent.value} ({result.confidence:.0%})")
        
        if result.entities.get('items'):
            print(f"  {Fore.MAGENTA}  Items: {result.entities['items']}")
        if result.entities.get('quantities'):
            print(f"  {Fore.MAGENTA}  Qty: {result.entities['quantities']}")
            
        print(f"  {Fore.BLUE}  Response: '{result.suggested_response}'")
        print()
        
        time.sleep(0.5)  # Avoid rate limits

def test_voice_to_intent():
    """Test complete pipeline: Voice → Whisper → GPT → Response"""
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}VOICE TO INTENT PIPELINE TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    # Initialize components
    print(f"{Fore.YELLOW}Initializing components...")
    voice = VoicePipeline(model_size="tiny")  # Fast for testing
    detector = TacoBellIntentDetector()
    
    print(f"{Fore.GREEN}Ready for voice input!\n")
    
    # Test conversation loop
    conversation_history = []
    
    for round_num in range(3):
        print(f"{Fore.CYAN}Round {round_num + 1}/3")
        print(f"{Fore.YELLOW}Speak your order...")
        
        # Get voice input
        text, confidence = voice.process_voice_input()
        
        if text:
            # Detect intent
            result = detector.detect_intent(text, conversation_history)
            conversation_history.append(text)
            
            # Speak response
            voice.speak(result.suggested_response)
            
            # Check if order is complete
            if result.intent == OrderIntent.CONFIRM_ORDER:
                voice.speak("Thank you for your order!")
                break
        else:
            voice.speak("Sorry, I didn't catch that. Could you repeat?")
    
    print(f"\n{Fore.GREEN}Pipeline test complete!")

def test_edge_cases():
    """Test edge cases and complex orders"""
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}EDGE CASES TEST")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    detector = TacoBellIntentDetector()
    
    edge_cases = [
        "Umm... uh... I'll take... you know what, give me tacos",
        "TWO CRUNCHY TACOS NO WAIT THREE",
        "i want 2 tacos 3 burritos and a large drink",
        "Everything but hold the lettuce and add extra cheese and make it supreme",
        "What's your cheapest item?",
        "Cancel that last thing I said",
        "",  # Empty input
        "🌮🌮🌮",  # Emojis
    ]
    
    for text in edge_cases:
        print(f"{Fore.CYAN}Input: '{text}'")
        result = detector.detect_intent(text)
        print(f"  → {result.intent.value} ({result.confidence:.0%})")
        print(f"  Response: {result.suggested_response}")
        print()

if __name__ == "__main__":
    # Test 1: Basic GPT intent detection
    test_gpt_intent_detection()
    
    print(f"\n{Fore.MAGENTA}Press Enter to test edge cases...")
    input()
    
    # Test 2: Edge cases
    test_edge_cases()
    
    print(f"\n{Fore.MAGENTA}Press Enter to test voice pipeline...")
    input()
    
    # Test 3: Full voice pipeline (optional)
    response = input(f"{Fore.YELLOW}Test voice input? (y/n): ")
    if response.lower() == 'y':
        test_voice_to_intent()
    
    print(f"\n{Fore.GREEN}✓ Phase 2 testing complete!")