from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"

def load_list(filename):
    path = DATA_DIR / filename
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# Load rule lists
BULLYING_WORDS = load_list("bullying_words.txt")
BULLYING_EMOJIS = load_list("bullying_emojis.txt")

def rule_based_check(text: str) -> bool:
    text_lower = text.lower()

    # Check bad words
    for word in BULLYING_WORDS:
        if word in text_lower:
            return True

    # Check emojis
    for emoji in BULLYING_EMOJIS:
        if emoji in text:
            return True

    return False
