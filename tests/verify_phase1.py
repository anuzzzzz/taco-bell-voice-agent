#!/usr/bin/env python3
"""Verify Phase 1 components are working"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice_pipeline import VoicePipeline
from colorama import init, Fore
import time

init(autoreset=True)

def verify_phase1():
    """Run all Phase 1 verification tests"""
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}PHASE 1 VERIFICATION - Voice Pipeline")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    results = []
    
    # Test 1: Initialize Pipeline
    print(f"{Fore.YELLOW}Test 1: Pipeline Initialization...")
    try:
        pipeline = VoicePipeline(model_size="tiny")  # Using tiny for quick test
        results.append(("Pipeline Init", True))
        print(f"{Fore.GREEN}✓ Pipeline initialized\n")
    except Exception as e:
        results.append(("Pipeline Init", False))
        print(f"{Fore.RED}✗ Failed: {e}\n")
        return results
    
    # Test 2: TTS Working
    print(f"{Fore.YELLOW}Test 2: Text-to-Speech...")
    try:
        pipeline.speak("Testing TTS system")
        results.append(("TTS", True))
        print(f"{Fore.GREEN}✓ TTS working\n")
    except Exception as e:
        results.append(("TTS", False))
        print(f"{Fore.RED}✗ Failed: {e}\n")
    
    # Test 3: Audio Recording
    print(f"{Fore.YELLOW}Test 3: Audio Recording...")
    print(f"{Fore.CYAN}Say 'Testing' when you hear the beep")
    time.sleep(1)
    
    try:
        text, confidence = pipeline.process_voice_input()
        if text:
            results.append(("Recording", True))
            results.append(("ASR", True))
            print(f"{Fore.GREEN}✓ Recording works")
            print(f"{Fore.GREEN}✓ ASR works: '{text}' (confidence: {confidence:.2%})\n")
        else:
            results.append(("Recording", True))
            results.append(("ASR", False))
            print(f"{Fore.YELLOW}⚠ Recording works but no transcription\n")
    except Exception as e:
        results.append(("Recording", False))
        results.append(("ASR", False))
        print(f"{Fore.RED}✗ Failed: {e}\n")
    
    # Test 4: Complete Pipeline
    print(f"{Fore.YELLOW}Test 4: Complete Pipeline Test...")
    try:
        pipeline.speak("Please say: I want two tacos")
        text, confidence = pipeline.process_voice_input()
        
        if text and confidence > 0.5:
            results.append(("Full Pipeline", True))
            pipeline.speak(f"Great! I heard: {text}")
            print(f"{Fore.GREEN}✓ Full pipeline working!\n")
        else:
            results.append(("Full Pipeline", False))
            print(f"{Fore.YELLOW}⚠ Pipeline works but low confidence\n")
    except Exception as e:
        results.append(("Full Pipeline", False))
        print(f"{Fore.RED}✗ Failed: {e}\n")
    
    # Print Summary
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}PHASE 1 VERIFICATION RESULTS")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    for test_name, passed in results:
        status = f"{Fore.GREEN}✓ PASS" if passed else f"{Fore.RED}✗ FAIL"
        print(f"{test_name:20} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}PHASE 1 COMPLETE! Ready for Phase 2")
        print(f"{Fore.GREEN}{'='*60}")
    else:
        print(f"\n{Fore.YELLOW}Some tests failed. Check issues above.")
    
    return results

if __name__ == "__main__":
    results = verify_phase1()