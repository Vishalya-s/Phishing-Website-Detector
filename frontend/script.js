async function analyzeWebsite() {

    const url = document.getElementById("urlInput").value.trim();
    const result = document.getElementById("result");

    // Empty URL check
    if (url === "") {

        result.innerHTML = `
            ⚠️ <strong>Please enter a website URL.</strong>
        `;

        return;
    }

    // Loading state
    result.innerHTML = `
        <h2>🔄 Analyzing Website...</h2>
        <p>
            The AI security system is checking the URL.
        </p>
    `;

    try {

        const response = await fetch(
            "http://localhost:8080/analyze?url=" +
            encodeURIComponent(url)
        );

        if (!response.ok) {
            throw new Error("Server error");
        }

        // Read JSON from Java backend
        const data = await response.json();

        console.log("Security Analysis:", data);

        if (data.error) {
            throw new Error(data.error);
        }


        // =========================
        // VALUES
        // =========================

        const riskScore = Number(data.risk_score);
        const confidence = Number(data.confidence);

        const riskText =
            riskScore < 30
                ? "Low Risk"
                : riskScore < 70
                    ? "Medium Risk"
                    : "High Risk";


        // =========================
        // PHISHING RESULT
        // =========================

        if (data.prediction.includes("Phishing")) {

            result.innerHTML = `

                <div class="danger-result">

                    <h2>🔴 Phishing Website Detected</h2>

                    <p>
                        The machine-learning system detected
                        characteristics associated with a
                        potentially malicious URL.
                    </p>

                </div>


                <div class="security-grid">

                    <div class="security-card">

                        <strong>⚠️ Risk Score</strong>

                        <span>
                            ${riskScore}%
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🤖 Confidence</strong>

                        <span>
                            ${confidence}%
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>📊 Risk Level</strong>

                        <span>
                            ${riskText}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔗 URL Length</strong>

                        <span>
                            ${data.url_length}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔒 HTTPS</strong>

                        <span>
                            ${data.https ? "Yes" : "No"}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🌐 IP Address</strong>

                        <span>
                            ${data.ip_address
                                ? "Detected"
                                : "Not detected"}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>⚠️ Suspicious Keywords</strong>

                        <span>
                            ${data.suspicious_keywords
                                ? "Detected"
                                : "Not detected"}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔢 Digits</strong>

                        <span>
                            ${data.digit_count}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔣 Special Characters</strong>

                        <span>
                            ${data.special_characters}
                        </span>

                    </div>

                </div>


                <p class="warning-text">

                    ⚠️ Avoid entering passwords,
                    payment information, or personal data
                    on this website.

                </p>
            `;

        }


        // =========================
        // LEGITIMATE RESULT
        // =========================

        else {

            result.innerHTML = `

                <div class="safe-result">

                    <h2>🟢 Likely Legitimate Website</h2>

                    <p>
                        The machine-learning system classified
                        this URL as likely legitimate.
                    </p>

                </div>


                <div class="security-grid">

                    <div class="security-card">

                        <strong>⚠️ Risk Score</strong>

                        <span>
                            ${riskScore}%
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🤖 Confidence</strong>

                        <span>
                            ${confidence}%
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>📊 Risk Level</strong>

                        <span>
                            ${riskText}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔗 URL Length</strong>

                        <span>
                            ${data.url_length}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔒 HTTPS</strong>

                        <span>
                            ${data.https ? "Yes" : "No"}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🌐 IP Address</strong>

                        <span>
                            ${data.ip_address
                                ? "Detected"
                                : "Not detected"}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>⚠️ Suspicious Keywords</strong>

                        <span>
                            ${data.suspicious_keywords
                                ? "Detected"
                                : "Not detected"}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔢 Digits</strong>

                        <span>
                            ${data.digit_count}
                        </span>

                    </div>


                    <div class="security-card">

                        <strong>🔣 Special Characters</strong>

                        <span>
                            ${data.special_characters}
                        </span>

                    </div>

                </div>


                <p class="safe-text">

                    ✓ No major phishing characteristics
                    were detected by the current model.

                </p>
            `;
        }


    } catch (error) {

        result.innerHTML = `

            ❌ <strong>
                Unable to analyze the website.
            </strong>

            <br><br>

            Please make sure the Java backend
            is running on port 8080.

        `;

        console.error(error);
    }
}