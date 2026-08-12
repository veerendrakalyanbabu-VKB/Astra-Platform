from astra.core.intent.nlu_enhancer import NaturalLanguageEnhancer


def test_nlu_open_app():
    nlu = NaturalLanguageEnhancer()
    result = nlu.enhance("can you open chrome")

    assert result.intent == "OPEN_APP"
    assert result.entities["application"] == "chrome"
    assert result.confidence == 0.85


def test_nlu_remember():
    nlu = NaturalLanguageEnhancer()
    result = nlu.enhance("please remember that i like pizza")

    assert result.intent == "SAVE_MEMORY"
    assert "pizza" in result.entities["text"]


def test_nlu_get_time():
    nlu = NaturalLanguageEnhancer()
    result = nlu.enhance("tell me the time")

    assert result.intent == "GET_TIME"


def test_nlu_list_memory():
    nlu = NaturalLanguageEnhancer()
    result = nlu.enhance("what do you know")

    assert result.intent == "LIST_MEMORY"


def test_nlu_help_me():
    nlu = NaturalLanguageEnhancer()
    result = nlu.enhance("can you help me to cook")

    assert result.intent == "ASK_KNOWLEDGE"
    assert result.entities["query"] == "cook"


def test_nlu_help_me_cook_short():
    nlu = NaturalLanguageEnhancer()
    result = nlu.enhance("help me cook")

    assert result.intent == "ASK_KNOWLEDGE"
    assert result.entities["query"] == "cook"


def test_nlu_greeting():
    nlu = NaturalLanguageEnhancer()
    result = nlu.enhance("hey astra")

    assert result.intent == "ASK_KNOWLEDGE"
    assert result.entities["query"] == "greeting"


def test_nlu_intent_engine_integration():
    from astra.core.intent.intent_engine import IntentEngine

    engine = IntentEngine()
    result = engine.process("Can you open notepad")

    assert result.intent == "OPEN_APP"
    assert result.entities["application"] == "notepad"
