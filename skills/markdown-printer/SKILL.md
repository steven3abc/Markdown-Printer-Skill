---
name: markdown-printer
description: 把 Markdown (.md) 檔轉成排版精美的 A4 技術文件 PDF（封面頁、頁首標題、頁碼、GitHub 風格 callout、表格、程式碼區塊）。當使用者要把 .md 轉成 PDF、列印 Markdown、輸出或匯出 Markdown 為 PDF、幫 md 文件加封面，或提到 Markdown Printer / md_beautify 時使用。Convert Markdown files into styled, print-ready PDFs with a cover page.
license: MIT
compatibility: 需要 Python 3.9+ 與 markdown、weasyprint 套件，WeasyPrint 另需 Pango 系統函式庫（Windows 建議用 conda-forge 安裝）。雲端沙盒可自動安裝，需要網路。
---

# Markdown Printer

用這個 skill 資料夾裡的 `scripts/md_beautify.py`（WeasyPrint）把 Markdown 轉成 A4 PDF。下面的 `<skill>` 指的是這份 SKILL.md 所在的資料夾，`<python>` 指第 1 步找到的 Python。

## 1. 找到可用的 Python

```bash
python3 <skill>/scripts/find_python.py
```

`python3` 不存在時改用 `python`。這支腳本只用標準函式庫，會依序嘗試環境變數 `MARKDOWN_PRINTER_PYTHON`、PATH 上的 Python 與已安裝 weasyprint 的 conda 環境，每個都實際排版一頁 PDF 測試，成功就印出那個 Python 的路徑，之後的指令都用它。同一段對話裡找到一次即可，不用每次轉換都重找。

全部失敗時，依所在環境處理：

- **雲端沙盒或拋棄式容器**（例如 claude.ai，通常有 `/mnt/user-data/`）：直接安裝，再重跑 `find_python.py`。

  ```bash
  pip install --quiet markdown weasyprint
  ```

  若錯誤提到 `libpango`、`libgobject`，有權限時執行 `apt-get install -y libpango-1.0-0 libpangoft2-1.0-0`。
- **使用者自己的電腦**：不要直接 `pip install` 到使用者的 Python 環境。macOS 與 Linux 上若有 `uv`，改用 `uv run <skill>/scripts/md_beautify.py --check` 測試，通過的話之後都用 `uv run <skill>/scripts/md_beautify.py` 取代 `<python> <skill>/scripts/md_beautify.py`，uv 會依腳本開頭宣告的套件建立獨立的環境，不影響使用者原本的環境。仍然不行時，把 `find_python.py` 印出的原因告訴使用者，說明要安裝什麼，經使用者同意後再安裝。Windows 上 pip 裝不到 WeasyPrint 需要的 GTK，建議使用者建立 conda 環境（`conda create -n md-printer -c conda-forge python weasyprint markdown`）。

文件含中文時，在 Linux 上用 `fc-list :lang=zh | head -3` 確認有中文字型。沒有輸出就嘗試 `apt-get install -y fonts-noto-cjk`，裝不了的話照樣轉換，但要告訴使用者中文可能無法正確顯示。

## 2. 轉換

```bash
<python> <skill>/scripts/md_beautify.py "<input.md>" -o "<output.pdf>" -c random [其他選項]
```

Windows 上在指令前加上 `PYTHONIOENCODING=utf-8`（PowerShell 用 `$env:PYTHONIOENCODING='utf-8';`），避免中文訊息變成亂碼。

- 一定要傳入輸入檔，不帶參數會嘗試開啟圖形介面。
- 在雲端環境（例如 claude.ai）要把 PDF 寫到使用者拿得到的輸出資料夾，通常是 `/mnt/user-data/outputs/`。使用者上傳的檔案通常在 `/mnt/user-data/uploads/`。
- 使用者是直接貼上 Markdown 文字而不是給檔案時，先把內容存成 `.md` 再轉換。
- 含網路圖片時會花比較久的時間下載，timeout 給長一點。

## 選項

| 選項 | 說明 | 預設 |
|---|---|---|
| `-o, --output` | 輸出 PDF 路徑 | 與來源同名 `.pdf` |
| `-t, --title` | 文件標題（封面與頁首） | 第一個 H1，沒有則用檔名 |
| `-s, --subtitle` | 封面副標題 | `Official Documentation & Best Practices` |
| `-a, --author` | 封面作者 | `Developer Team` |
| `--no-cover` | 不產生封面頁 | 有封面 |
| `-c, --cover-color` | 封面配色，見下方 | 用 `random` |
| `--css` | 額外套用的 CSS 檔，可覆蓋預設樣式 | 無 |

封面配色可用中文名稱或英文別名：`經典藍`/`blue`、`森林綠`/`green`、`暖陽橙`/`orange`、`玫瑰紅`/`rose`、`優雅紫`/`purple`、`石墨灰`/`graphite`、`深夜藍`/`midnight`、`隨機`/`random`。使用者沒指定配色時一律用 `-c random`，讓每次的封面顏色都不同，有指定就照使用者說的。

副標題和作者的預設值是通用的佔位文字。使用者沒指定時，依文件內容填入合適的值或詢問使用者，不需要封面就加 `--no-cover`。

## 支援的 Markdown

- 表格、fenced code、footnotes、定義清單、attr_list、目錄（`[TOC]`）
- GitHub callout：`> [!NOTE]`、`[!TIP]`、`[!IMPORTANT]`、`[!WARNING]`、`[!CAUTION]`
- 相對路徑圖片以 `.md` 所在資料夾為基準

## 完成後

- 成功時會印出 `成功匯出 PDF: <path>`，exit code 為 0。失敗時錯誤訊息印在 stderr，exit code 為 1。
- 告訴使用者 PDF 的位置，雲端環境下把檔案交給使用者下載。
