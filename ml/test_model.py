import pickle

# Load trained model
with open("phishing_model.pkl", "rb") as file:
    model = pickle.load(file)

# Load vectorizer
with open("vectorizer.pkl", "rb") as file:
    vectorizer = pickle.load(file)


def predict_url(url):
    # Convert URL into the same features used during training
    url_vectorized = vectorizer.transform([url])

    # Make prediction
    prediction = model.predict(url_vectorized)[0]

    if prediction == 1:
        return "🔴 Phishing Website"
    else:
        return "🟢 Legitimate Website"


# Test URLs
urls = [
    "https://google.com",
    "http://secure-login-account.com",
    "https://github.com"
]

for url in urls:
    result = predict_url(url)

    print("\nURL:", url)
    print("Result:", result)