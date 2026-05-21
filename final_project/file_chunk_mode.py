import re

from collections.abc import Callable

from config import AppConfig
from files_utils import FileProcessingError, read_text_file, split_into_chunks
from request_to_llm import request_chunk_completion

EXIT_COMMAND = '\\q'

CHUNK_CMD_PATTERN = re.compile(
    r'^/?file[_-]?chunk(?:\s+(.*))?$',
    re.IGNORECASE,
)


def parse_file_chunk_command(raw: str) -> dict[str, int | bool | None] | None:
    match = CHUNK_CMD_PATTERN.match(raw.strip())
    if not match:
        return None

    args_str = (match.group(1) or '').strip()
    auto = False
    paragraph_size: int | None = None
    char_len: int | None = None

    for token in args_str.split():
        if token == '-y':
            auto = True
        elif token.startswith('paragraph='):
            paragraph_size = int(token.split('=', 1)[1])
        elif token.startswith('len='):
            char_len = int(token.split('=', 1)[1])

    return {
        'auto': auto,
        'paragraph_size': paragraph_size,
        'char_len': char_len,
    }


def _prompt_line(prompt: str) -> str | None:
    value = input(prompt)
    if value.strip() == EXIT_COMMAND:
        return None
    return value


def run_file_chunk_mode(
    config: AppConfig,
    command_args: dict[str, int | bool | None],
    on_response: Callable[[str], None],
) -> None:
    path_input = _prompt_line('Введите путь до файла\n')
    if path_input is None:
        return

    try:
        file_text = read_text_file(path_input.strip())
    except FileProcessingError as exc:
        print(exc)
        return

    user_prompt = _prompt_line(
        'Принято. Что нужно сделать для каждого фрагмента (User Prompt)?\n',
    )
    if user_prompt is None:
        return

    chunks = split_into_chunks(
        file_text,
        paragraph_size=command_args.get('paragraph_size'),
        char_len=command_args.get('char_len'),
    )

    print('Принято. Начинаю обработку:')

    for index, chunk in enumerate(chunks):
        if index > 0 and not command_args['auto']:
            while True:
                continuation = input()
                if continuation.strip() == EXIT_COMMAND:
                    return
                if continuation == '':
                    break

        response = request_chunk_completion(config, user_prompt, chunk)
        if response is None:
            return
        on_response(response)

    print('Обработка файла завершена.')
