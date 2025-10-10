def test_end2end_load_config():
    import yaml, pathlib
    cfg = yaml.safe_load(open("CONFIG.yaml","r",encoding="utf-8"))
    assert "app" in cfg, "CONFIG.yaml에 app 섹션이 필요합니다."
