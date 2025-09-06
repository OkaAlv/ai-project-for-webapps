import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY tidak ditemukan di variabel lingkungan.")

genai.configure(api_key=GOOGLE_API_KEY)

try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    raise ValueError(f"Tidak dapat menginisialisasi model. Detail: {e}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Flask AI Chatbot is running"})

@app.route('/ai/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body harus dalam format JSON'}), 400

        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({'error': 'Prompt tidak boleh kosong'}), 400

        full_prompt = (
            "Kamu adalah 'Pustaka AI', asisten perpustakaan virtual..."
            f"\nPertanyaan Pengguna: {prompt}"
        )

        response = model.generate_content(full_prompt)
        ai_answer = response.text

        return jsonify({'response': ai_answer})

    except genai.types.BlockedPromptException as e:
        return jsonify({
            'error': 'Prompt diblokir karena melanggar kebijakan konten.'
        }), 400
    except Exception as e:
        print(f"Error internal server: {e}")
        return jsonify({'error': 'Terjadi kesalahan internal pada server AI.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
