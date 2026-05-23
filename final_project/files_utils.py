import re
from pathlib import Path

MAX_FILE_SIZE = 5 * 1024 * 1024

FILE_REF_PATTERN = re.compile(r'@::(.+?)::')


class FileProcessingError(Exception):
    pass


def read_text_file(path_str: str) -> str:
    path = Path(path_str).expanduser()
    if not path.is_file():
        raise FileProcessingError(f'Файл не найден: {path}')
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise FileProcessingError(
            f'Файл {path} слишком большой ({size} байт). Максимум: {MAX_FILE_SIZE} байт.',
        )
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError as exc:
        raise FileProcessingError(f'Файл {path} не является текстовым (UTF-8).') from exc


def expand_file_references(text: str) -> str:
    result = text
    for match in FILE_REF_PATTERN.finditer(text):
        path_str = match.group(1)
        content = read_text_file(path_str)
        replacement = f'\n{content}'
        result = result.replace(match.group(0), replacement, 1)
    return result


def split_into_chunks(
    text: str,
    *,
    paragraph_size: int | None = None,
    char_len: int | None = None,
) -> list[str]:
    if char_len is not None:
        chunks: list[str] = []
        for index in range(0, len(text), char_len):
            chunk = text[index : index + char_len]
            if chunk:
                chunks.append(chunk)
        return chunks or ['']

    paragraphs = text.splitlines()
    if paragraph_size is None or paragraph_size <= 1:
        return paragraphs if paragraphs else ['']

    grouped: list[str] = []
    buffer: list[str] = []
    for paragraph in paragraphs:
        buffer.append(paragraph)
        if len(buffer) >= paragraph_size:
            grouped.append('\n'.join(buffer))
            buffer = []
    if buffer:
        grouped.append('\n'.join(buffer))
    return grouped or ['']
