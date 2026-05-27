from pathlib import Path

import pytest

from files_utils import FileProcessingError, expand_file_references, read_text_file, split_into_chunks


def test_read_text_file_success(tmp_path: Path) -> None:
    file_path = tmp_path / 'sample.txt'
    file_path.write_text('hello', encoding='utf-8')

    assert read_text_file(str(file_path)) == 'hello'


def test_read_text_file_missing_raises_error(tmp_path: Path) -> None:
    with pytest.raises(FileProcessingError):
        read_text_file(str(tmp_path / 'missing.txt'))


def test_expand_file_references_inserts_file_contents(tmp_path: Path) -> None:
    file_path = tmp_path / 'code.py'
    file_path.write_text('print("ok")', encoding='utf-8')
    message = f'Проверь @::{file_path}::'

    expanded = expand_file_references(message)

    assert 'print("ok")' in expanded


def test_split_into_chunks_by_len() -> None:
    chunks = split_into_chunks('abcdef', char_len=2)
    assert chunks == ['ab', 'cd', 'ef']


def test_split_into_chunks_by_paragraph_size() -> None:
    text = 'a\nb\nc\nd'
    chunks = split_into_chunks(text, paragraph_size=2)
    assert chunks == ['a\nb', 'c\nd']
