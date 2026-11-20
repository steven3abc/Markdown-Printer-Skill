# Markdown Printer Skill

Markdown Printer Skill converts Markdown files into cleanly formatted A4 technical PDF documents—complete with an automatic cover page, running header titles, page numbers, GitHub-style alerts, tables, and code blocks. Built to follow the [Agent Skills](https://agentskills.io) specification, it works seamlessly with AI agents such as Claude Code, Codex, Gemini CLI, Cursor, and GitHub Copilot. Once installed, simply ask your agent to "convert this Markdown file to PDF." It can also be run standalone via a graphical interface (GUI) or the command line (CLI).

> **Looking for more?** Check out [**Markdown Printer Premium**](https://www.agensi.io/skills/markdown-printer-premium) ($1 on Agensi) for corporate & technical layouts, syntax highlighting, table of contents with page numbers, and custom page watermarks.

## Features

- A4 page layout with document title in the header and page numbers in the footer (omitted on the cover page)
- 7 built-in cover color themes, plus a random harmonious palette generator
- Supports GitHub-style alert callouts: `> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, and `[!CAUTION]`
- Supports tables, fenced code blocks, footnotes, definition lists, and `[TOC]` table of contents
- Resolves relative image paths from the Markdown file's directory and automatically downloads remote images
- Supports custom CSS files to override default styles
- Preconfigured typography for both CJK and Latin scripts (prioritizing Noto Sans TC and Microsoft JhengHei for Traditional Chinese)

## Upgrade to Markdown Printer Premium

Need publication-grade styling for client reports, technical specifications, or internal documentation? Upgrade to **[Markdown Printer Premium](https://www.agensi.io/skills/markdown-printer-premium)**—available for **$1** on Agensi (one-time purchase with Stripe checkout and a money-back guarantee).

**What's included in Premium:**
- **Corporate & Technical Layouts:** Switch between specialized document layouts (such as the `tech` layout) tailored for professional reports and specs
- **Syntax Highlighting:** Clean, readable syntax highlighting for fenced code blocks
- **Table of Contents with Page Numbers:** Automatically generated TOC with accurate page numbering
- **Custom Watermarks:** Apply page-wide watermarks (e.g., `DRAFT`, `CONFIDENTIAL`) across body pages
- **Full Agent Compatibility:** Follows the `SKILL.md` standard and works out of the box with Claude Code, Cursor, Codex CLI, Gemini CLI, and 20+ other AI agents

👉 **[Get Markdown Printer Premium on Agensi ($1)](https://www.agensi.io/skills/markdown-printer-premium)**

## Installing the Skill

The skill lives in the [`skills/markdown-printer/`](skills/markdown-printer) directory, which contains `SKILL.md` (instructions for the AI agent) and `scripts/md_beautify.py` (the conversion script). To install it, place this folder into your agent's skills directory using any of the three methods below.

### Method 1: One-Click Install with skills CLI

If you have Node.js installed, the [skills CLI](https://github.com/vercel-labs/skills) automatically detects your installed agents and copies the skill to the right location:

```bash
npx skills add steven3abc/Markdown-Printer-Skill
```

Add `-g` to install globally in your user directory (available across all projects); omit it to install only in the current project. Use `-a` to target a specific agent, e.g., `-a claude-code`.

### Method 2: Manual Copy

First, clone the repository:

```bash
git clone https://github.com/steven3abc/Markdown-Printer-Skill.git
```

Then copy `skills/markdown-printer` into your agent's skills directory. For example, for Claude Code on macOS and Linux:

```bash
mkdir -p ~/.claude/skills && cp -r Markdown-Printer-Skill/skills/markdown-printer ~/.claude/skills/
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null; Copy-Item -Recurse Markdown-Printer-Skill\skills\markdown-printer "$HOME\.claude\skills\"
```

For other agents, replace the destination path using the table below. Skills in the **Personal** directory are available across all projects, while skills in the **Project** directory live at the project root and apply only to that repository (and can be committed to version control for your team).

| Agent | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/` | `.gemini/skills/` or `.agents/skills/` |
| Cursor | `~/.cursor/skills/` or `~/.agents/skills/` | `.cursor/skills/` or `.agents/skills/` |
| GitHub Copilot (VS Code) | `~/.copilot/skills/` | `.github/skills/` |

Since Codex, Gemini CLI, and Cursor all read from `~/.agents/skills/`, installing there once shares the skill across all three. Cursor also reads `~/.claude/skills/`, so if you have already installed it for Claude Code, you don't need to install it again. Paths may change across versions—refer to each tool's official documentation: [Claude Code](https://code.claude.com/docs/en/skills), [Codex](https://learn.chatgpt.com/docs/build-skills), [Gemini CLI](https://geminicli.com/docs/cli/skills/), [Cursor](https://cursor.com/docs/skills), and [VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills).

When developing or customizing this skill, you can create a link instead of copying so your edits take effect immediately. On Windows, use a directory junction (no administrator privileges required):

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\markdown-printer" -Target "<repo-path>\skills\markdown-printer"
```

On macOS and Linux, use a symlink:

```bash
ln -s "<repo-path>/skills/markdown-printer" ~/.claude/skills/markdown-printer
```

### Method 3: Built-in Agent Install Commands

Gemini CLI can install directly from GitHub:

```bash
gemini skills install https://github.com/steven3abc/Markdown-Printer-Skill.git --path skills/markdown-printer
```

Codex's built-in `$skill-installer` can also fetch skills from GitHub—simply run `$skill-installer` in Codex with `https://github.com/steven3abc/Markdown-Printer-Skill/tree/main/skills/markdown-printer`.

### claude.ai and Claude Desktop App

Chat in claude.ai and the Claude Desktop app requires uploading a `.zip` package. Run the following command from the repository root to generate `dist/markdown-printer.zip`:

```bash
python build_skill.py
```

Then go to **Settings → Capabilities → Skills** and upload the zip file. On claude.ai, the skill runs inside a cloud sandbox and automatically installs missing Python packages; however, if the sandbox lacks CJK fonts and cannot install `fonts-noto-cjk`, Chinese/Japanese/Korean characters may render as blank boxes.

### Verify Installation

After restarting your agent, most agents let you inspect loaded skills via `/skills`, and in Claude Code you can invoke it directly with `/markdown-printer`. From there, prompts like *"Convert notes.md to PDF"* or *"Export this Markdown file as a PDF with a cover page"* will trigger the skill. If no color theme is specified, a random theme is chosen.

## Requirements

Because the agent executes `scripts/md_beautify.py`, the host machine needs **Python 3.9+** along with the `markdown` and `weasyprint` packages. The agent runs `scripts/find_python.py` first to locate a working Python interpreter across `PATH` and conda environments. If you have multiple environments, you can specify one via the `MARKDOWN_PRINTER_PYTHON` environment variable.

This skill will not silently install packages into your local Python environment. On macOS and Linux, if [uv](https://docs.astral.sh/uv/) is available, the agent uses `uv run` to create an isolated environment; otherwise, it reports what is missing and asks for your confirmation before installing. Direct `pip` installation is only used inside ephemeral cloud sandboxes like claude.ai. To install dependencies manually upfront:

```bash
pip install -r requirements.txt
```

To verify that your environment can render PDFs properly, run:

```bash
python skills/markdown-printer/scripts/md_beautify.py --check
```

It will render a test PDF page and print `OK` when everything is ready.

[WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) also requires system libraries such as Pango:

- **Windows:** Installing via conda is recommended (`conda install -c conda-forge weasyprint`), which bundles GTK and Pango. On startup, the script prioritizes DLLs from the conda environment to avoid conflicts with older DLLs on `PATH`.
- **macOS:** `brew install pango`
- **Debian / Ubuntu:** `apt install libpango-1.0-0 libpangoft2-1.0-0` (plus `fonts-noto-cjk` for CJK documents)

## Standalone Usage (Without an Agent)

### Graphical Interface (GUI)

Run the script without arguments to launch the desktop GUI (on Windows, you can also double-click `run.bat`):

```bash
python skills/markdown-printer/scripts/md_beautify.py
```

Once you select a Markdown file, the output path and document title are filled in automatically. Adjust the cover details if needed and click **Start Conversion** to generate your PDF.

By default, `run.bat` launches `pythonw` from `PATH`. To point it to a specific Python installation (such as a conda environment), create a `run.local.bat` file in the same directory—`run.bat` will automatically delegate to it (and it is already ignored by `.gitignore`):

```bat
@echo off
start "" "C:\path\to\envs\myenv\pythonw.exe" "%~dp0skills\markdown-printer\scripts\md_beautify.py"
```

### Command Line (CLI)

```bash
python skills/markdown-printer/scripts/md_beautify.py examples/sample.md
python skills/markdown-printer/scripts/md_beautify.py notes.md -o out/notes.pdf -a "Jane Doe" -s "Internal Documentation" -c green
python skills/markdown-printer/scripts/md_beautify.py notes.md --no-cover --css my-style.css
```

| Option | Description | Default |
|---|---|---|
| `-o, --output` | Output PDF file path | Same name as input with `.pdf` extension |
| `-t, --title` | Document title (used on cover and header) | First H1 heading, or filename if none |
| `-s, --subtitle` | Cover page subtitle | `Official Documentation & Best Practices` |
| `-a, --author` | Cover page author | `Developer Team` |
| `--no-cover` | Disable the cover page | Cover page enabled |
| `-c, --cover-color` | Cover color theme | `blue` (`經典藍`) |
| `--css` | Path to a custom CSS override file | None |

Cover color themes accept either English aliases or Chinese names:

| English Alias | Chinese Name |
|---|---|
| `blue` | 經典藍 |
| `green` | 森林綠 |
| `orange` | 暖陽橙 |
| `rose` | 玫瑰紅 |
| `purple` | 優雅紫 |
| `graphite` | 石墨灰 |
| `midnight` | 深夜藍 |
| `random` | 隨機 |

When set to `random`, the script picks a hue and builds a coordinated palette automatically (with roughly a 25% chance of generating a dark cover).

### Python API

Add `skills/markdown-printer/scripts` to `sys.path` or `PYTHONPATH`, then import and call the conversion function directly:

```python
from md_beautify import convert_markdown_to_pdf

convert_markdown_to_pdf("notes.md", "notes.pdf", author="Jane Doe", cover_theme="green")
```

## Project Structure

```text
skills/markdown-printer/
  SKILL.md               Agent instructions: when to use, environment setup, and commands
  scripts/md_beautify.py Core converter with Python API, GUI, and CLI
  scripts/find_python.py Locates a working Python interpreter for PDF generation
examples/sample.md       Sample document demonstrating all supported syntax
build_skill.py           Packages the skill into a .zip file for claude.ai
run.bat                  Windows shortcut to launch the GUI
requirements.txt         Python package dependencies
```

## License

This project is licensed under the [MIT License](LICENSE).
