import os
import uuid
import math
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_groq_score(text):
    prompt = f"""You are an AI detection tool. Rate the likelihood that the following text was written by AI, on a scale from 0.0 to 1.0.
0.0 means definitely human-written, 1.0 means definitely AI-generated.
Respond with a single number between 0.0 and 1.0 and nothing else.

Text:
{text}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )

    raw = response.choices[0].message.content.strip()
    score = float(raw)
    return max(0.0, min(1.0, score))

def get_stylometric_score(text):
    # Split into sentences roughly
    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    words = text.lower().split()

    # Edge case: too short to analyze meaningfully
    if len(sentences) < 2 or len(words) < 10:
        return 0.5  # uncertain

    # Sentence length variance (high variance = more human-like)
    lengths = [len(s.split()) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)

    # Normalize variance: cap at 50, higher variance = lower AI score
    normalized_variance = min(variance / 50.0, 1.0)
    variance_score = 1.0 - normalized_variance  # high variance = low AI likelihood

    # Type-token ratio (high TTR = more diverse vocab = more human-like)
    ttr = len(set(words)) / len(words)
    ttr_score = 1.0 - ttr  # high TTR = low AI likelihood

    # Combine the two metrics equally
    stylometric_score = (variance_score + ttr_score) / 2
    return round(max(0.0, min(1.0, stylometric_score)), 4)

def get_label(score):
    if score >= 0.7:
        return "This content has been flagged as AI-generated. Strong confidence for AI origins."
    elif score >= 0.4:
        return "The system is not confident about authorship. May be AI-generated, human-generated, or both (could be AI text slightly altered by a human)."
    else:
        return "This content appears to be human-generated. No strong indications of AI use."

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    text = data.get("text", "")
    creator_id = data.get("creator_id", "unknown")
    content_id = str(uuid.uuid4())

    groq_score = get_groq_score(text)
    stylometric_score = get_stylometric_score(text)

    combined_score = round((0.6 * groq_score) + (0.4 * stylometric_score), 4)

    if combined_score >= 0.7:
        attribution = "likely_ai"
    elif combined_score >= 0.4:
        attribution = "uncertain"
    else:
        attribution = "likely_human"

    label = get_label(combined_score)

    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "groq_score": groq_score,
        "stylometric_score": stylometric_score,
        "confidence": combined_score,
        "label": label
    })

if __name__ == "__main__":
    app.run(debug=True)