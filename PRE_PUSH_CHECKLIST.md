# Pre-Push Checklist ✅

Before you push, verify these items:

## Security (CRITICAL!)

- [ ] `.env` file is NOT in the commit
- [ ] Run: `git status` and confirm `.env` is not listed
- [ ] Run: `git diff --cached` and confirm no API keys visible
- [ ] `logs/` directory is ignored
- [ ] No `*.pkl` files being committed

Quick check:
```bash
git status | grep -E "\.env$|logs/|api_key"
# Should be empty or show ".env" under "Untracked files" or ignored
```

## Documentation

- [ ] README.md is updated
- [ ] SETUP.md exists
- [ ] CONTRIBUTING.md exists
- [ ] .env.example exists (but NOT .env)

## Code Quality

- [ ] All tests pass: `python tests/test_phase7_integration.py`
- [ ] No syntax errors: `python -m py_compile main.py`
- [ ] No obvious bugs

## Files to Commit

Should see these:
```
modified:   .env.example
modified:   README.md
new file:   CONTRIBUTING.md
new file:   GIT_COMMANDS.md
new file:   PUSH_TO_GITHUB.md
new file:   SETUP.md
new file:   data/.gitkeep
```

## Should NOT Commit

These should be ignored:
```
.env
logs/
__pycache__/
*.pkl (except maybe empty ones)
venv/
*.pyc
.DS_Store
```

## Final Commands

```bash
# 1. Check status
git status

# 2. Verify no secrets
git diff --cached | grep -i "sk-proj"  # Should be empty

# 3. Add files
git add .

# 4. Commit
git commit -m "Update documentation and setup files

- Rewrote README with authentic student voice
- Added comprehensive SETUP.md guide
- Added CONTRIBUTING.md for contributors
- Created .env.example template
- Added git command references
- All tests passing (8/8)
- Security: No API keys or secrets committed"

# 5. Push
git push origin main
```

## After Push

Visit your repo and check:

- [ ] README displays nicely
- [ ] No .env file visible
- [ ] All code files present
- [ ] Tests folder visible

## If Something Goes Wrong

**Committed .env by accident:**
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
git push -f origin main
```

**Want to undo last commit:**
```bash
git reset --soft HEAD~1
# Make changes
git commit -m "Fixed commit message"
```

---

✅ All checks passed? Go ahead and push!
