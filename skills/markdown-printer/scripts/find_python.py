"""找出這台電腦上能執行 md_beautify.py 的 Python。

只用標準函式庫，任何 Python 3 都能執行。依序嘗試：
  1. 環境變數 MARKDOWN_PRINTER_PYTHON
  2. 執行本腳本的 Python，以及 PATH 上的 python3、python
  3. 已安裝 weasyprint 的 conda 環境
對每個候選執行 `md_beautify.py --check`（實際排版一頁 PDF），
印出第一個通過的 Python 路徑並以 0 結束；全部失敗則把原因印到 stderr 並以 1 結束。
"""
import glob
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONVERTER = os.path.join(HERE, 'md_beautify.py')


def conda_candidates():
    conda = shutil.which('conda')
    if not conda:
        return []
    try:
        out = subprocess.run([conda, 'env', 'list', '--json'], capture_output=True,
                             text=True, timeout=60).stdout
        envs = json.loads(out).get('envs', [])
    except (OSError, ValueError, subprocess.SubprocessError):
        return []

    found = []
    for env in envs:
        if os.name == 'nt':
            python = os.path.join(env, 'python.exe')
            has_weasyprint = os.path.isdir(os.path.join(env, 'Lib', 'site-packages', 'weasyprint'))
        else:
            python = os.path.join(env, 'bin', 'python')
            has_weasyprint = bool(glob.glob(os.path.join(env, 'lib', 'python*', 'site-packages', 'weasyprint')))
        if has_weasyprint and os.path.isfile(python):
            found.append(python)
    return found


def candidates():
    items = []
    if os.environ.get('MARKDOWN_PRINTER_PYTHON'):
        items.append(os.environ['MARKDOWN_PRINTER_PYTHON'])
    items.append(sys.executable)
    for name in ('python3', 'python'):
        path = shutil.which(name)
        if path:
            items.append(path)
    items.extend(conda_candidates())

    seen, unique = set(), []
    for path in items:
        key = os.path.normcase(os.path.realpath(path))
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def main():
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    failures = []
    for python in candidates():
        try:
            result = subprocess.run([python, CONVERTER, '--check'], capture_output=True,
                                    text=True, encoding='utf-8', errors='replace',
                                    timeout=180, env=env)
        except (OSError, subprocess.SubprocessError) as e:
            failures.append(f'{python}: {e}')
            continue
        if result.returncode == 0:
            print(python)
            return
        lines = [l for l in result.stderr.splitlines() if '環境檢查失敗' in l]
        failures.append(f'{python}: {lines[0] if lines else result.stderr.strip()[-200:]}')

    print('找不到可用的 Python：', file=sys.stderr)
    for line in failures:
        print('  ' + line, file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    main()
