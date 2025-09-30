# Contributing

Thanks for checking this out! If you want to contribute, here's how.

## Found a Bug?

Open an issue with:
- What you were doing
- What happened
- What you expected to happen
- Error messages (if any)
- Your Python version and OS

## Want to Add a Feature?

Cool! Here's the process:

1. **Open an issue first** - let's discuss if it fits the project
2. **Fork the repo**
3. **Make your changes**
4. **Test everything**
5. **Submit a PR**

## Code Guidelines

Keep it clean and readable:

- **Follow PEP 8** - use `black` for formatting
- **Add docstrings** - explain what functions do
- **Type hints** - use them where it makes sense
- **Keep functions small** - under 50 lines ideally
- **Comment tricky parts** - explain the "why", not the "what"

Example:
```python
def process_order(order: Order, customer_id: str) -> OrderResult:
    """
    Process a customer order and update inventory.

    Args:
        order: The order to process
        customer_id: Unique customer identifier

    Returns:
        OrderResult with status and total
    """
    # Use atomic transaction to prevent race conditions
    with transaction():
        result = validate_and_charge(order)
        update_inventory(order.items)
    return result
```

## Testing

**All PRs must pass the test suite:**
```bash
python tests/test_phase7_integration.py
```

If you add new features, add tests for them.

## Commit Messages

Write clear commit messages:

**Good:**
```
Add support for combo meals

- Added combo meal detection in intent parser
- Updated menu RAG with combo items
- Added tests for combo ordering flow
```

**Not great:**
```
fixed stuff
```

## Pull Request Process

1. **Fork** the repo
2. **Create a branch**: `git checkout -b feature/cool-new-thing`
3. **Make changes** and commit
4. **Push** to your fork
5. **Open a PR** with:
   - What you changed
   - Why you changed it
   - How to test it

## What to Contribute

Some ideas:

### Easy
- [ ] Fix typos in documentation
- [ ] Add more test cases
- [ ] Improve error messages
- [ ] Add menu items

### Medium
- [ ] Better conversation repair
- [ ] Spanish language support
- [ ] Improved voice activity detection
- [ ] Performance optimizations

### Hard
- [ ] Fine-tune Whisper on restaurant audio
- [ ] Custom wake word detection
- [ ] Multi-location menu support
- [ ] Real-time order tracking

## Code Review

PRs will be reviewed for:
- Code quality
- Test coverage
- Documentation
- Performance impact
- Breaking changes

Be patient - might take a few days.

## Questions?

Not sure about something? Just ask! Open an issue or reach out.

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/taco-bell-voice-agent.git
cd taco-bell-voice-agent

# Set up upstream
git remote add upstream https://github.com/ORIGINAL-OWNER/taco-bell-voice-agent.git

# Create venv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev tools
pip install black flake8 pytest

# Make a branch
git checkout -b feature/my-cool-feature

# Make changes, commit, push
git add .
git commit -m "Add cool feature"
git push origin feature/my-cool-feature
```

## Style Guide

**Python:**
- Use `black` for formatting: `black src/ tests/`
- Max line length: 100 characters
- Use type hints
- Prefer f-strings over `.format()`

**Documentation:**
- Use Markdown
- Keep lines under 100 chars
- Use code blocks with language tags

**Naming:**
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

## License

By contributing, you agree that your contributions will be available under the same terms as the project.

## Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Given credit in commit history

## Thanks!

Appreciate you taking the time to contribute. Even small improvements help!
