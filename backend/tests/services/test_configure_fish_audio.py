"""凭据写入助手必须拒绝回显并保持原配置可读取。"""

import importlib.util
from pathlib import Path
import warnings

import pytest


@pytest.fixture
def helper():
    path = Path(__file__).resolve().parents[2] / "scripts/configure_fish_audio.py"
    spec = importlib.util.spec_from_file_location("configure_fish_audio_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_getpass_fallback_cannot_echo_key(helper, monkeypatch):
    monkeypatch.setattr(helper.sys.stdin, "isatty", lambda: True)
    def unhidden(prompt):
        warnings.warn("无法隐藏输入", helper.getpass.GetPassWarning)
        pytest.fail("警告后不得继续读取密钥")
    monkeypatch.setattr(helper.getpass, "getpass", unhidden)
    with pytest.raises(SystemExit, match="无法隐藏输入"):
        helper.main()


@pytest.mark.parametrize("key", ["", "secret${HOME}", "密钥", "secret\x7f", "secret key"])
def test_invalid_key_cannot_modify_file(helper, monkeypatch, key):
    monkeypatch.setattr(helper.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(helper.getpass, "getpass", lambda prompt: key)
    with pytest.raises(SystemExit, match="ASCII 令牌"):
        helper.main()


def test_key_is_atomic_private_and_roundtrips_dotenv(helper, monkeypatch, tmp_path, capsys):
    from dotenv import dotenv_values
    script = tmp_path / "scripts/configure_fish_audio.py"
    script.parent.mkdir()
    monkeypatch.setattr(helper, "__file__", str(script))
    monkeypatch.setattr(helper.sys.stdin, "isatty", lambda: True)
    key = "test-only_Fish-token.123+/=="
    monkeypatch.setattr(helper.getpass, "getpass", lambda prompt: key)
    env = tmp_path / ".env"
    env.write_text('OTHER_SETTING="保留"\nFISH_SPEECH_API_KEY="old"\n')
    helper.main()
    assert dotenv_values(env) == {"OTHER_SETTING": "保留", "FISH_SPEECH_API_KEY": key}
    assert env.stat().st_mode & 0o777 == 0o600
    assert key not in capsys.readouterr().out
    assert list(tmp_path.glob(".fish-config-*")) == []
