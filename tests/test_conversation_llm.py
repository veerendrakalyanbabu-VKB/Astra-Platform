from astra.core.knowledge.llm_responder import conversation_to_turns


def test_conversation_to_turns_maps_speakers():
    convo = [
        {"speaker": "User", "text": "hello"},
        {"speaker": "Astra", "text": "Hi there."},
        {"speaker": "User", "text": "what time is it"},
    ]
    turns = conversation_to_turns(convo)
    assert turns == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Hi there."},
        {"role": "user", "content": "what time is it"},
    ]


def test_conversation_to_turns_limits_window():
    convo = [{"speaker": "User", "text": f"msg {i}"} for i in range(30)]
    turns = conversation_to_turns(convo)
    assert len(turns) == 18
    assert turns[0]["content"] == "msg 12"
