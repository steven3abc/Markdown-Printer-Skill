# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "markdown>=3.4",
#     "weasyprint>=60",
# ]
# ///
"""Markdown Printer：把 Markdown 轉成排版好的 A4 技術文件 PDF。

不帶參數執行會開啟圖形介面，帶入 Markdown 檔案路徑則以命令列模式轉換，
加上 --check 則只檢查執行環境。上方的 script 區塊讓 `uv run` 可以自動準備套件。
"""
import os
import sys
import re
import html
import argparse
import colorsys
import random
import threading

# Windows：讓 WeasyPrint 優先使用 conda 環境內的 GTK/Pango DLL，
# 避免 PATH 上其他程式 (例如 gtkwave) 附帶的舊版 DLL 造成載入失敗
if os.name == 'nt':
    _dll_dir = os.path.join(sys.prefix, 'Library', 'bin')
    if os.path.isdir(_dll_dir):
        os.environ['PATH'] = _dll_dir + os.pathsep + os.environ.get('PATH', '')
        os.environ.setdefault('WEASYPRINT_DLL_DIRECTORIES', _dll_dir)

# markdown 與 weasyprint 延後到實際轉換時才載入，
# 缺套件或缺系統函式庫時才能印出清楚的錯誤，而不是一進程式就崩潰
markdown = HTML = CSS = None

def _load_deps():
    global markdown, HTML, CSS
    if HTML is None:
        import markdown as _markdown
        from weasyprint import HTML as _HTML, CSS as _CSS
        markdown, HTML, CSS = _markdown, _HTML, _CSS

def check_environment():
    """實際排版一頁含中文的小 PDF，確認套件、系統函式庫都能正常運作。回傳錯誤訊息，正常則回傳 None"""
    try:
        _load_deps()
        HTML(string='<p>Markdown Printer 環境檢查</p>').write_pdf()
    except ImportError as e:
        return f'缺少 Python 套件：{e}。請安裝 markdown 與 weasyprint'
    except Exception as e:
        hint = ''
        if os.name == 'nt':
            hint = ('\nWindows 上通常是缺少 GTK/Pango，或 PATH 上有其他程式附帶的舊版 DLL。'
                    '建議用 conda 安裝：conda install -c conda-forge weasyprint，並用該環境的 Python 執行')
        else:
            hint = '\nLinux 需要 libpango-1.0-0 與 libpangoft2-1.0-0，macOS 需要 brew install pango'
        return f'WeasyPrint 無法排版：{e}{hint}'
    return None

CALLOUT_LABELS = {
    'NOTE': 'Note',
    'TIP': 'Tip',
    'IMPORTANT': 'Important',
    'WARNING': 'Warning',
    'CAUTION': 'Caution',
}

# 封面配色：bg1/bg2 為背景漸層、accent 為左側色條，其餘為文字顏色
COVER_THEMES = {
    '經典藍': dict(bg1='#f5f7fa', bg2='#c3cfe2', accent='#0366d6', title='#1b1f23', subtitle='#586069', author='#24292e'),
    '森林綠': dict(bg1='#f2f9f4', bg2='#b9dcc5', accent='#1a7f37', title='#14301e', subtitle='#4a6b55', author='#1f3a28'),
    '暖陽橙': dict(bg1='#fff8f1', bg2='#f6d3b3', accent='#d9480f', title='#3b1d0b', subtitle='#7a5235', author='#4a2a14'),
    '玫瑰紅': dict(bg1='#fdf3f5', bg2='#f2c4cf', accent='#c2255c', title='#3a1020', subtitle='#7d4a5a', author='#4a1a2b'),
    '優雅紫': dict(bg1='#f7f4fc', bg2='#d4c7ec', accent='#6f42c1', title='#24163f', subtitle='#5f5378', author='#2e2050'),
    '石墨灰': dict(bg1='#f6f8fa', bg2='#d0d7de', accent='#24292e', title='#1b1f23', subtitle='#57606a', author='#24292e'),
    '深夜藍': dict(bg1='#0f2027', bg2='#2c5364', accent='#4fc3f7', title='#ffffff', subtitle='#b8d4e0', author='#e6f2f7'),
}
COVER_RANDOM = '隨機'
COVER_CHOICES = list(COVER_THEMES) + [COVER_RANDOM]

# 命令列可用的英文別名
COVER_ALIASES = {
    'blue': '經典藍', 'green': '森林綠', 'orange': '暖陽橙', 'rose': '玫瑰紅',
    'purple': '優雅紫', 'graphite': '石墨灰', 'midnight': '深夜藍', 'random': COVER_RANDOM,
}

def normalize_cover_name(name):
    """接受中文名稱或英文別名，回傳中文配色名稱；不認得則丟出 ValueError"""
    if name in COVER_CHOICES:
        return name
    key = name.strip().lower()
    if key in COVER_ALIASES:
        return COVER_ALIASES[key]
    raise ValueError(name)

def _hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, l, s)
    return '#{:02x}{:02x}{:02x}'.format(round(r * 255), round(g * 255), round(b * 255))

def random_cover_theme():
    """隨機產生一組色相協調的配色 (偶爾產生深色封面)"""
    h = random.random()
    shift = random.uniform(0.03, 0.12)
    if random.random() < 0.25:  # 深色封面
        return dict(bg1=_hsl(h, 0.45, 0.12), bg2=_hsl(h + shift, 0.40, 0.28), accent=_hsl(h, 0.80, 0.65),
                    title='#ffffff', subtitle=_hsl(h, 0.30, 0.80), author=_hsl(h, 0.25, 0.90))
    return dict(bg1=_hsl(h, 0.50, 0.97), bg2=_hsl(h + shift, 0.45, 0.82), accent=_hsl(h, 0.75, 0.40),
                title=_hsl(h, 0.40, 0.12), subtitle=_hsl(h, 0.15, 0.38), author=_hsl(h, 0.30, 0.18))

def resolve_cover_theme(name):
    if name == COVER_RANDOM:
        return random_cover_theme()
    return COVER_THEMES.get(name, COVER_THEMES['經典藍'])

_CALLOUT_START_RE = re.compile(r'^ {0,3}>[ \t]?\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*(.*)$', re.IGNORECASE)
_QUOTE_LINE_RE = re.compile(r'^ {0,3}>[ \t]?')
_FENCE_LINE_RE = re.compile(r'^ {0,3}(```|~~~)')

def process_github_callouts(md_text):
    """將 GitHub 風格的 > [!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION] 轉換為提示框。

    在 Markdown 階段就把整段引用改寫成 <div markdown="1">，
    因為 Python-Markdown 會把中間只隔一個空行的多個引用合併成同一個 <blockquote>，
    等轉成 HTML 後才處理會讓第二個以後的提示框失效。
    """
    lines = md_text.split('\n')
    out = []
    fence = None
    i = 0
    while i < len(lines):
        line = lines[i]

        # 程式碼區塊內的內容原樣保留
        fm = _FENCE_LINE_RE.match(line)
        if fence:
            if fm and fm.group(1) == fence:
                fence = None
            out.append(line)
            i += 1
            continue
        if fm:
            fence = fm.group(1)
            out.append(line)
            i += 1
            continue

        m = _CALLOUT_START_RE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        kind = m.group(1).upper()
        body = [m.group(2)] if m.group(2).strip() else []
        i += 1
        while i < len(lines) and _QUOTE_LINE_RE.match(lines[i]):
            body.append(_QUOTE_LINE_RE.sub('', lines[i], count=1))
            i += 1

        content = '\n'.join(body).strip('\n')
        # 若內文本身已以粗體開頭 (例如 **Note:**)，就不再重複加標籤
        label = '' if content.lstrip().startswith('**') else \
            f'<strong class="callout-label">{CALLOUT_LABELS[kind]}</strong>\n\n'
        out.extend(['', f'<div class="callout {kind.lower()}" markdown="1">', '',
                    label + content, '', '</div>', ''])

    return '\n'.join(out)

_FENCE_RE = re.compile(r'^(```|~~~).*?^\1[ \t]*$', flags=re.MULTILINE | re.DOTALL)

def guess_title(md_text, input_path):
    """取第一個 H1 作為標題，沒有則使用檔名 (略過程式碼區塊內的 # 註解)"""
    text = _FENCE_RE.sub('', md_text)
    m = re.search(r'^#[ \t]+(.+?)[ \t]*#*[ \t]*$', text, flags=re.MULTILINE)
    if m:
        # 去掉標題裡常見的行內 Markdown 符號，例如 **粗體**、`code`
        title = re.sub(r'[*_`]', '', m.group(1)).strip()
        if title:
            return title
    return os.path.splitext(os.path.basename(input_path))[0]

def read_markdown(path):
    """以 UTF-8 讀取 Markdown，並自動去掉 Windows 記事本常加的 BOM"""
    with open(path, 'r', encoding='utf-8-sig') as f:
        return f.read()

def generate_tech_doc_html(md_text, title, author, subtitle="", with_cover=True, cover_theme='經典藍'):
    """將技術文件的 Markdown 轉為 HTML，嵌入適合技術文件的 CSS"""

    # extra = tables、fenced_code、attr_list、def_list、abbr、footnotes 等
    # (extra 內含 md_in_html，讓提示框 <div markdown="1"> 裡的 Markdown 也會被轉換)
    extensions = ['extra', 'toc', 'sane_lists']
    _load_deps()
    html_body = markdown.markdown(process_github_callouts(md_text), extensions=extensions)

    font_stack = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", sans-serif'

    # 技術文件專用 CSS
    css_style = """
    @page {
        size: A4;
        margin: 25mm 20mm;
        @bottom-right {
            content: counter(page);
            font-family: FONT_STACK;
            font-size: 9pt;
            color: #555;
        }
        @top-left {
            content: string(doc_title);
            font-family: FONT_STACK;
            font-size: 8pt;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    }

    * { box-sizing: border-box; }

    body {
        font-family: FONT_STACK;
        font-size: 11pt;
        line-height: 1.65;
        color: #24292e;
        margin: 0;
        padding: 0;
    }

    /* 提供頁首使用的文件標題 (不顯示於內文) */
    .running-title {
        string-set: doc_title content();
        height: 0;
        margin: 0;
        overflow: hidden;
        visibility: hidden;
    }

    /* 標題設計 */
    h1 {
        font-size: 24pt;
        border-bottom: 2px solid #eaecef;
        padding-bottom: 10px;
        margin-top: 40px;
        margin-bottom: 20px;
        color: #1b1f23;
    }

    h2 {
        font-size: 18pt;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 8px;
        margin-top: 35px;
        margin-bottom: 15px;
        color: #1b1f23;
    }

    h3 {
        font-size: 14pt;
        margin-top: 25px;
        margin-bottom: 10px;
        color: #24292e;
    }

    h1, h2, h3, h4 { page-break-after: avoid; }

    /* 內文設計 */
    p {
        margin-top: 0;
        margin-bottom: 16px;
        text-align: left;
    }

    a {
        color: #0366d6;
        text-decoration: none;
    }

    /* 圖片排版 */
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 30px auto;
        border: 1px solid #ddd;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* 列表 */
    ul, ol {
        margin-top: 0;
        margin-bottom: 16px;
        padding-left: 2em;
    }

    /* 定義清單 */
    dt { font-weight: 600; margin-top: 8px; }
    dd { margin: 0 0 12px 2em; }

    /* 程式碼與區塊 */
    code {
        background-color: rgba(27,31,35,0.05);
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, "Microsoft JhengHei", monospace;
        font-size: 90%;
    }

    pre {
        background-color: #f6f8fa;
        border-radius: 6px;
        padding: 16px;
        line-height: 1.45;
        margin-bottom: 16px;
        white-space: pre-wrap;
        word-wrap: break-word;
        page-break-inside: avoid;
    }

    pre code {
        background-color: transparent;
        padding: 0;
    }

    blockquote {
        border-left: 4px solid #dfe2e5;
        color: #6a737d;
        padding-left: 1em;
        margin-left: 0;
    }

    /* GitHub 風格的 Callouts (提示框) */
    .callout {
        padding: 15px;
        margin-bottom: 16px;
        border-radius: 6px;
        border-left: 5px solid;
        page-break-inside: avoid;
    }
    .callout p { margin: 0 0 8px 0; }
    .callout p:last-child { margin-bottom: 0; }
    .callout .callout-label { display: block; margin-bottom: 5px; font-size: 1.05em; }

    .callout.note { background-color: #f0f8ff; border-color: #0366d6; }
    .callout.note strong { color: #0366d6; }

    .callout.tip { background-color: #effaf1; border-color: #1a7f37; }
    .callout.tip strong { color: #1a7f37; }

    .callout.important { background-color: #fff8c5; border-color: #e3b341; }
    .callout.important strong { color: #b08800; }

    .callout.warning { background-color: #fff4e5; border-color: #d97706; }
    .callout.warning strong { color: #b45309; }

    .callout.caution { background-color: #ffebe9; border-color: #cf222e; }
    .callout.caution strong { color: #cf222e; }

    /* 表格 */
    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 16px;
        page-break-inside: avoid;
    }
    table th, table td {
        padding: 8px 13px;
        border: 1px solid #dfe2e5;
        text-align: left;
    }
    table th {
        font-weight: 600;
        background-color: #f6f8fa;
    }
    """

    cover_css = """
    /* 封面頁取消頁首頁尾 */
    @page :first {
        margin: 0;
        @top-left { content: normal; }
        @bottom-right { content: normal; }
    }

    /* 封面設計 */
    .cover-page {
        height: 297mm; /* A4 高度 */
        background: linear-gradient(135deg, C_BG1 0%, C_BG2 100%);
        padding: 80mm 30mm 30mm 30mm;
        border-left: 15px solid C_ACCENT;
        page-break-after: always;
    }
    .cover-title {
        font-size: 32pt;
        font-weight: 800;
        color: C_TITLE;
        margin-bottom: 20px;
        line-height: 1.2;
    }
    .cover-subtitle {
        font-size: 16pt;
        color: C_SUBTITLE;
        margin-bottom: 50px;
    }
    .cover-author {
        font-size: 12pt;
        color: C_AUTHOR;
        font-weight: bold;
    }
    """

    css_style = css_style.replace('FONT_STACK', font_stack)

    t = html.escape(title)
    cover_html = ""
    if with_cover:
        colors = resolve_cover_theme(cover_theme) if isinstance(cover_theme, str) else cover_theme
        for key in ('bg1', 'bg2', 'accent', 'title', 'subtitle', 'author'):
            cover_css = cover_css.replace('C_' + key.upper(), colors[key])
        css_style += cover_css
        cover_html = f"""
    <div class="cover-page">
        <div class="cover-title">{t}</div>
        <div class="cover-subtitle">{html.escape(subtitle)}</div>
        <div class="cover-author">{html.escape(author)}</div>
    </div>"""

    full_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>{t}</title>
    <style>{css_style}</style>
</head>
<body>{cover_html}
    <div class="running-title">{t}</div>

    <div class="doc-content">
        {html_body}
    </div>
</body>
</html>
"""
    return full_html

def convert_markdown_to_pdf(input_path, output_path, title=None, author="", subtitle="",
                            with_cover=True, css_path=None, cover_theme='經典藍'):
    """核心轉換函式：將 Markdown 轉為 PDF"""
    _load_deps()
    md_text = read_markdown(input_path)

    if not title:
        title = guess_title(md_text, input_path)

    html_content = generate_tech_doc_html(md_text, title, author, subtitle, with_cover, cover_theme)

    stylesheets = []
    if css_path:
        if not os.path.exists(css_path):
            raise FileNotFoundError(f"找不到 CSS 檔案：{css_path}")
        stylesheets.append(CSS(filename=css_path))

    # base_url 設為 Markdown 所在資料夾，讓相對路徑圖片可以正確載入
    base_dir = os.path.dirname(os.path.abspath(input_path))

    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)
    HTML(string=html_content, base_url=base_dir).write_pdf(output_path, stylesheets=stylesheets)


# tkinter 只有圖形介面需要，延後到真正開視窗時才載入，
# 讓命令列模式在沒有 Tk 的環境 (例如 Linux 伺服器、雲端沙盒) 也能執行
tk = filedialog = messagebox = None

def _load_tkinter():
    global tk, filedialog, messagebox
    import tkinter
    from tkinter import filedialog as _fd, messagebox as _mb
    tk, filedialog, messagebox = tkinter, _fd, _mb


class MarkdownToPdfApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown 轉 PDF 工具")
        self.root.resizable(False, False)

        # 變數綁定
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.subtitle_var = tk.StringVar(value="Official Documentation & Best Practices")
        self.author_var = tk.StringVar(value="Developer Team")
        self.css_file_var = tk.StringVar()
        self.cover_var = tk.BooleanVar(value=True)
        self.cover_theme_var = tk.StringVar(value=COVER_CHOICES[0])

        self._build_ui()

    def _build_ui(self):
        # --- 介面排版 (Padding & Grid) ---
        pad = {'padx': 10, 'pady': 6}
        row = 0

        # 1. 選擇 Markdown 來源檔案
        tk.Label(self.root, text="來源檔案 (.md):").grid(row=row, column=0, sticky="e", **pad)
        tk.Entry(self.root, textvariable=self.input_file_var, width=45, state='readonly').grid(row=row, column=1, sticky="we")
        tk.Button(self.root, text="瀏覽...", command=self.select_input_file).grid(row=row, column=2, padx=10)
        row += 1

        # 2. 選擇 PDF 輸出位置
        tk.Label(self.root, text="輸出位置 (.pdf):").grid(row=row, column=0, sticky="e", **pad)
        tk.Entry(self.root, textvariable=self.output_file_var, width=45, state='readonly').grid(row=row, column=1, sticky="we")
        tk.Button(self.root, text="瀏覽...", command=self.select_output_file).grid(row=row, column=2, padx=10)
        row += 1

        # 3. 文件資訊 (封面與頁首)
        tk.Label(self.root, text="文件標題:").grid(row=row, column=0, sticky="e", **pad)
        tk.Entry(self.root, textvariable=self.title_var, width=45).grid(row=row, column=1, sticky="we")
        row += 1

        tk.Label(self.root, text="副標題:").grid(row=row, column=0, sticky="e", **pad)
        self.subtitle_entry = tk.Entry(self.root, textvariable=self.subtitle_var, width=45)
        self.subtitle_entry.grid(row=row, column=1, sticky="we")
        row += 1

        tk.Label(self.root, text="作者:").grid(row=row, column=0, sticky="e", **pad)
        self.author_entry = tk.Entry(self.root, textvariable=self.author_var, width=45)
        self.author_entry.grid(row=row, column=1, sticky="we")
        row += 1

        tk.Checkbutton(self.root, text="加入封面頁", variable=self.cover_var,
                       command=self._toggle_cover_fields).grid(row=row, column=1, sticky="w")
        row += 1

        tk.Label(self.root, text="封面配色:").grid(row=row, column=0, sticky="e", **pad)
        theme_row = tk.Frame(self.root)
        theme_row.grid(row=row, column=1, sticky="w")
        self.theme_menu = tk.OptionMenu(theme_row, self.cover_theme_var, *COVER_CHOICES,
                                        command=lambda _: self._update_theme_preview())
        self.theme_menu.config(width=8)
        self.theme_menu.pack(side="left")
        self.theme_preview = tk.Canvas(theme_row, width=90, height=22, highlightthickness=1,
                                       highlightbackground="#999")
        self.theme_preview.pack(side="left", padx=8)
        self._update_theme_preview()
        row += 1

        # 4. 自訂 CSS (選填)
        tk.Label(self.root, text="自訂 CSS (選填):").grid(row=row, column=0, sticky="e", **pad)
        tk.Entry(self.root, textvariable=self.css_file_var, width=45, state='readonly').grid(row=row, column=1, sticky="we")
        css_btns = tk.Frame(self.root)
        css_btns.grid(row=row, column=2, padx=10)
        tk.Button(css_btns, text="瀏覽...", command=self.select_css_file).pack(side="left")
        tk.Button(css_btns, text="清除", command=lambda: self.css_file_var.set("")).pack(side="left", padx=(4, 0))
        row += 1

        # 5. 狀態提示與轉換按鈕
        self.status_label = tk.Label(self.root, text="請選擇檔案後點擊「開始轉換」", fg="gray")
        self.status_label.grid(row=row, column=0, columnspan=3, pady=(16, 8))
        row += 1

        self.convert_btn = tk.Button(self.root, text="開始轉換", command=self.start_conversion,
                                     bg="#4CAF50", fg="black", font=("Arial", 12, "bold"), width=15)
        self.convert_btn.grid(row=row, column=0, columnspan=3, pady=(0, 16))

    def _toggle_cover_fields(self):
        state = 'normal' if self.cover_var.get() else 'disabled'
        self.subtitle_entry.config(state=state)
        self.author_entry.config(state=state)
        self.theme_menu.config(state=state)

    def _update_theme_preview(self):
        """在色塊上預覽目前選擇的封面配色 (隨機時顯示問號)"""
        c = self.theme_preview
        c.delete("all")
        name = self.cover_theme_var.get()
        if name == COVER_RANDOM:
            c.create_text(45, 11, text="? ? ?", fill="#666", font=("Arial", 10, "bold"))
            return
        t = COVER_THEMES[name]
        c.create_rectangle(0, 0, 8, 24, fill=t['accent'], outline="")
        c.create_rectangle(8, 0, 49, 24, fill=t['bg1'], outline="")
        c.create_rectangle(49, 0, 92, 24, fill=t['bg2'], outline="")
        c.create_text(50, 11, text="Aa", fill=t['title'], font=("Arial", 10, "bold"))

    def select_input_file(self):
        filepath = filedialog.askopenfilename(
            title="選擇 Markdown 檔案",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            self.input_file_var.set(filepath)
            # 自動推導輸出檔名與標題
            self.output_file_var.set(os.path.splitext(filepath)[0] + ".pdf")
            try:
                self.title_var.set(guess_title(read_markdown(filepath), filepath))
            except (OSError, UnicodeDecodeError):
                self.title_var.set(os.path.splitext(os.path.basename(filepath))[0])

    def select_output_file(self):
        current = self.output_file_var.get()
        filepath = filedialog.asksaveasfilename(
            title="儲存 PDF 檔案",
            defaultextension=".pdf",
            initialdir=os.path.dirname(current) if current else None,
            initialfile=os.path.basename(current) if current else None,
            filetypes=[("PDF Files", "*.pdf")]
        )
        if filepath:
            self.output_file_var.set(filepath)

    def select_css_file(self):
        filepath = filedialog.askopenfilename(
            title="選擇 CSS 檔案",
            filetypes=[("CSS Files", "*.css"), ("All Files", "*.*")]
        )
        if filepath:
            self.css_file_var.set(filepath)

    def start_conversion(self):
        input_path = self.input_file_var.get()
        output_path = self.output_file_var.get()

        if not input_path or not output_path:
            messagebox.showwarning("警告", "請先選擇來源檔案與輸出位置！")
            return

        kwargs = dict(
            title=self.title_var.get().strip() or None,
            author=self.author_var.get().strip(),
            subtitle=self.subtitle_var.get().strip(),
            with_cover=self.cover_var.get(),
            css_path=self.css_file_var.get() or None,
            cover_theme=self.cover_theme_var.get(),
        )

        self.status_label.config(text="正在轉換中，請稍候... (網路圖片需要下載時間)", fg="blue")
        self.convert_btn.config(state='disabled')

        # 在背景執行緒轉換，避免視窗凍結。
        # Tk 不是執行緒安全的，背景執行緒只寫入結果，由主執行緒輪詢後更新介面
        result = {}

        def worker():
            try:
                convert_markdown_to_pdf(input_path, output_path, **kwargs)
                result['error'] = None
            except Exception as e:
                result['error'] = e

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        def poll():
            if thread.is_alive():
                self.root.after(100, poll)
            else:
                self._on_done(output_path, result.get('error'))

        self.root.after(100, poll)

    def _on_done(self, output_path, error):
        self.convert_btn.config(state='normal')
        if error is None:
            self.status_label.config(text="✅ 轉換成功！", fg="green")
            if messagebox.askyesno("成功", f"檔案已成功儲存至：\n{output_path}\n\n要立即開啟嗎？"):
                if hasattr(os, 'startfile'):
                    os.startfile(output_path)
        else:
            self.status_label.config(text="❌ 轉換失敗", fg="red")
            if isinstance(error, PermissionError):
                msg = f"無法寫入檔案，PDF 可能正在其他程式中開啟：\n{output_path}"
            else:
                msg = f"轉換失敗: {error}"
            messagebox.showerror("錯誤", msg)


def main():
    parser = argparse.ArgumentParser(description="Markdown 轉 PDF 工具 (不帶參數則開啟圖形介面)")
    parser.add_argument("input", nargs="?", help="來源 Markdown 檔案")
    parser.add_argument("-o", "--output", help="輸出 PDF 路徑 (預設與來源同名)")
    parser.add_argument("-t", "--title", help="文件標題 (預設取第一個 H1 或檔名)")
    parser.add_argument("-a", "--author", default="Developer Team", help="作者")
    parser.add_argument("-s", "--subtitle", default="Official Documentation & Best Practices", help="封面副標題")
    parser.add_argument("--no-cover", action="store_true", help="不產生封面頁")
    parser.add_argument("--css", help="額外套用的 CSS 檔案")
    parser.add_argument("--check", action="store_true", help="只檢查執行環境能否產生 PDF，正常時印出 OK")
    aliases = ', '.join(f'{en}={zh}' for en, zh in COVER_ALIASES.items())
    parser.add_argument("-c", "--cover-color", default=COVER_CHOICES[0], metavar="COLOR",
                        help=f"封面配色：{'、'.join(COVER_CHOICES)}，或英文別名 {aliases} (預設：經典藍)")
    args = parser.parse_args()

    if args.check:
        error = check_environment()
        if error:
            print(f'環境檢查失敗：{error}', file=sys.stderr)
            sys.exit(1)
        print(f'OK ({sys.executable})')
        return

    if args.input is None:
        # 建立主視窗並啟動事件迴圈
        _load_tkinter()
        root = tk.Tk()
        MarkdownToPdfApp(root)
        root.mainloop()
        return

    try:
        cover_theme = normalize_cover_name(args.cover_color)
    except ValueError:
        parser.error(f"未知的封面配色：{args.cover_color}")

    if not os.path.isfile(args.input):
        print(f"錯誤：找不到檔案 '{args.input}'", file=sys.stderr)
        sys.exit(1)

    output_pdf = args.output or os.path.splitext(args.input)[0] + ".pdf"
    print("正在生成 PDF...")
    try:
        convert_markdown_to_pdf(args.input, output_pdf, args.title, args.author,
                                args.subtitle, not args.no_cover, args.css, cover_theme)
        print(f"成功匯出 PDF: {output_pdf}")
    except PermissionError:
        print(f"轉換發生錯誤: 無法寫入 {output_pdf}，PDF 可能正在其他程式中開啟", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"轉換發生錯誤: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
