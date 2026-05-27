from chat_context import ChatContext


def test_trim_by_message_count() -> None:
    context = ChatContext(limit_message=2, limit_chars=None)
    context.add_user_message('one')
    context.add_assistant_message('two')
    context.add_user_message('three')

    assert context.messages == [
        {'role': 'assistant', 'content': 'two'},
        {'role': 'user', 'content': 'three'},
    ]


def test_trim_by_char_count_keeps_last_part_of_single_message() -> None:
    context = ChatContext(limit_message=None, limit_chars=4)
    context.add_user_message('abcdef')

    assert context.messages == [{'role': 'user', 'content': 'cdef'}]


def test_prepare_does_not_mutate_original_messages() -> None:
    context = ChatContext(limit_message=None, limit_chars=None)
    context.messages = [{'role': 'user', 'content': 'hello'}]

    pending = context.prepare_with_user_message('world')

    assert pending == [
        {'role': 'user', 'content': 'hello'},
        {'role': 'user', 'content': 'world'},
    ]
    assert context.messages == [{'role': 'user', 'content': 'hello'}]
