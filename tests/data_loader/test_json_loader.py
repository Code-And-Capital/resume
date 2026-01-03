import json
import pytest
from pathlib import Path

from data_loader.json_loader import JSONDataSource


def test_init_accepts_str_and_path(tmp_path: Path):
    file_path = tmp_path / "data.json"
    file_path.write_text("{}", encoding="utf-8")

    ds_str = JSONDataSource(str(file_path))
    ds_path = JSONDataSource(file_path)

    assert isinstance(ds_str.path, Path)
    assert isinstance(ds_path.path, Path)
    assert ds_str.path == file_path
    assert ds_path.path == file_path


def test_data_property_raises_before_load(tmp_path: Path):
    file_path = tmp_path / "data.json"
    file_path.write_text("{}", encoding="utf-8")

    ds = JSONDataSource(file_path)

    with pytest.raises(RuntimeError, match="not been loaded"):
        _ = ds.data


def test_load_valid_json_returns_dict_and_sets_state(tmp_path: Path):
    content = {"a": 1, "b": {"c": 2}}
    file_path = tmp_path / "data.json"
    file_path.write_text(json.dumps(content), encoding="utf-8")

    ds = JSONDataSource(file_path)
    ds.load()

    assert ds.data == content
    assert ds.data == content


def test_load_raises_file_not_found(tmp_path: Path):
    file_path = tmp_path / "missing.json"
    ds = JSONDataSource(file_path)

    with pytest.raises(FileNotFoundError, match="JSON file not found"):
        ds.load()


def test_load_raises_on_invalid_json(tmp_path: Path):
    file_path = tmp_path / "bad.json"
    file_path.write_text("{ invalid json", encoding="utf-8")

    ds = JSONDataSource(file_path)

    with pytest.raises(json.JSONDecodeError):
        ds.load()


def test_load_raises_if_top_level_is_not_dict(tmp_path: Path):
    file_path = tmp_path / "list.json"
    file_path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    ds = JSONDataSource(file_path)

    with pytest.raises(ValueError, match="Top-level JSON structure must be an object"):
        ds.load()


def test_load_overwrites_previous_data(tmp_path: Path):
    file_path = tmp_path / "data.json"

    file_path.write_text(json.dumps({"a": 1}), encoding="utf-8")
    ds = JSONDataSource(file_path)
    ds.load()
    assert ds.data == {"a": 1}

    file_path.write_text(json.dumps({"b": 2}), encoding="utf-8")
    ds.load()
    assert ds.data == {"b": 2}
