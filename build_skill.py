"""把 skills/markdown-printer/ 打包成可上傳到 claude.ai 的 zip。

產出：dist/markdown-printer.zip
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = 'markdown-printer'
SKILLS = os.path.join(ROOT, 'skills')
DIST = os.path.join(ROOT, 'dist')


def main():
    os.makedirs(DIST, exist_ok=True)
    zip_path = os.path.join(DIST, NAME + '.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder, dirs, files in os.walk(os.path.join(SKILLS, NAME)):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for name in files:
                full = os.path.join(folder, name)
                # 壓縮檔內以 markdown-printer/ 為最上層資料夾
                zf.write(full, os.path.relpath(full, SKILLS).replace(os.sep, '/'))
    print(f'已建立 {zip_path}')


if __name__ == '__main__':
    main()
