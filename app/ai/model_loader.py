import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]   # app/
TRAIN_CLEAN_PATH = BASE_DIR / "data" / "processed" / "train_clean.csv"
COMMENTS_PATH = BASE_DIR / "data" / "processed" / "comments_formatted.csv"  # new file

MODEL_PATH = BASE_DIR / "ai" / "bullying_model.pkl"
VECT_PATH = BASE_DIR / "ai" / "tfidf_vectorizer.pkl"

# ----------------------------
# Load datasets
# ----------------------------
df_train = pd.read_csv(TRAIN_CLEAN_PATH)
df_comments = pd.read_csv(COMMENTS_PATH)

print("Train dataset loaded:", df_train.shape)
print("Comments dataset loaded:", df_comments.shape)

# ----------------------------
# Concatenate datasets
# ----------------------------
# Make sure both have 'clean_text' and 'class' columns
for col in ["clean_text", "class"]:
    if col not in df_train.columns or col not in df_comments.columns:
        raise Exception(f"❌ Column {col} missing in one of the CSVs")

df = pd.concat([df_train, df_comments], ignore_index=True)
print("Combined dataset shape:", df.shape)

# ----------------------------
# Create labels
# ----------------------------
# Binary bullying classification
# 1 = bullying (hate + offensive)
# 0 = non-bullying (neither)
df["label"] = df["class"].apply(lambda x: 0 if x == 2 else 1)

print("Label distribution:")
print(df["label"].value_counts())

# ----------------------------
# Split train / test
# ----------------------------
X = df["clean_text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Train size:", len(X_train))
print("Test size:", len(X_test))

# ----------------------------
# TF-IDF Vectorization
# ----------------------------
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english"
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("TF-IDF shape:", X_train_vec.shape)

# ----------------------------
# Train model
# ----------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# ----------------------------
# Evaluate
# ----------------------------
y_pred = model.predict(X_test_vec)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# ----------------------------
# Save model + vectorizer
# ----------------------------
joblib.dump(model, MODEL_PATH)
joblib.dump(vectorizer, VECT_PATH)

print("✅ bullying_model.pkl created")
print("✅ tfidf_vectorizer.pkl created")
