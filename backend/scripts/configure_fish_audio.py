"""交互写入 Fish Key，避免密钥出现在命令历史、参数或输出中。"""

import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import warnings


def main():
    if not sys.stdin.isatty():
        raise SystemExit("请在交互终端运行此命令，避免密钥输入回显。")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            value = getpass.getpass("Fish API Key（输入不回显，粘贴后按回车）：").strip()
    except getpass.GetPassWarning:
        raise SystemExit("终端无法隐藏输入，未读取或修改密钥；请使用支持隐藏输入的交互终端。")
    if not re.fullmatch(r"[A-Za-z0-9._~+/-]+=*", value):
        raise SystemExit("Key 为空或不是有效的 ASCII 令牌，未修改配置。")
    target = Path(__file__).resolve().parents[1] / ".env"
    content = target.read_text()
    content = re.sub(r"(?m)^(?:export\s+)?FISH_SPEECH_API_KEY=.*\n?", "", content)
    content = content.rstrip() + "\nFISH_SPEECH_API_KEY=" + json.dumps(value) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=".fish-config-", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("Fish Key 已保存；没有输出密钥。请返回对话告诉我“已写好”。")


if __name__ == "__main__":
    main()
