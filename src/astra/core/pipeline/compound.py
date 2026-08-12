COMPOUND_SEPARATORS = (
    " and then ",
    " and also ",
    " then ",
    " and ",
)


def split_compound_command(text: str) -> list:
    normalized = text.strip().lower()

    for separator in COMPOUND_SEPARATORS:
        if separator in normalized:
            parts = normalized.split(separator)
            return [part.strip() for part in parts if part.strip()]

    return [text.strip()]
