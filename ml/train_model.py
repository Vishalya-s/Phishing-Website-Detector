import pandas as pd
import numpy as np
import pickle
import re
from urllib.parse import urlparse

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

from scipy.sparse import hstack, csr_matrix


# ==========================================
# 1. LOAD DATASET
# ==========================================

print("Loading dataset...")

data = pd.read_csv(
    "urlset.csv",
    encoding="latin1",
    engine="python",
    on_bad_lines="skip"
)

data = data.dropna(subset=["domain", "label"])

X = data["domain"].astype(str).str.strip()

y = pd.to_numeric(data["label"], errors="coerce")

valid = y.notna()

X = X[valid]
y = y[valid].astype(int)

print("Valid rows:", len(X))


# ==========================================
# 2. URL STRUCTURAL FEATURES
# ==========================================

def extract_features(url):

    url = str(url).strip()

    # Add scheme temporarily if missing
    parse_url = url

    if not parse_url.startswith(("http://", "https://")):
        parse_url = "http://" + parse_url

    parsed = urlparse(parse_url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    features = [

        # Overall URL
        len(url),

        # Hostname
        len(hostname),
        hostname.count("."),
        hostname.count("-"),
        hostname.count("_"),
        sum(c.isdigit() for c in hostname),

        # Path
        len(path),
        path.count("/"),
        path.count("-"),
        path.count("_"),

        # Query
        len(query),
        query.count("="),
        query.count("&"),

        # Special characters
        url.count("@"),
        url.count("%"),

        # Protocol
        int(url.lower().startswith("https://")),
        int(url.lower().startswith("http://")),

        # IP address
        int(bool(
            re.match(
                r"^(?:\d{1,3}\.){3}\d{1,3}$",
                hostname
            )
        )),

        # Suspicious keywords
        int(bool(re.search(
            r"login|signin|verify|verification|secure|account|update|"
            r"password|confirm|bank|paypal|credential",
            url.lower()
        ))),

        # Number of digits
        sum(c.isdigit() for c in url),

        # Number of letters
        sum(c.isalpha() for c in url)
    ]

    return features


print("Extracting URL features...")

structural_features = np.array([
    extract_features(url)
    for url in X
])

print(
    "Structural features:",
    structural_features.shape
)


# ==========================================
# 3. TRAIN / TEST SPLIT
# ==========================================

(
    X_train,
    X_test,
    y_train,
    y_test,
    sf_train,
    sf_test
) = train_test_split(
    X,
    y,
    structural_features,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training URLs:", len(X_train))
print("Testing URLs:", len(X_test))


# ==========================================
# 4. TF-IDF FEATURES
# ==========================================

print("Creating TF-IDF features...")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 5),
    min_df=2,
    max_features=100000,
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)

X_test_tfidf = vectorizer.transform(X_test)


# ==========================================
# 5. SCALE STRUCTURAL FEATURES
# ==========================================

print("Scaling structural features...")

scaler = StandardScaler()

sf_train_scaled = scaler.fit_transform(sf_train)

sf_test_scaled = scaler.transform(sf_test)


# Convert to sparse matrices

sf_train_sparse = csr_matrix(sf_train_scaled)

sf_test_sparse = csr_matrix(sf_test_scaled)


# ==========================================
# 6. COMBINE FEATURES
# ==========================================

print("Combining features...")

X_train_final = hstack([
    X_train_tfidf,
    sf_train_sparse
])

X_test_final = hstack([
    X_test_tfidf,
    sf_test_sparse
])

print(
    "Final training features:",
    X_train_final.shape
)


# ==========================================
# 7. TRAIN MODEL
# ==========================================

print("Training improved model...")

model = LogisticRegression(
    max_iter=3000,
    C=2
)

model.fit(
    X_train_final,
    y_train
)

print("Training completed!")


# ==========================================
# 8. EVALUATE MODEL
# ==========================================

y_pred = model.predict(X_test_final)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print()
print("==========================================")
print("MODEL ACCURACY")
print("==========================================")

print(
    f"{accuracy * 100:.2f}%"
)

print()
print("Classification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Legitimate",
            "Phishing"
        ]
    )
)


# ==========================================
# 9. SAVE MODEL
# ==========================================

print("Saving model...")

with open(
    "phishing_model.pkl",
    "wb"
) as file:

    pickle.dump(
        model,
        file
    )


# Save TF-IDF vectorizer

with open(
    "vectorizer.pkl",
    "wb"
) as file:

    pickle.dump(
        vectorizer,
        file
    )


# Save scaler

with open(
    "scaler.pkl",
    "wb"
) as file:

    pickle.dump(
        scaler,
        file
    )


print()
print("==========================================")
print("MODEL SAVED SUCCESSFULLY")
print("==========================================")