import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os

# Set mirror
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# --- 1. SETUP KONEKSI ---
print("🔌 Menghubungkan ke ChromaDB...")

# Pastikan path-nya absolut/jelas biar gak nyasar
db_path = "./my_db_anime"
client = chromadb.PersistentClient(path=db_path)

# Hapus database lama biar bersih (RESET TOTAL)
try:
    client.delete_collection("anime_collection")
    print("🧹 Database lama berhasil dihapus. Memulai lembaran baru...")
except:
    print("✨ Belum ada database lama, membuat baru...")

# Bikin wadah baru
model_name = "intfloat/multilingual-e5-small"
local_model_path = "./models/multilingual-e5-small"

# Cek apakah ada model di folder lokal
if os.path.exists(local_model_path):
    print(f"🧠 Menggunakan model lokal dari: {local_model_path}")
    model_name = local_model_path
else:
    print(f"🌐 Mengunduh model {model_name} dari internet...")

emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
collection = client.create_collection(name="anime_collection", embedding_function=emb_fn)


# --- 2. BACA FILE CSV TEMANMU ---
nama_file = "dataset_anime_indonesia.csv" # Pastikan nama file ini BENAR
print(f"📂 Sedang membaca file {nama_file}...")

try:
    df = pd.read_csv(nama_file)
    print(f"✅ Berhasil membaca {len(df)} baris data!")
    
    # Validasi sedikit: Cek apakah ada Naruto di CSV
    cek_naruto = df[df['judul'].str.contains("Naruto", case=False, na=False)]
    if not cek_naruto.empty:
        print(f"   (Info: Ditemukan {len(cek_naruto)} judul Naruto di dalam CSV. Aman!)")
    else:
        print("⚠️ PERINGATAN: Tidak ada 'Naruto' di file CSV kamu! Cek isinya.")

except FileNotFoundError:
    print(f"❌ ERROR FATAL: File '{nama_file}' tidak ditemukan di folder ini!")
    print("   Pastikan file CSV ada di sebelah file script ini.")
    exit()


# --- 3. MASUKKAN KE DATABASE ---
print("\n🚀 Sedang memproses data ke 'Otak AI'...")
print("   (Ini mungkin butuh 1-2 menit tergantung kecepatan komputermu, JANGAN DI-CLOSE!)")

# Konversi data
ids = df['id'].astype(str).tolist()
documents = df['sinopsis'].tolist() 
metadatas = df[['judul', 'genre']].to_dict(orient='records')

# Masukkan ke ChromaDB
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

jumlah_data = collection.count()
print(f"\n🎉 SUKSES BESAR! Total data di database sekarang: {jumlah_data} item.")


# --- 4. PEMBUKTIAN (TESTING LANGSUNG) ---
print("\n🔍 MELAKUKAN TES PENCARIAN 'Naruto'...")
results = collection.query(
    query_texts=["Naruto"],
    n_results=3
)

if not results['ids'][0]:
    print("❌ Tes Gagal: Naruto tidak ditemukan di database.")
else:
    print("✅ Tes Berhasil! Berikut hasil pencariannya:")
    for i in range(len(results['ids'][0])):
        judul = results['metadatas'][0][i]['judul']
        print(f"   {i+1}. {judul}")

print("\n------------------------------------------------")
print("Sekarang kamu bisa jalankan 'ujicoba_2.py' atau 'app.py' dengan tenang!")