import os
from pathlib import Path
import tempfile
from config.pin_config import load_shared_secret

def test_load_shared_secret_from_env(monkeypatch):
    monkeypatch.setenv("MY_TEST_SECRET", "env_secret_value")
    assert load_shared_secret(env_var_name="MY_TEST_SECRET", fallback_path="/nonexistent/path") == "env_secret_value"

def test_load_shared_secret_from_file(tmp_path, monkeypatch):
    # create fallback file with secret content
    f = tmp_path / "time_secret"
    f.write_text("file_secret_value", encoding="utf-8")
    # ensure env not set
    monkeypatch.delenv("MY_OTHER_SECRET", raising=False)
    assert load_shared_secret(env_var_name="MY_OTHER_SECRET", fallback_path=str(f)) == "file_secret_value"
