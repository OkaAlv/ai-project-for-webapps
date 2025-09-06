import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__)
# Mengizinkan permintaan dari semua origin. Untuk produksi yang lebih aman,
# Anda bisa membatasinya ke domain web PHP Anda, contoh: CORS(app, origins="https://perpus-anda.com")
CORS(app)

# Muat variabel lingkungan dari file .env (hanya untuk pengembangan lokal)
load_dotenv()

# --- KONFIGURASI API KEY ---
# Mengambil API Key dari variabel lingkungan.
# Di hosting (seperti Render), Anda akan mengatur ini langsung di dashboard, bukan dari file .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY tidak ditemukan di variabel lingkungan.")

# Konfigurasi library google-generativeai dengan API Key Anda
genai.configure(api_key=GOOGLE_API_KEY)

# --- PERBAIKAN KRITIS DI SINI ---
# Inisialisasi model Gemini. Menggunakan nama model resmi yang benar.
# 'gemini-1.5-flash-latest' adalah model Flash terbaru yang direkomendasikan.
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    raise ValueError(f"Tidak dapat menginisialisasi model. Pastikan nama model benar dan API key valid. Detail: {e}")
# ---------------------------------

@app.route('/ai/chat', methods=['POST'])
def chat():
    """
    Endpoint untuk berinteraksi dengan model AI.
    Menerima 'prompt' dari request JSON dan mengembalikan respons dari AI.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body harus dalam format JSON'}), 400

        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({'error': 'Prompt tidak boleh kosong'}), 400

        # Menambahkan persona asisten perpustakaan ke prompt pengguna
        full_prompt = (
            "Kamu adalah 'Pustaka AI', asisten perpustakaan virtual yang ramah dan sangat membantu. "
            "Tugasmu adalah menjawab pertanyaan seputar perpustakaan, buku, rekomendasi bacaan, "
            "dan pengetahuan umum. Gunakan bahasa Indonesia yang baik dan sopan. "
            "JANGAN menjawab pertanyaan yang tidak pantas atau di luar topik. "
            f"\nPertanyaan Pengguna: {prompt}"
        )

        # Mengirim prompt ke model
        response = model.generate_content(full_prompt)

        # Mengambil teks dari respons
        ai_answer = response.text

        return jsonify({'response': ai_answer})

    except genai.types.BlockedPromptException as e:
        # Menangani kasus di mana prompt diblokir karena kebijakan keamanan
        print(f"Prompt diblokir: {e}")
        return jsonify({
            'error': 'Permintaan Anda tidak dapat diproses karena melanggar kebijakan konten.',
        }), 400
    except Exception as e:
        # Menangani error umum lainnya
        print(f"Error internal server: {e}")
        return jsonify({
            'error': 'Terjadi kesalahan internal pada server AI.',
        }), 500

if __name__ == '__main__':
    # host='0.0.0.0' agar bisa diakses dari luar container (penting untuk Docker)
    # debug=True hanya untuk pengembangan, jangan gunakan di produksi
    app.run(host='0.0.0.0', port=5000, debug=True)
