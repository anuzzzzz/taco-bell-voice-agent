# Setup Guide

Getting this running is pretty straightforward. Here's what you need to do.

## Prerequisites

- **Python 3.11+** (check with `python --version`)
- **16GB RAM** recommended (works with less but Whisper likes RAM)
- **Microphone** if you want voice mode
- **OpenAI API key** (you'll need credits, maybe $2-3 for testing)
- **macOS or Linux** (tested on M2 Pro Mac, should work on Linux)

## Installation Steps

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/taco-bell-voice-agent.git
cd taco-bell-voice-agent
```

### 2. Set Up Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or on Windows: venv\Scripts\activate

# Upgrade pip (always do this)
pip install --upgrade pip
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- openai (for GPT-3.5 and Whisper)
- sentence-transformers (for menu embeddings)
- torch (ML backend)
- pyttsx3 (text-to-speech)
- pyaudio (microphone input)
- colorama (pretty terminal output)
- other stuff

**Note:** First install might take a few minutes. PyTorch is kinda big.

### 4. Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in (or create account)
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. Make sure you have some credits - check https://platform.openai.com/usage

### 5. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit it (use nano, vim, or any editor)
nano .env
```

Add your key:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

Save and exit.

### 6. Test It Works

```bash
python tests/test_phase7_integration.py
```

Should see all green checkmarks and end with:
```
🎉 ALL TESTS PASSED! MVP COMPLETE!
```

If that works, you're good to go!

### 7. Run Your First Conversation

Start in text mode (easier for first time):
```bash
python main.py --text-only
```

Select option 1, then try:
- "Hi"
- "I want two tacos"
- "That's all"
- "Yes"

## Common Issues

### PyAudio Installation Fails

**On macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**On Windows:**
Download the wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install it.

### Whisper Models Download Slowly

First run downloads the Whisper model (~150MB for base model). It's cached in `~/.cache/whisper/` so only happens once.

If it's too slow, use the tiny model:
```bash
python main.py --text-only --whisper-model tiny
```

### Microphone Not Working

**macOS:**
1. System Preferences → Security & Privacy → Privacy → Microphone
2. Make sure Terminal (or your terminal app) has access

**Linux:**
Check `pavucontrol` for input device settings.

### OpenAI API Errors

**"Invalid API Key":**
- Double-check the key in `.env`
- Make sure no extra spaces
- Key should start with `sk-proj-` or `sk-`

**"Rate limit exceeded":**
- You're making too many requests
- Wait a minute or use a paid account

**"Insufficient quota":**
- You're out of credits
- Add credits at https://platform.openai.com/account/billing

### Import Errors

If you see `ImportError` or `ModuleNotFoundError`:
```bash
# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Tests Failing

If integration tests fail:
1. Check your API key is set
2. Make sure you have internet
3. Try running individual test files to isolate the issue

## Next Steps

Once it's working:

1. **Try voice mode:**
   ```bash
   python main.py
   ```

2. **Run the demo:**
   ```bash
   python run_demo.py
   ```

3. **Explore the code:**
   - Start with `main.py`
   - Check out `src/conversation_manager_v2.py`
   - Look at the tests to see examples

4. **Check the logs:**
   ```bash
   ls logs/
   cat logs/session_*.json
   ```

## Development Setup

If you want to modify the code:

```bash
# Install dev dependencies (if any)
pip install pytest black flake8

# Format code
black src/ tests/

# Check style
flake8 src/ tests/
```

## Troubleshooting Tips

**Still stuck?**

1. Check Python version: `python --version` (need 3.11+)
2. Make sure venv is activated: you should see `(venv)` in your prompt
3. Try reinstalling: delete `venv/` and start over
4. Check the GitHub issues page

**Need help?**
Open an issue on GitHub with:
- Your Python version
- Operating system
- Full error message
- What you were trying to do

## System Requirements

**Minimum:**
- Python 3.11
- 8GB RAM
- 2GB disk space
- Internet connection

**Recommended:**
- Python 3.11+
- 16GB RAM
- SSD storage
- Quiet environment for voice mode

## What Gets Downloaded

First run downloads:
- Whisper model (~150MB for base)
- Sentence transformer model (~80MB)
- Some Python packages

Total: ~500MB-1GB depending on models

All cached locally so only happens once.

---

That's it! If everything installed correctly, you should be good to go. Start with `python main.py --text-only` to test things out.
