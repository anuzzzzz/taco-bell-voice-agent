import whisper
import pyaudio
import wave
import numpy as np
import time
import os
from typing import Optional, Tuple
import torch
from pathlib import Path
import pyttsx3
from colorama import init, Fore, Style

init(autoreset=True)

class VoicePipeline:
    """Basic voice input/output pipeline for drive-thru system"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize voice pipeline with Whisper ASR
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       For M2 Pro 16GB, 'base' or 'small' recommended
        """
        print(f"{Fore.YELLOW}Initializing Voice Pipeline...")
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5  # Max recording time
        self.SILENCE_THRESHOLD = 500  # Adjust based on testing
        
        # Initialize Whisper
        # Note: MPS has compatibility issues with Whisper, use CPU for now
        device = "cpu"  # Force CPU for compatibility
        print(f"{Fore.CYAN}Loading Whisper model '{model_size}' on {device}...")
        self.whisper_model = whisper.load_model(model_size, device=device)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)  # Speed
        self.tts_engine.setProperty('volume', 0.9)
        
        print(f"{Fore.GREEN}✓ Voice Pipeline initialized successfully!")
    
    def detect_silence(self, audio_chunk: bytes, threshold: int = 500) -> bool:
        """Detect if audio chunk contains silence"""
        audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
        return np.max(np.abs(audio_data)) < threshold
    
    def record_audio(self, output_file: str = "temp_recording.wav") -> str:
        """
        Record audio from microphone with silence detection
        
        Returns:
            Path to recorded audio file
        """
        print(f"{Fore.YELLOW}🎤 Listening... (speak now)")
        
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        frames = []
        silence_chunks = 0
        max_silence_chunks = 30  # ~1 second of silence
        recording = False
        
        try:
            for _ in range(int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                
                if not self.detect_silence(data, self.SILENCE_THRESHOLD):
                    recording = True
                    silence_chunks = 0
                    frames.append(data)
                elif recording:
                    silence_chunks += 1
                    frames.append(data)
                    
                    if silence_chunks > max_silence_chunks:
                        print(f"{Fore.GREEN}✓ Recording complete (silence detected)")
                        break
        except KeyboardInterrupt:
            print(f"{Fore.RED}Recording interrupted")
        finally:
            stream.stop_stream()
            stream.close()
        
        # Save recording
        if frames:
            wf = wave.open(output_file, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return output_file
        return None
    
    def transcribe_audio(self, audio_file: str) -> Tuple[str, float]:
        """
        Transcribe audio file using Whisper
        
        Returns:
            Tuple of (transcription, confidence_score)
        """
        if not audio_file or not os.path.exists(audio_file):
            return "", 0.0
        
        print(f"{Fore.CYAN}Transcribing audio...")
        
        # Transcribe with Whisper
        result = self.whisper_model.transcribe(
            audio_file, 
            language='en',
            task='transcribe',
            temperature=0.2,  # Lower temperature for more consistent results
            no_speech_threshold=0.3
        )
        
        # Extract text and calculate confidence
        transcription = result.get('text', '').strip()
        
        # Simple confidence calculation based on no_speech_prob
        segments = result.get('segments', [])
        if segments:
            avg_no_speech = np.mean([s.get('no_speech_prob', 0) for s in segments])
            confidence = 1.0 - avg_no_speech
        else:
            confidence = 0.0
        
        return transcription, confidence
    
    def speak(self, text: str):
        """Convert text to speech"""
        print(f"{Fore.MAGENTA}🔊 Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def process_voice_input(self) -> Tuple[str, float]:
        """
        Complete pipeline: record -> transcribe -> return text
        
        Returns:
            Tuple of (transcribed_text, confidence)
        """
        # Record audio
        audio_file = self.record_audio()
        
        if not audio_file:
            return "", 0.0
        
        # Transcribe
        text, confidence = self.transcribe_audio(audio_file)
        
        # Clean up temp file
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        if text:
            print(f"{Fore.GREEN}📝 Heard: '{text}' (confidence: {confidence:.2f})")
        else:
            print(f"{Fore.RED}❌ Could not understand audio")
        
        return text, confidence
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'audio'):
            self.audio.terminate()