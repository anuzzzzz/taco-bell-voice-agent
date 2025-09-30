# Quick Git Commands

Here's what you need to push this to GitHub.

## First Time Setup

### 1. Check what will be committed
```bash
git status
```

Should NOT see:
- `.env` (only `.env.example`)
- `logs/` directory
- `__pycache__/`
- Any API keys

### 2. Initialize Git (if not done)
```bash
# Check if already initialized
git status

# If not, initialize
git init
git branch -M main
```

### 3. Add all files
```bash
git add .
```

### 4. Make first commit
```bash
git commit -m "Initial commit: Taco Bell Voice Agent MVP

Complete AI voice assistant for drive-thru ordering.

Features:
- Whisper ASR for speech recognition
- GPT-3.5 for intent detection and responses
- RAG-powered menu search with embeddings
- State-based conversation management
- Error handling and recovery
- Comprehensive test suite (8/8 passing)

Tech stack: Python, OpenAI APIs, sentence-transformers, PyTorch

Built in 3 days as a learning project."
```

## Push to GitHub

### Option 1: Using GitHub Website

1. Go to https://github.com/new
2. Repository name: `taco-bell-voice-agent`
3. Description: `AI voice agent for drive-thru ordering - GPT-3.5, Whisper, RAG`
4. Choose Public or Private
5. **Don't** check "Initialize with README" (you already have one)
6. Click "Create repository"

7. Then run these commands:
```bash
git remote add origin https://github.com/YOUR-USERNAME/taco-bell-voice-agent.git
git push -u origin main
```

### Option 2: Using GitHub CLI

```bash
# Install gh if you don't have it
brew install gh  # macOS
# sudo apt install gh  # Linux

# Login
gh auth login

# Create and push (public)
gh repo create taco-bell-voice-agent --public --source=. --remote=origin --push

# Or private
gh repo create taco-bell-voice-agent --private --source=. --remote=origin --push
```

## After First Push

### Check it worked
Visit: https://github.com/YOUR-USERNAME/taco-bell-voice-agent

Should see:
- ✅ README.md displayed nicely
- ✅ All source files
- ✅ Tests folder
- ✅ .env.example (but NOT .env)

### Add topics/tags on GitHub
Go to your repo → Click ⚙️ next to "About" → Add topics:
```
ai, voice-agent, gpt-3, whisper, nlp, chatbot, rag, llm, speech-recognition, python
```

## Making Updates Later

```bash
# Check what changed
git status

# Add changes
git add .

# Commit
git commit -m "Description of what you changed"

# Push
git push
```

## Create a Release

```bash
# Tag version
git tag -a v1.0.0 -m "v1.0.0 - Initial MVP Release"

# Push tag
git push origin v1.0.0
```

Then on GitHub:
- Go to "Releases" tab
- Click "Draft a new release"
- Select tag `v1.0.0`
- Add release notes
- Publish

## Troubleshooting

**"Repository not found":**
- Make sure you created the repo on GitHub
- Check the remote URL: `git remote -v`

**".env file in commit":**
```bash
# Remove it from git (but keep local copy)
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

**Large files error:**
- Check you didn't commit model files
- They should be in .gitignore

**Merge conflicts:**
```bash
# If you edited on GitHub and locally
git pull --rebase
# Fix conflicts
git add .
git rebase --continue
git push
```

## Useful Commands

```bash
# See commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See what's ignored
git status --ignored

# Check remote
git remote -v

# See all branches
git branch -a
```

---

That's it! Once you push, your repo is live.
