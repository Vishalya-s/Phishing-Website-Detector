import sys
import json
import re
import pickle
from urllib.parse import urlparse


# --------------------------------------------------
# Trusted domains
# --------------------------------------------------

TRUSTED_DOMAINS = {
    "google.com",
    "github.com",
    "microsoft.com",
    "wikipedia.org",
    "amazon.com"
}


# --------------------------------------------------
# Suspicious keywords
# --------------------------------------------------

SUSPICIOUS_KEYWORDS = [
    "login",
    "signin",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "confirm",
    "password",
    "bank",
    "paypal",
    "wallet",
    "free",
    "bonus",
    "claim",
    "urgent"
]


# --------------------------------------------------
# Extract URL features
# --------------------------------------------------

def extract_features(url):

    parsed = urlparse(url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    # IMPORTANT:
    # Check the beginning of the URL only.
    # http:// -> False
    # https:// -> True
    is_https = url.lower().startswith("https://")
    is_http = url.lower().startswith("http://")

    # Check if hostname is an IP address
    ip_address = bool(
        re.fullmatch(
            r"\d{1,3}(\.\d{1,3}){3}",
            hostname
        )
    )

    # Suspicious keyword detection
    url_lower = url.lower()

    suspicious_keywords = any(
        keyword in url_lower
        for keyword in SUSPICIOUS_KEYWORDS
    )

    # 21 structural URL features
    features = [

        len(url),                         # 1
        len(hostname),                    # 2
        hostname.count("."),              # 3
        hostname.count("-"),              # 4
        hostname.count("_"),              # 5
        sum(c.isdigit() for c in hostname),  # 6

        len(path),                        # 7
        path.count("/"),                  # 8
        path.count("-"),                  # 9
        path.count("_"),                  # 10

        len(query),                       # 11
        query.count("="),                 # 12
        query.count("&"),                 # 13

        url.count("@"),                   # 14
        url.count("%"),                   # 15

        int(is_https),                    # 16
        int(is_http),                     # 17

        int(ip_address),                  # 18

        int(suspicious_keywords),         # 19

        sum(c.isdigit() for c in url),    # 20
        sum(c.isalpha() for c in url)     # 21
    ]

    return features


# --------------------------------------------------
# Check trusted domain
# --------------------------------------------------

def is_trusted_domain(hostname):

    hostname = hostname.lower().strip(".")

    # Remove www.
    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname in TRUSTED_DOMAINS


# --------------------------------------------------
# Main prediction function
# --------------------------------------------------

def predict(url):

    url = url.strip()

    # Add scheme if user enters only a domain
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    hostname = parsed.hostname or ""

    # Remove www. for trusted-domain checking
    clean_hostname = hostname.lower().strip(".")

    if clean_hostname.startswith("www."):
        clean_hostname = clean_hostname[4:]


    # --------------------------------------------------
    # Basic URL information
    # --------------------------------------------------

    is_https = url.lower().startswith("https://")

    ip_address = bool(
        re.fullmatch(
            r"\d{1,3}(\.\d{1,3}){3}",
            hostname
        )
    )

    url_lower = url.lower()

    suspicious_keywords = any(
        keyword in url_lower
        for keyword in SUSPICIOUS_KEYWORDS
    )

    digit_count = sum(
        c.isdigit()
        for c in url
    )

    special_characters = sum(
        not c.isalnum() and not c.isspace()
        for c in url
    )


    # --------------------------------------------------
    # Trusted domain handling
    # --------------------------------------------------

    if is_trusted_domain(hostname):

        return {

            "prediction": "Legitimate",

            "confidence": 99.0,

            "risk_score": 1.0,

            "url": url,

            "https": is_https,

            "url_length": len(url),

            "ip_address": ip_address,

            "suspicious_keywords": suspicious_keywords,

            "digit_count": digit_count,

            "special_characters": special_characters

        }


    # --------------------------------------------------
    # Load ML model
    # --------------------------------------------------

    try:

        with open(
            "phishing_model.pkl",
            "rb"
        ) as file:

            model = pickle.load(file)


        with open(
            "vectorizer.pkl",
            "rb"
        ) as file:

            vectorizer = pickle.load(file)


        with open(
            "scaler.pkl",
            "rb"
        ) as file:

            scaler = pickle.load(file)


    except Exception as error:

        return {
            "error": f"Unable to load ML model: {error}"
        }


    # --------------------------------------------------
    # Extract features
    # --------------------------------------------------

    structural_features = extract_features(url)


    # Convert structural features
    # into the format expected by scaler

    scaled_features = scaler.transform(
        [structural_features]
    )


    # --------------------------------------------------
    # TF-IDF URL features
    # --------------------------------------------------

    text_features = vectorizer.transform(
        [url]
    )


    # --------------------------------------------------
    # Combine features
    # --------------------------------------------------

    try:

        from scipy.sparse import hstack

        combined_features = hstack(
            [
                scaled_features,
                text_features
            ]
        )

    except Exception as error:

        return {
            "error": f"Unable to combine features: {error}"
        }


    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    try:

        prediction_value = model.predict(
            combined_features
        )[0]

        probabilities = model.predict_proba(
            combined_features
        )[0]

    except Exception as error:

        return {
            "error": f"Prediction failed: {error}"
        }


    # --------------------------------------------------
    # Convert prediction
    # --------------------------------------------------

    phishing_probability = float(
        probabilities[1]
    )

    legitimate_probability = float(
        probabilities[0]
    )


    if prediction_value == 1:

        prediction = "Phishing"

        confidence = phishing_probability * 100

    else:

        prediction = "Legitimate"

        confidence = legitimate_probability * 100


    # Risk score represents the model's
    # estimated phishing probability.

    risk_score = phishing_probability * 100


    # --------------------------------------------------
    # Return JSON-compatible result
    # --------------------------------------------------

    return {

        "prediction": prediction,

        "confidence": round(
            confidence,
            2
        ),

        "risk_score": round(
            risk_score,
            2
        ),

        "url": url,

        "https": is_https,

        "url_length": len(url),

        "ip_address": ip_address,

        "suspicious_keywords": suspicious_keywords,

        "digit_count": digit_count,

        "special_characters": special_characters

    }


# --------------------------------------------------
# Command-line execution
# --------------------------------------------------

if __name__ == "_main_":

    if len(sys.argv) < 2:

        print(
            json.dumps(
                {
                    "error": "Please provide a URL"
                }
            )
        )

        sys.exit(1)


    input_url = sys.argv[1]

    result = predict(input_url)

    print(
        json.dumps(result)
    )