def test_schema_file_exists():
    import pathlib
    assert pathlib.Path("DATA_SCHEMA.yaml").exists(), "DATA_SCHEMA.yaml이 존재해야 합니다."
