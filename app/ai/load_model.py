import pandas as pd
import re
from pathlib import Path

# ----------------------------
# Path setup
# ----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]  # app/
RAW_PATH = BASE_DIR / "data" / "raw" / "train.csv"
OUT_PATH = BASE_DIR / "data" / "processed" / "train_clean.csv"

# Create processed folder if not exists
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Load dataset
# ----------------------------
df = pd.read_csv(RAW_PATH)

print("Original shape:", df.shape)
print("Columns:", df.columns)

# ----------------------------
# Detect text column
# ----------------------------
TEXT_COL = None
for col in df.columns:
    if col.lower() in ["text", "comment", "tweet", "content"]:
        TEXT_COL = col
        break

if TEXT_COL is None:
    raise Exception("❌ Text column not found")

print("Using text column:", TEXT_COL)

# ----------------------------
# Text cleaning function
# ----------------------------
def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove mentions & hashtags
    text = re.sub(r"@\w+|#\w+", "", text)

    # Remove emojis ✅ FIXED
    text = re.sub(
        r"["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+",
        "",
        text,               # ✅ MISSING ARGUMENT FIXED
        flags=re.UNICODE,
    )

    # Remove punctuation & numbers
    text = re.sub(r"[^a-z\s]", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ----------------------------
# Apply cleaning
# ----------------------------
df["clean_text"] = df[TEXT_COL].apply(clean_text)

# Drop empty rows
df = df[df["clean_text"].str.len() > 3]

print("After cleaning shape:", df.shape)

# ----------------------------
# Save cleaned dataset
# ----------------------------
df.to_csv(OUT_PATH, index=False)

print("✅ Cleaned data saved to:", OUT_PATH)
