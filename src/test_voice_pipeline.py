import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice_pipeline import VoicePipeline
from colorama import init, Fore, Style
import time

init(autoreset=True)

def test_basic_pipeline():
    """Test basic voice pipeline functionality"""
    print(f"{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}VOICE PIPELINE TEST")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    # Initialize pipeline
    pipeline = VoicePipeline(model_size="base")  # Use 'tiny' for faster testing
    
    # Test TTS
    print(f"\n{Fore.YELLOW}Testing Text-to-Speech...")
    pipeline.speak("Welcome to Taco Bell! May I take your order?")
    time.sleep(1)
    
    # Test ASR
    print(f"\n{Fore.YELLOW}Testing Speech Recognition...")
    print(f"{Fore.CYAN}Try saying something like: 'I want two tacos'")
    
    text, confidence = pipeline.process_voice_input()
    
    if text:
        print(f"\n{Fore.GREEN}✓ Success!")
        print(f"  Transcription: {text}")
        print(f"  Confidence: {confidence:.2%}")
        
        # Echo back what was heard
        pipeline.speak(f"I heard you say: {text}")
    else:
        print(f"\n{Fore.RED}✗ No transcription received")

def test_continuous_conversation():
    """Test continuous conversation loop"""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}CONTINUOUS CONVERSATION TEST")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    pipeline = VoicePipeline(model_size="base")
    
    pipeline.speak("Welcome to Taco Bell drive-thru!")
    
    for i in range(3):
        print(f"\n{Fore.YELLOW}Round {i+1}/3")
        text, confidence = pipeline.process_voice_input()
        
        if text:
            # Simple echo response for now
            response = f"You said: {text}. Anything else?"
            pipeline.speak(response)
        else:
            pipeline.speak("I didn't catch that. Could you repeat?")
    
    pipeline.speak("Thank you for testing!")

def test_performance():
    """Test pipeline performance metrics"""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}PERFORMANCE TEST")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    import time
    
    pipeline = VoicePipeline(model_size="tiny")  # Use tiny for speed test
    
    # Warm-up
    pipeline.transcribe_audio("tests/sample_audio.wav")  # You'll need to create this
    
    # Test transcription speed
    start = time.time()
    text, conf = pipeline.process_voice_input()
    end = time.time()
    
    print(f"\n{Fore.GREEN}Performance Metrics:")
    print(f"  Total processing time: {end-start:.2f}s")
    print(f"  Transcription: {text}")
    print(f"  Confidence: {conf:.2%}")

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}\n🚀 Starting Voice Pipeline Tests\n")
    
    # Run tests
    test_basic_pipeline()
    
    # Optional: Uncomment to test continuous conversation
    # test_continuous_conversation()
    
    print(f"\n{Fore.MAGENTA}✓ Tests completed!")