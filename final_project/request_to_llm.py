import asyncio
from collections.abc import AsyncIterator, Callable

from google import genai
from google.genai import types

from config import AppConfig
from exceptions import LLMServiceError


def _build_client(config: AppConfig) -> genai.Client:
    return genai.Client(api_key=config.api_key)


def _generate_config(config: AppConfig) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=config.system_prompt,
        temperature=config.temperature,
    )


def _to_gemini_contents(history: list[dict[str, str]]) -> list[types.Content]:
    role_map = {
        'user': 'user',
        'assistant': 'model',
    }
    contents: list[types.Content] = []
    for msg in history:
        contents.append(
            types.Content(
                role=role_map[msg['role']],
                parts=[types.Part.from_text(text=msg['content'])],
            ),
        )
    return contents


def _generate_text(
    client: genai.Client,
    *,
    model: str,
    contents: list[types.Content],
    config: types.GenerateContentConfig,
    on_delta: Callable[[str], None] | None = None,
) -> str | None:
    try:
        return asyncio.run(
            _generate_text_async(
                client,
                model=model,
                contents=contents,
                config=config,
                on_delta=on_delta,
            ),
        )
    except KeyboardInterrupt:
        return None
    except Exception as exc:
        raise LLMServiceError(message='Ошибка при обращении к Gemini API (Turn On vPN)') from exc


async def _generate_text_async(
    client: genai.Client,
    *,
    model: str,
    contents: list[types.Content],
    config: types.GenerateContentConfig,
    on_delta: Callable[[str], None] | None = None,
) -> str | None:
    try:
        response_text = ''
        async for text_delta in _stream_text_deltas(
            client,
            model=model,
            contents=contents,
            config=config,
        ):
            response_text += text_delta
            if on_delta is not None:
                on_delta(text_delta)
    except KeyboardInterrupt:
        return None
    except Exception as exc:
        raise LLMServiceError(message='Ошибка при обращении к Gemini API (Turn On vPN)') from exc
    return response_text


async def _stream_text_deltas(
    client: genai.Client,
    *,
    model: str,
    contents: list[types.Content],
    config: types.GenerateContentConfig,
) -> AsyncIterator[str]:
    stream = await client.aio.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config,
    )
    async for chunk in stream:
        text_delta = chunk.text or ''
        if text_delta:
            yield text_delta


def request_chat_completion(
    config: AppConfig,
    history: list[dict[str, str]],
    on_delta: Callable[[str], None] | None = None,
) -> str | None:
    client = _build_client(config)
    return _generate_text(
        client,
        model=config.model,
        contents=_to_gemini_contents(history),
        config=_generate_config(config),
        on_delta=on_delta,
    )


def request_chunk_completion(
    config: AppConfig,
    user_prompt: str,
    chunk_text: str,
    on_delta: Callable[[str], None] | None = None,
) -> str | None:
    client = _build_client(config)
    contents = [
        types.Content(
            role='user',
            parts=[types.Part.from_text(text=f'{user_prompt}\n\n{chunk_text}')],
        ),
    ]
    return _generate_text(
        client,
        model=config.model,
        contents=contents,
        config=_generate_config(config),
        on_delta=on_delta,
    )
