# Markdown Printer 範例文件

這份檔案示範 Markdown Printer 支援的語法，可以直接拿來試轉：

```bash
python md_beautify.py examples/sample.md -c random
```

[TOC]

## 文字與清單

一般段落支援 **粗體**、*斜體*、`行內程式碼` 與[連結](https://github.com)，也可以加上註腳[^1]。

- 無序清單第一項
- 無序清單第二項
    - 巢狀項目

1. 有序清單
2. 第二步

[^1]: 註腳會集中顯示在文件最後。

## 提示框

> [!NOTE]
> 一般補充說明。

> [!TIP]
> 實用的小技巧。

> [!IMPORTANT]
> 讀者必須知道的重點。

> [!WARNING]
> 需要注意的風險。

> [!CAUTION]
> 可能造成損失的操作。

## 表格

| 配色 | 英文別名 | 風格 |
|---|---|---|
| 經典藍 | `blue` | 預設、正式 |
| 森林綠 | `green` | 清爽 |
| 深夜藍 | `midnight` | 深色封面 |
| 隨機 | `random` | 每次不同 |

## 程式碼

```python
from md_beautify import convert_markdown_to_pdf

convert_markdown_to_pdf("README.md", "README.pdf", author="Me", cover_theme="森林綠")
```

## 定義清單

WeasyPrint
:   把 HTML 與 CSS 排版成 PDF 的 Python 函式庫。

Callout
:   GitHub 風格的提示框，用 `> [!NOTE]` 這類語法撰寫。
