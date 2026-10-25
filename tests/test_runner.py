"""Verify portable input paths without access to private course data."""
from run_project import resolve_input_path


def test_relative_path_is_relative_to_repository_not_current_directory(tmp_path, monkeypatch):
    repository = tmp_path / "project"
    repository.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    assert resolve_input_path("data/raw/example.csv", repository) == repository / "data/raw/example.csv"


def test_absolute_override_is_preserved(tmp_path):
    assert resolve_input_path(str(tmp_path / "example.csv")) == tmp_path / "example.csv"
