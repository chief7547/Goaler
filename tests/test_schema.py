import pathlib
import yaml


def test_schema_file_exists():
    assert pathlib.Path("DATA_SCHEMA.yaml").exists(), "DATA_SCHEMA.yaml이 존재해야 합니다."


def test_schema_contains_boss_stages():
    schema = yaml.safe_load(pathlib.Path("DATA_SCHEMA.yaml").read_text(encoding="utf-8"))
    assert "boss_stages" in schema, "boss_stages 스키마가 정의되어야 합니다."
    props = schema["boss_stages"].get("properties", {})
    expected = {"boss_id", "goal_id", "title", "success_criteria", "stage_order", "target_week"}
    assert expected.issubset(props.keys()), "boss_stages 필수 속성이 누락되었습니다."
