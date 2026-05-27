import os
import sys

from chat_context import ChatContext
from config import AppConfig, load_config
from exceptions import LLMServiceError
from file_chunk_mode import parse_file_chunk_command, run_file_chunk_mode
from files_utils import FileProcessingError, expand_file_references
from request_to_llm import request_chat_completion

EXIT_COMMAND = '\\q'
RESET_COMMAND = '/reset'


def print_llm_response(text: str) -> None:
    print(text)


def clear_screen() -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        print('\033[2J\033[H', end='')


def print_config_hint() -> None:
    print(
        'Не найдена конфигурация.\n'
        'Задайте переменные окружения (API_KEY, TEMPERATURE и др.) '
        'или создайте config.yaml в каталоге final_project.',
    )


def handle_user_message(config: AppConfig, context: ChatContext, raw_input: str) -> None:
    try:
        message = expand_file_references(raw_input)
    except FileProcessingError as exc:
        print(exc)
        return

    pending = context.prepare_with_user_message(message)
    stream_state = {'used': False}

    def on_delta(text: str) -> None:
        stream_state['used'] = True
        print(text, end='', flush=True)

    response = request_chat_completion(config, pending, on_delta=on_delta)
    if response is None:
        if stream_state['used']:
            print()
        return

    if stream_state['used']:
        print()
    else:
        print_llm_response(response)
    context.messages = pending
    context.add_assistant_message(response)


def run_chat_loop(config: AppConfig) -> None:
    context = ChatContext(
        limit_message=config.limit_message,
        limit_chars=config.limit_chars,
    )

    while True:
        try:
            user_input = input('>>> ')
        except EOFError:
            break

        stripped = user_input.strip()

        if stripped == EXIT_COMMAND:
            break

        if stripped == RESET_COMMAND:
            context.reset()
            clear_screen()
            continue

        try:
            chunk_cmd = parse_file_chunk_command(stripped)
        except ValueError as exc:
            print(exc)
            continue
        if chunk_cmd is not None:
            try:
                run_file_chunk_mode(config, chunk_cmd, on_response=lambda _: None)
            except LLMServiceError as exc:
                print(exc)
            continue

        if not stripped:
            continue

        try:
            handle_user_message(config, context, user_input)
        except LLMServiceError as exc:
            print(exc)


def main() -> None:
    try:
        config = load_config()
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    if config is None:
        print_config_hint()
        sys.exit(1)

    run_chat_loop(config)


if __name__ == '__main__':
    main()
