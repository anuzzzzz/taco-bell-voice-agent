Demo:
# 🤖 Taco Bell Voice Agent

[![Demo Video](https://img.shields.io/badge/▶️-Watch%20Demo-red?style=for-the-badge)](https://drive.google.com/file/d/1Af7CGjDUn8tH5ZHo4JSH-6UEsHCW-IqG/view?usp=sharing)

An AI-powered voice ordering system that automates drive-thru conversations using Whisper ASR, GPT-3.5, and semantic search.



[rest of your existing README]


# 🌮 Taco Bell Voice Agent

An AI-powered voice assistant for drive-thru ordering that actually works. Built with GPT-3.5, Whisper, and a semantic search system over the menu.

## What This Does

Think drive-thru ordering but with AI. You talk to it, it understands what you want, finds items on the menu, and takes your order. Built this over a few days to learn about voice AI and LLM integration.

**Main features:**
- Voice input using Whisper (speech-to-text)
- Intent detection with GPT-3.5
- Smart menu search using embeddings
- Conversation state tracking
- Natural-sounding responses
- Error recovery when things go wrong

## Why I Built This

Wanted to get hands-on with:
- LLM prompt engineering
- RAG (Retrieval-Augmented Generation) systems
- Voice AI pipelines
- Production-level error handling
- Building something that feels real, not just a demo

## Quick Start

**Requirements:**
- Python 3.11+
- OpenAI API key
- Microphone (for voice mode)

**Setup:**
```bash
# Clone and install
git clone https://github.com/yourusername/taco-bell-voice-agent.git
cd taco-bell-voice-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your-key-here

# Test it works
python tests/test_phase7_integration.py
```

**Run it:**
```bash
# Text mode (easier for testing)
python main.py --text-only

# Full voice mode
python main.py

# Quick demo
python run_demo.py
```

## Example Conversation

```
Agent: What's up! Late night cravings? We got you.
You: I want two crunchy tacos
Agent: Added 2 Crunchy Tacos. Want a Baja Blast for $2.29?
You: Sure
Agent: Added Baja Blast. Anything else?
You: No lettuce on the tacos
Agent: Got it, no lettuce. Anything else?
You: That's all
Agent: Your order:
  • 2x Crunchy Taco (no lettuce) - $2.98
  • 1x Baja Blast - $2.29
Total: $5.27
Is that correct?
You: Yes
Agent: $5.27 total. Pull forward!
```

## How It Works

```
┌─────────────┐
│ Your Voice  │
└──────┬──────┘
       │
┌──────▼──────┐
│   Whisper   │ (speech → text)
└──────┬──────┘
       │
┌──────▼──────┐
│   GPT-3.5   │ (what do they want?)
└──────┬──────┘
       │
┌──────▼──────┐
│ Conversation│ (track order, state)
│   Manager   │
└──┬────────┬─┘
   │        │
┌──▼──┐  ┌─▼────┐
│Menu │  │Brain │ (generate response)
│ RAG │  │Voice │
└─────┘  └───┬──┘
             │
     ┌───────▼────┐
     │  Speaker   │
     └────────────┘
```

**Key Components:**

1. **Voice Pipeline** - Whisper for transcription, pyttsx3 for speech
2. **Intent Detection** - GPT-3.5 figures out what you're asking for
3. **Menu RAG** - Semantic search finds items even with typos
4. **Conversation Manager** - Tracks state, handles modifications
5. **Response Generator** - Makes it sound natural, not robotic
6. **Error Handler** - Recovers from mishears and confusion

## Project Structure

```
taco-bell-voice-agent/
├── main.py                         # Entry point
├── run_demo.py                     # Automated demo
├── src/
│   ├── voice_pipeline.py           # Whisper + TTS
│   ├── intent_detector_llm.py      # GPT-3.5 intent detection
│   ├── menu_rag.py                 # Semantic menu search
│   ├── conversation_manager_v2.py  # State machine + context
│   ├── response_generator.py       # Brand voice responses
│   ├── brand_voice.py              # Personality config
│   └── error_handler.py            # Recovery system
├── tests/
│   └── test_phase7_integration.py  # All 8 tests
└── data/
    └── menu_embeddings_v2.pkl      # Cached embeddings
```

## Testing

All tests pass (8/8):
```bash
python tests/test_phase7_integration.py
```

Tests cover:
- ✅ Initialization
- ✅ Simple orders
- ✅ Complex orders with modifications
- ✅ Error recovery
- ✅ Menu search
- ✅ Performance (< 2s per turn)
- ✅ Logging
- ✅ Stress test (10 conversations)

## Tech Stack

- **Python 3.11** - Main language
- **OpenAI GPT-3.5** - Intent detection & responses
- **Whisper** - Speech recognition
- **sentence-transformers** - Menu embeddings
- **PyTorch** - ML backend
- **pyttsx3** - Text-to-speech

## Configuration

The system is pretty flexible:

```bash
# Text-only mode
python main.py --text-only

# Different Whisper models (tiny/base/small/medium)
python main.py --whisper-model small

# No logging
python main.py --no-logging

# Single conversation
python main.py --text-only --single-conversation
```

## Performance

Tested on M2 Pro, 16GB RAM:
- Response time: ~1s per turn
- ASR confidence: 92-99%
- Intent accuracy: 95%+
- Test pass rate: 100%

## What I Learned

**Technical:**
- How to chain LLM calls effectively
- RAG system design and implementation
- Voice pipeline integration
- State machine conversation management
- Handling real-world errors gracefully

**Practical:**
- Testing matters - caught so many edge cases
- Error handling is like 30% of the code
- Prompt engineering is an art
- Voice AI is harder than text (mishears are brutal)

## Known Issues

- Whisper sometimes mishears words (especially with background noise)
- Menu is limited to 16 items (subset of full Taco Bell menu)
- Complex modifications can confuse it
- No actual payment processing (obviously)

## Future Ideas

If I keep working on this:
- [ ] Expand menu to full catalog
- [ ] Better conversation repair for complex scenarios
- [ ] Multi-language support
- [ ] Voice activity detection improvements
- [ ] Customer preference memory
- [ ] Fine-tune Whisper on restaurant audio

## Setup Issues?

Check `SETUP.md` for detailed installation help.

Common fixes:
- **PyAudio won't install**: `brew install portaudio` on Mac
- **Whisper slow**: First run downloads models (~150MB)
- **Mic not working**: Check system permissions
- **API errors**: Verify your OpenAI key and credits

## What This Demonstrates

Skills I built/used:
- LLM engineering and prompt design
- Voice AI integration
- RAG system implementation
- Conversation design
- Error handling strategies
- Test-driven development
- Production-ready logging

## Contributing

Feel free to open issues or PRs. See `CONTRIBUTING.md` for guidelines.

## Development Timeline

Built this incrementally:
- Phase 1: Voice pipeline
- Phase 2: Intent detection
- Phase 3: Menu RAG system
- Phase 4: Conversation flow
- Phase 5: Brand voice
- Phase 6: Error handling
- Phase 7: Integration + testing

Total time: ~3 days of focused work

---

Built this to learn about voice AI and LLM systems. Not affiliated with Taco Bell.

If you found this helpful, star the repo!
