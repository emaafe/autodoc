from __future__ import annotations

from analyzer.changed_files import ChangedFile, filter_analyzable_files, is_productive_java_file


def test_is_productive_java_file_accepts_main_java_file() -> None:
    assert is_productive_java_file("src/main/java/com/example/UserService.java") is True


def test_is_productive_java_file_rejects_test_file() -> None:
    assert is_productive_java_file("src/test/java/com/example/UserServiceTest.java") is False


def test_is_productive_java_file_rejects_non_java_file() -> None:
    assert is_productive_java_file("src/main/java/com/example/config.yml") is False


def test_filter_analyzable_files_keeps_only_valid_project_files() -> None:
    files = [
        ChangedFile("src/main/java/com/example/A.java", "added"),
        ChangedFile("src/main/java/com/example/B.java", "modified"),
        ChangedFile("src/test/java/com/example/ATest.java", "modified"),
        ChangedFile("README.md", "modified"),
        ChangedFile("src/main/java/com/example/C.java", "removed"),
    ]

    result = filter_analyzable_files(files)

    assert result == [
        "src/main/java/com/example/A.java",
        "src/main/java/com/example/B.java",
    ]