# Markdown Printer

Markdown Printer 把 Markdown 檔案轉成排版好的 A4 技術文件 PDF，會自動加上封面頁、頁首標題與頁碼，並支援 GitHub 風格的提示框、表格與程式碼區塊。它有圖形介面與命令列兩種用法，也可以打包成 Claude 的 skill，讓 Claude 直接幫你轉檔。

## 功能

- A4 版面，頁首顯示文件標題，頁尾顯示頁碼，封面頁不顯示頁首頁尾
- 封面有 7 種配色可選，也可以每次隨機產生一組
- 支援 GitHub 的 `> [!NOTE]`、`[!TIP]`、`[!IMPORTANT]`、`[!WARNING]`、`[!CAUTION]` 提示框
- 支援表格、fenced code、註腳、定義清單、`[TOC]` 目錄
- 相對路徑的圖片以 Markdown 檔所在的資料夾為基準，網路圖片會自動下載
- 可以額外套用自己的 CSS 覆蓋預設樣式
- 中英文字型都已設定好，中文優先使用 Noto Sans TC 與微軟正黑體

## 安裝

需要 Python 3.9 以上版本。

```bash
pip install -r requirements.txt
```

[WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) 需要 Pango 等系統函式庫，各平台的安裝方式如下：

- Windows：建議用 conda 安裝，`conda install -c conda-forge weasyprint` 會一併裝好 GTK 與 Pango。程式啟動時會優先使用 conda 環境裡的 DLL，避免 PATH 上其他軟體附帶的舊版 DLL 造成載入失敗。
- macOS：`brew install pango`
- Debian、Ubuntu：`apt install libpango-1.0-0 libpangoft2-1.0-0`，含中文的文件還需要 `fonts-noto-cjk`

## 使用方式

### 圖形介面

不帶參數執行就會開啟視窗，Windows 上也可以直接點兩下 `run.bat`。

```bash
python md_beautify.py
```

選好 Markdown 檔案後，程式會自動填入輸出路徑與標題，調整封面資訊後按「開始轉換」即可。

`run.bat` 預設使用 PATH 上的 `pythonw`。如果要指定其他 Python，例如某個 conda 環境，在同一個資料夾建立 `run.local.bat`，`run.bat` 會改為執行它，這個檔案已列在 `.gitignore` 裡：

```bat
@echo off
start "" "C:\path\to\envs\myenv\pythonw.exe" "%~dp0md_beautify.py"
```

### 命令列

```bash
python md_beautify.py examples/sample.md
python md_beautify.py notes.md -o out/notes.pdf -a "王小明" -s "內部文件" -c green
python md_beautify.py notes.md --no-cover --css my-style.css
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

```python
from md_beautify import convert_markdown_to_pdf

convert_markdown_to_pdf("notes.md", "notes.pdf", author="王小明", cover_theme="森林綠")
```

## 作為 Claude skill 使用

`skill/SKILL.md` 是給 Claude 讀的說明，告訴它何時使用這個工具、如何準備環境與下指令。打包方式如下：

```bash
python build_skill.py
```

執行後會產生兩樣東西：

- `dist/markdown-printer/`：複製到 `~/.claude/skills/` 底下，Claude Code 就能使用
- `dist/markdown-printer.zip`：在 claude.ai 的 Settings → Capabilities → Skills 上傳

安裝後對 Claude 說「把這份 md 轉成 PDF」即可，skill 會在雲端沙盒裡自動安裝缺少的套件，沒有指定配色時則用隨機配色。要注意的是，雲端環境如果沒有中文字型，又無法安裝 `fonts-noto-cjk`，中文會顯示成方框。

## 專案結構

```
md_beautify.py     主程式，包含轉換函式、圖形介面與命令列
run.bat            Windows 上開啟圖形介面的捷徑
build_skill.py     把 skill 打包到 dist/
skill/SKILL.md     Claude skill 的說明檔
examples/sample.md 示範所有支援語法的範例文件
requirements.txt   Python 套件需求
```

## 授權

本專案採用 [MIT License](LICENSE)。
