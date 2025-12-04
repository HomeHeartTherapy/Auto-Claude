# Auto-Build Framework

A production-ready framework for autonomous multi-session AI coding. Build complete applications or add features to existing projects through coordinated AI agent sessions.

## What It Does

Auto-Build uses a **three-agent pattern** to build software autonomously:

1. **Spec Agent** (`claude /spec`) - Interactive questionnaire to create a detailed specification
2. **Initializer Agent** (Session 1) - Analyzes spec, generates test plan, sets up project
3. **Coding Agent** (Sessions 2+) - Implements features one-by-one until all tests pass

Each session runs with a fresh context window. Progress is tracked via `feature_list.json` and Git commits.

## Quick Start

### Prerequisites

- Python 3.8+
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)
- Claude Code OAuth token (run `claude setup-token`)

### Setup

```bash
# 1. Set your OAuth token
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'

# 2. Create a spec interactively (also sets up Python environment)

You have two options:

**Option 1:** Using Claude Code CLI in terminal

```bash
# Start Claude Code
claude

# Then write:
/spec "whatever you want to create"
```

**Option 2:** Using your favorite IDE (like Cursor)

Open your IDE's AI agent chat and write:

```
/spec "whatever you want to create"
```

The spec agent will guide you through creating a detailed specification and set up the Python environment automatically.

# 3. Activate the virtual environment
source auto-build/.venv/bin/activate

# 4. Run the autonomous build
python auto-build/run.py --spec 001
```

### Managing Specs

```bash
# List all specs and their status
python auto-build/run.py --list

# Run a specific spec
python auto-build/run.py --spec 001
python auto-build/run.py --spec 001-feature-name

# Limit iterations for testing
python auto-build/run.py --spec 001 --max-iterations 5
```

### Interactive Controls

While the agent is running, you can:

```bash
# Pause and optionally add instructions
Ctrl+C (once)
# You'll be prompted to add instructions for the agent
# The agent will read these instructions when you resume

# Exit immediately without prompting
Ctrl+C (twice)
# Press Ctrl+C again during the prompt to exit
```

**Alternative (file-based):**
```bash
# Create PAUSE file to pause after current session
touch auto-build/specs/001-name/PAUSE

# Manually edit instructions file
echo "Focus on fixing the login bug first" > auto-build/specs/001-name/HUMAN_INPUT.md
```

## Project Structure

```
your-project/
├── .claude/commands/
│   └── spec.md              # Interactive spec creation
├── auto-build/
│   ├── run.py               # Entry point
│   ├── agent.py             # Session orchestration
│   ├── client.py            # Claude SDK configuration
│   ├── prompts/
│   │   ├── initializer.md   # Session 1 agent
│   │   └── coder.md         # Sessions 2+ agent
│   └── specs/
│       └── 001-feature/     # Each spec in its own folder
│           ├── spec.md
│           ├── feature_list.json
│           └── progress.txt
└── [your project files]
```

## Key Features

- **Domain Agnostic**: Works for any software project (web apps, APIs, CLIs, etc.)
- **Multi-Session**: Unlimited sessions, each with fresh context
- **Self-Verifying**: Agents test their work with browser automation before marking complete
- **Fix Bugs Immediately**: Agents fix discovered bugs in the same session, not later
- **Defense-in-Depth Security**: OS sandbox, filesystem restrictions, command allowlist
- **Human Intervention**: Pause, add instructions, or stop at any time
- **Multiple Specs**: Track and run multiple specifications independently

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Yes | OAuth token from `claude setup-token` |
| `AUTO_BUILD_MODEL` | No | Model override (default: claude-opus-4-5-20251101) |

## Documentation

For complete documentation including:
- Detailed architecture diagrams
- Agent prompt specifications
- Security model details
- Configuration options
- Troubleshooting guide

See [AUTO-BUILD-FRAMEWORK.md](AUTO-BUILD-FRAMEWORK.md)

## Acknowledgments

This framework was inspired by Anthropic's [Autonomous Coding Agent](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding). Thank you to the Anthropic team for their innovative work on autonomous coding systems.

## License

MIT License
