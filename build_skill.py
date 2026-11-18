"""把 skill/SKILL.md 與 md_beautify.py 打包成可上傳的 Claude skill。

產出：
  dist/markdown-printer/       可直接複製到 ~/.claude/skills/ 的資料夾
  dist/markdown-printer.zip    可上傳到 claude.ai 的壓縮檔
"""
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = 'markdown-printer'
DIST = os.path.join(ROOT, 'dist')
SKILL_DIR = os.path.join(DIST, NAME)


def main():
    if os.path.isdir(SKILL_DIR):
        shutil.rmtree(SKILL_DIR)
    os.makedirs(os.path.join(SKILL_DIR, 'scripts'))

    shutil.copy2(os.path.join(ROOT, 'skill', 'SKILL.md'), SKILL_DIR)
    shutil.copy2(os.path.join(ROOT, 'md_beautify.py'), os.path.join(SKILL_DIR, 'scripts'))

    zip_path = os.path.join(DIST, NAME + '.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder, _, files in os.walk(SKILL_DIR):
            for name in files:
                full = os.path.join(folder, name)
                # 壓縮檔內以 markdown-printer/ 為最上層資料夾
                zf.write(full, os.path.relpath(full, DIST).replace(os.sep, '/'))

    print(f'已建立 {SKILL_DIR}')
    print(f'已建立 {zip_path}')


if __name__ == '__main__':
    main()
