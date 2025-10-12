import pathlib

import yaml


def test_end2end_load_config() -> None:
    config_path = pathlib.Path("CONFIG.yaml")
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert "app" in cfg, "CONFIG.yaml에 app 섹션이 필요합니다."
