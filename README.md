# Markdown Printer Skill

Markdown Printer Skill 把 Markdown 檔案轉成排版好的 A4 技術文件 PDF，會自動加上封面頁、頁首標題與頁碼，並支援 GitHub 風格的提示框、表格與程式碼區塊。它是一個符合 [Agent Skills](https://agentskills.io) 格式的 skill，裝進 Claude Code、Codex、Gemini CLI、Cursor、GitHub Copilot 等 AI Agent 之後，直接說「把這份 md 轉成 PDF」就能使用。不透過 Agent 時，也可以用圖形介面或命令列單獨執行。

## 功能

- A4 版面，頁首顯示文件標題，頁尾顯示頁碼，封面頁不顯示頁首頁尾
- 封面有 7 種配色可選，也可以每次隨機產生一組
- 支援 GitHub 的 `> [!NOTE]`、`[!TIP]`、`[!IMPORTANT]`、`[!WARNING]`、`[!CAUTION]` 提示框
- 支援表格、fenced code、註腳、定義清單、`[TOC]` 目錄
- 相對路徑的圖片以 Markdown 檔所在的資料夾為基準，網路圖片會自動下載
- 可以額外套用自己的 CSS 覆蓋預設樣式
- 中英文字型都已設定好，中文優先使用 Noto Sans TC 與微軟正黑體

## 安裝 skill

skill 本體是 [`skills/markdown-printer/`](skills/markdown-printer) 這個資料夾，裡面有給 Agent 看的 `SKILL.md` 和轉換程式 `scripts/md_beautify.py`。安裝就是把這個資料夾放進 Agent 會讀取的 skills 目錄，下面三種方式擇一即可。

### 方法一：用 skills CLI 一鍵安裝

已經裝好 Node.js 的話，[skills CLI](https://github.com/vercel-labs/skills) 會偵測電腦上有哪些 Agent，並把 skill 裝到對應的目錄：

```bash
npx skills add steven3abc/Markdown-Printer-Skill
```

加上 `-g` 會裝到使用者目錄，所有專案都能用，不加則只裝在目前的專案。要指定 Agent 時用 `-a`，例如 `-a claude-code`。

### 方法二：手動複製

先下載 repository：

```bash
git clone https://github.com/steven3abc/Markdown-Printer-Skill.git
```

再把 `skills/markdown-printer` 複製到 Agent 的 skills 目錄。以 Claude Code 為例，macOS 和 Linux 的指令如下：

```bash
mkdir -p ~/.claude/skills && cp -r Markdown-Printer-Skill/skills/markdown-printer ~/.claude/skills/
```

Windows PowerShell 的指令如下：

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null; Copy-Item -Recurse Markdown-Printer-Skill\skills\markdown-printer "$HOME\.claude\skills\"
```

其他 Agent 只要把目的地換成下表的目錄。「個人」目錄裡的 skill 在所有專案都能用，「專案」目錄則放在專案根目錄，只對該專案生效，也可以一起提交到版本庫給團隊使用。

| Agent | 個人 | 專案 |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` 或 `~/.agents/skills/` | `.gemini/skills/` 或 `.agents/skills/` |
| Cursor | `~/.cursor/skills/` 或 `~/.agents/skills/` | `.cursor/skills/` 或 `.agents/skills/` |
| GitHub Copilot（VS Code） | `~/.copilot/skills/` | `.github/skills/` |

由於 Codex、Gemini CLI 與 Cursor 都會讀取 `~/.agents/skills/`，裝在這裡一次就能讓三者共用，而 Cursor 也會讀取 `~/.claude/skills/`，已經裝給 Claude Code 的話不必再裝一次。各家的路徑可能隨版本調整，以官方文件為準：[Claude Code](https://code.claude.com/docs/en/skills)、[Codex](https://learn.chatgpt.com/docs/build-skills)、[Gemini CLI](https://geminicli.com/docs/cli/skills/)、[Cursor](https://cursor.com/docs/skills)、[VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)。

### 方法三：用 Agent 內建的安裝指令

Gemini CLI 可以直接從 GitHub 安裝：

```bash
gemini skills install https://github.com/steven3abc/Markdown-Printer-Skill.git --path skills/markdown-printer
```

Codex 內建的 `$skill-installer` 也能從 GitHub 下載 skill，在 Codex 裡輸入 `$skill-installer` 並附上 `https://github.com/steven3abc/Markdown-Printer-Skill/tree/main/skills/markdown-printer` 即可。

### claude.ai 與 Claude 桌面 app

網頁版和桌面 app 的 Chat 要上傳 zip 檔。在 repository 根目錄執行下列指令，會產生 `dist/markdown-printer.zip`：

```bash
python build_skill.py
```

接著到 Settings → Capabilities → Skills 上傳這個 zip。claude.ai 的程式在雲端沙盒執行，skill 會自動安裝缺少的 Python 套件，但沙盒如果沒有中文字型，又無法安裝 `fonts-noto-cjk`，中文會顯示成方框。

### 確認安裝成功

重新啟動 Agent 後，大多數 Agent 可以用 `/skills` 查看已載入的 skill，Claude Code 也可以直接輸入 `/markdown-printer` 呼叫。之後說「把 notes.md 轉成 PDF」或「幫這份 md 加封面輸出成 PDF」，Agent 就會使用這個 skill，沒有指定配色時會用隨機配色。

## 環境需求

skill 實際上是由 Agent 執行 `scripts/md_beautify.py`，所以 Agent 所在的電腦需要 Python 3.9 以上版本，以及 `markdown` 與 `weasyprint` 兩個套件。缺少套件時 skill 會嘗試自動用 pip 安裝，也可以自己先裝好：

```bash
pip install -r requirements.txt
```

[WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) 還需要 Pango 等系統函式庫，各平台的安裝方式如下：

- Windows：建議用 conda 安裝，`conda install -c conda-forge weasyprint` 會一併裝好 GTK 與 Pango。程式啟動時會優先使用 conda 環境裡的 DLL，避免 PATH 上其他軟體附帶的舊版 DLL 造成載入失敗。
- macOS：`brew install pango`
- Debian、Ubuntu：`apt install libpango-1.0-0 libpangoft2-1.0-0`，含中文的文件還需要 `fonts-noto-cjk`

## 不透過 Agent 單獨使用

### 圖形介面

不帶參數執行就會開啟視窗，Windows 上也可以直接點兩下 `run.bat`。

```bash
python skills/markdown-printer/scripts/md_beautify.py
```

選好 Markdown 檔案後，程式會自動填入輸出路徑與標題，調整封面資訊後按「開始轉換」即可。

`run.bat` 預設使用 PATH 上的 `pythonw`。如果要指定其他 Python，例如某個 conda 環境，在同一個資料夾建立 `run.local.bat`，`run.bat` 會改為執行它，這個檔案已列在 `.gitignore` 裡：

```bat
@echo off
start "" "C:\path\to\envs\myenv\pythonw.exe" "%~dp0skills\markdown-printer\scripts\md_beautify.py"
```

### 命令列

```bash
python skills/markdown-printer/scripts/md_beautify.py examples/sample.md
python skills/markdown-printer/scripts/md_beautify.py notes.md -o out/notes.pdf -a "王小明" -s "內部文件" -c green
python skills/markdown-printer/scripts/md_beautify.py notes.md --no-cover --css my-style.css
```

| 選項 | 說明 | 預設 |
|---|---|---|
| `-o, --output` | 輸出 PDF 路徑 | 與來源同名的 `.pdf` |
| `-t, --title` | 文件標題，用於封面與頁首 | 第一個 H1，沒有則用檔名 |
| `-s, --subtitle` | 封面副標題 | `Official Documentation & Best Practices` |
| `-a, --author` | 封面作者 | `Developer Team` |
| `--no-cover` | 不產生封面頁 | 有封面 |
| `-c, --cover-color` | 封面配色 | `經典藍` |
| `--css` | 額外套用的 CSS 檔案 | 無 |

封面配色可以用中文名稱或英文別名：

| 中文 | 英文別名 |
|---|---|
| 經典藍 | `blue` |
| 森林綠 | `green` |
| 暖陽橙 | `orange` |
| 玫瑰紅 | `rose` |
| 優雅紫 | `purple` |
| 石墨灰 | `graphite` |
| 深夜藍 | `midnight` |
| 隨機 | `random` |

選 `隨機` 時，程式會挑一個色相配出整組協調的顏色，大約四分之一的機率產生深色封面。

### 在 Python 裡呼叫

把 `skills/markdown-printer/scripts` 加進 `sys.path` 或 `PYTHONPATH` 後即可匯入：

```python
from md_beautify import convert_markdown_to_pdf

convert_markdown_to_pdf("notes.md", "notes.pdf", author="王小明", cover_theme="森林綠")
```

## 專案結構

```
skills/markdown-printer/
  SKILL.md               給 Agent 看的說明：何時使用、如何準備環境與下指令
  scripts/md_beautify.py 轉換程式，包含轉換函式、圖形介面與命令列
examples/sample.md       示範所有支援語法的範例文件
build_skill.py           把 skill 打包成 claude.ai 用的 zip
run.bat                  Windows 上開啟圖形介面的捷徑
requirements.txt         Python 套件需求
```

## 授權

本專案採用 [MIT License](LICENSE)。
