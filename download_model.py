import os

# Set mirror SEBELUM import library lain
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from sentence_transformers import SentenceTransformer

def download_model():
    model_name = "intfloat/multilingual-e5-small"
    local_path = "./models/multilingual-e5-small"

    print(f"🚀 Memulai download model '{model_name}'...")
    print(f"📂 Model akan disimpan di: {os.path.abspath(local_path)}")
    print("⏳ Mohon tunggu, ini mungkin memakan waktu tergantung internetmu...")

    try:
        # Download dan simpan model ke folder lokal
        model = SentenceTransformer(model_name)
        model.save(local_path)
        print("✅ Download SELESAI! Model berhasil disimpan.")
        print(f"   path: {local_path}")
    except Exception as e:
        print(f"❌ Gagal download model: {e}")
        print("   Pastikan koneksi internet stabil untuk langkah ini saja.")

if __name__ == "__main__":
    download_model()
