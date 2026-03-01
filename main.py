import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from utils import load_system_prompt

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=api_key)

app = Flask(__name__, static_folder="frontend")
CORS(app)


@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not data or "prompt" not in data:
        return jsonify({"error": "Missing prompt"}), 400

    prompt = data["prompt"].strip()
    level = 4  # תמיד משתמש ב-prompt3.md
    
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    reply = None

    try:
        system_prompt = load_system_prompt(level)
        system_prompt += "\n\nהחזר את התשובה בפורמט JSON בלבד."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        reply = response.choices[0].message.content

        if not reply:
            return jsonify({"error": "Empty response from model"}), 500

        parsed = json.loads(reply)

        if not isinstance(parsed, dict):
            return jsonify({"error": "Model did not return JSON object"}), 500

        return jsonify(parsed)

    except json.JSONDecodeError:
        return jsonify({
            "error": "Invalid JSON from model",
            "raw": reply
        }), 500

    except Exception as err:
        print(f"Error details: {err}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error",
            "details": str(err)
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)