# Contributing to Discord Music Bot

First off, thank you for considering contributing to Discord Music Bot! It's people like you that make this project better.

## Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. Please be kind and courteous to others.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

**When reporting bugs, include:**
- Clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please:
- Use a clear and descriptive title
- Provide detailed description of the feature
- Explain why this feature would be useful
- Include examples if possible

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/your-username/discord-music-bot.git
cd discord-music-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your test bot token

4. Make your changes

5. Test thoroughly

## Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Code Organization
- Keep related code in appropriate modules
- Don't mix concerns
- Maintain the modular structure

### Comments
- Write clear comments for complex logic
- Update comments when changing code
- Use docstrings for functions and classes

## Testing

Before submitting a PR:
- Test all existing commands still work
- Test your new feature thoroughly
- Test on multiple servers if possible
- Check for any error messages

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

Examples:
```
Add shuffle command
Fix queue display bug
Update documentation for playlists
```

## Project Structure

```
discord-music-bot/
├── bot.py                  # Main bot file
├── config.py               # Configuration
├── music_player.py         # Playback logic
├── music_sources.py        # YouTube/Spotify
├── playlist_manager.py     # Playlist management
├── docs/                   # Documentation
└── playlists/              # Saved playlists
```

## Adding New Features

### Adding a New Command

1. Add the command function in `bot.py`:
```python
@bot.command(name='mycommand')
async def my_command(ctx, arg):
    """Command description"""
    # Your code here
    await ctx.send('Response')
```

2. Update documentation in `docs/COMMANDS.md`

3. Add examples in `docs/EXAMPLES.md`

4. Test the command

### Adding a New Music Source

1. Add source logic in `music_sources.py`

2. Update `search_song()` function

3. Update documentation

4. Test thoroughly

## Documentation

When adding features:
- Update README.md if needed
- Update relevant docs in `docs/`
- Add examples
- Update CHANGELOG.md

## Questions?

Feel free to open an issue with your question!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎵
