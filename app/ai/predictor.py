import joblib
from pathlib import Path
import numpy as np
import re

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "../data/raw"

MODEL_PATH = BASE_DIR / "bullying_model.pkl"
VECT_PATH = BASE_DIR / "tfidf_vectorizer.pkl"

# ----------------------------
# Load ML model & vectorizer
# ----------------------------
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECT_PATH)

# ----------------------------
# Load emojis from text file
# ----------------------------
EMOJI_FILE = DATA_DIR / "bullying_emojis.txt"
EMOJI_MAP = {}

with open(EMOJI_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or " " not in line:
            continue
        emoji, word = line.split(maxsplit=1)
        EMOJI_MAP[emoji] = word.lower()

# ----------------------------
# Load bullying words
# ----------------------------
WORDS_FILE = DATA_DIR / "bullying_words.txt"
with open(WORDS_FILE, "r", encoding="utf-8") as f:
    BULLYING_WORDS = set(line.strip().lower() for line in f if line.strip())




def restore_masked_words(raw_text: str) -> str:
    """
    Restore masked abusive WORDS using raw text
    before '*' removal.
    """
    text = raw_text.lower()

    word_patterns = {
        r"f\*+l": "fool",
        r"m\*+r\*+n": "moron",
        r"cl\*+wn": "clown",
        r"p\*+thetic": "pathetic",
        r"l\*+ser": "loser",
        r"tr\*+sh": "trash",
        r"sc\*+m": "scum",
        r"d\*+mb": "dumb",
        r"s\*+upid": "stupid",
        r"b\*+tch": "bitch",
        r"sh\*+t": "shit",
        r"f\*+ off":"fuck off"
        
    }

    for pattern, replacement in word_patterns.items():
        text = re.sub(pattern, replacement, text)

    return text

# ----------------------------
# Text normalization
# ----------------------------
def normalize_text(text: str) -> str:
    """
    Normalize obfuscated abusive text safely.
    """
    # 🔥 FIRST: restore masked phrases from RAW text
    text = restore_masked_words(text)

    original = text
    text = text.lower()

    had_masking = bool(re.search(r"[\*\$!@1]", original))

    # Character substitutions
    char_map = {
        '@': 'a',
        '$': 's',
        '1': 'i',
        '0': 'o',
        '3': 'e',
        '4': 'a',
        '!': 'i'
    }

    for k, v in char_map.items():
        text = text.replace(k, v)

    # Remove separators & stars
    text = re.sub(r"[._\-|]", "", text)
    text = re.sub(r"\*", "", text)

    # ---- Word-level restoration (ONLY if masking existed) ----
    if had_masking:
        word_patterns = {
            r"\bfck\b": "fuck",
            r"\bdmb\b": "dumb",
            r"\bstpd\b": "stupid",
            r"\bsht\b": "shit",
            r"\bbtch\b": "bitch",
            r"\ba\b": "ass",
            r"\bid\b":"idiot",
            r"\bmor\b":"moron"

        }

        for p, r in word_patterns.items():
            text = re.sub(p, r, text)

    return text




# ----------------------------
# Clean text for ML
# ----------------------------
def clean_text(text: str) -> str:
    """
    Clean text for ML model input.
    """
    text = normalize_text(text)

    # Replace emojis with words
    for emoji, word in EMOJI_MAP.items():
        text = text.replace(emoji, f" {word} ")

    # Remove non-alphanumeric characters
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text

# ----------------------------
# Rule-based detection
# ----------------------------
def rule_based_check(text: str) -> bool:
    """
    Detect bullying using word list and emojis.
    """
    normalized = normalize_text(text)
    words = set(normalized.split())
    word_flag = bool(words & BULLYING_WORDS)

    emoji_flag = any(emoji in text for emoji in EMOJI_MAP)

    return word_flag or emoji_flag

# ----------------------------
# Severity detection
# ----------------------------
SEVERE_PHRASES = {
    "kill yourself",
    "you should die",
    "go die",
    "drop dead"
}

def severity_check(text: str) -> str:
    """
    Return severity level.
    """
    t = normalize_text(text)

    if any(phrase in t for phrase in SEVERE_PHRASES):
        return "severe"

    if rule_based_check(text):
        return "bullying"

    return "normal"

# ----------------------------
# Prediction function
# ----------------------------
def predict_data(text: str, threshold: float = 0.85):
    """
    Predict bullying using ML + rules.
    """
    cleaned = clean_text(text)

    # Rule-based
    rule_detected = rule_based_check(text)

    # ML-based
    X = vectorizer.transform([cleaned])
    prob = model.predict_proba(X)[0]
    confidence = float(np.max(prob))
    prediction = int(model.predict(X)[0])
    ml_detected = prediction == 1 and confidence >= threshold

    bullying = ml_detected or rule_detected
    severity = severity_check(text)

    sources = []
    if ml_detected:
        sources.append("ml")
    if rule_detected:
        sources.append("rule")

    return {
        "bullying": bullying,
        "severity": severity,
        "confidence": round(confidence, 3),
        "source": " + ".join(sources) if sources else "none",
        "cleaned_text": cleaned
    }

# ----------------------------
# Manual testing
# ----------------------------
if __name__ == "__main__":
    print("Bullying Comment Predictor (type 'exit' to quit)")
    while True:
        comment = input("Enter comment: ")
        if comment.lower() == "exit":
            break
        result = predict_data(comment)
        print(result)
