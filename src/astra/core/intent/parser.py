import re


class Parser:
    """
    Cleans and normalizes user input before
    sending it to the classifier.
    """

    TYPO_FIXES = {
        "what so you know": "what do you know",
        "what so you know about me": "what do you know about me",
        "what so you remember": "what do you remember",
    }

    def normalize(self, text: str) -> str:

        if not text:
            return ""

        # lowercase
        text = text.lower()

        for typo, fix in self.TYPO_FIXES.items():
            if text == typo or text.startswith(typo + " "):
                text = text.replace(typo, fix, 1)
                break

        # remove spaces at beginning/end
        text = text.strip()

        # remove punctuation except math operators and routine delimiters
        text = re.sub(r"[^\w\s*/+\-().:,]", "", text)

        # remove extra spaces
        text = re.sub(r"\s+", " ", text)

        return text