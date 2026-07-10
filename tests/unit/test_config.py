import os, pytest
from pathlib import Path

def test_no_env_no_file_raises(monkeypatch, tmp_path):
    for k in list(os.environ):
        if k.startswith("BOC_"):
            monkeypatch.delenv(k)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(Exception):
        from importlib import reload
        import boc_mcp.config as c
        reload(c)
        c.load_config()

def test_env_only_minimal(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BOC_BASE_URL", "https://boc.test")
    monkeypatch.setenv("BOC_USERNAME", "admin")
    monkeypatch.setenv("BOC_PASSWORD", "secret")
    from importlib import reload
    import boc_mcp.config as c
    reload(c)
    cfg = c.load_config()
    assert cfg.base_url == "https://boc.test"
    assert cfg.username == "admin"
    assert cfg.password == "secret"
    assert cfg.system_id == "1"
    assert cfg.verify_ssl is True
    assert cfg.request_timeout == 30
    assert cfg.max_retries == 3
    assert cfg.log_level == "INFO"
    assert cfg.mcp.host == "0.0.0.0"
    assert cfg.mcp.port == 8000

def test_yaml_file(monkeypatch, tmp_path):
    yaml_content = """
base_url: "https://boc.yaml"
username: "yamluser"
password: "yamlpass"
request_timeout: 15
mcp:
  port: 9000
"""
    (tmp_path / "config.yaml").write_text(yaml_content, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    for k in list(os.environ):
        if k.startswith("BOC_"):
            monkeypatch.delenv(k)
    from importlib import reload
    import boc_mcp.config as c
    reload(c)
    cfg = c.load_config()
    assert cfg.base_url == "https://boc.yaml"
    assert cfg.request_timeout == 15
    assert cfg.mcp.port == 9000

def test_env_overrides_yaml(monkeypatch, tmp_path):
    (tmp_path / "config.yaml").write_text(
        "base_url: 'https://from.yaml'\nusername: 'u'\npassword: 'p'\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BOC_BASE_URL", "https://from.env")
    from importlib import reload
    import boc_mcp.config as c
    reload(c)
    cfg = c.load_config()
    assert cfg.base_url == "https://from.env"

def test_config_file_env(monkeypatch, tmp_path):
    cfg_file = tmp_path / "custom.yaml"
    cfg_file.write_text(
        "base_url: 'https://custom'\nusername: 'u'\npassword: 'p'\n", encoding="utf-8"
    )
    monkeypatch.setenv("BOC_CONFIG_FILE", str(cfg_file))
    monkeypatch.chdir(tmp_path)
    from importlib import reload
    import boc_mcp.config as c
    reload(c)
    cfg = c.load_config()
    assert cfg.base_url == "https://custom"

def test_base_url_trailing_slash_stripped():
    from boc_mcp.config import AppConfig
    cfg = AppConfig(base_url="https://boc.test/", username="u", password="p")
    assert cfg.base_url == "https://boc.test"
