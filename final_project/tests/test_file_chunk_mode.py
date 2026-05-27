import pytest

from file_chunk_mode import parse_file_chunk_command


def test_parse_file_chunk_command_basic() -> None:
    parsed = parse_file_chunk_command('/filechunk -y paragraph=3 len=120')
    assert parsed == {'auto': True, 'paragraph_size': 3, 'char_len': 120}


def test_parse_file_chunk_command_returns_none_for_regular_message() -> None:
    assert parse_file_chunk_command('hello') is None


def test_parse_file_chunk_command_rejects_non_int() -> None:
    with pytest.raises(ValueError):
        parse_file_chunk_command('/filechunk len=abc')


def test_parse_file_chunk_command_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError):
        parse_file_chunk_command('/filechunk paragraph=0')


def test_parse_file_chunk_command_rejects_unknown_option() -> None:
    with pytest.raises(ValueError):
        parse_file_chunk_command('/filechunk speed=fast')
