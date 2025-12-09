import csv
import chromadb
from chromadb.utils import embedding_functions
import os

# Nama file CSV yang kamu pakai
CSV_FILENAME = 'dataset_anime_indonesia.csv'
DB_PATH = "./my_db_anime"
MODEL_NAME = "intfloat/multilingual-e5-small"

print("=== 🕵️ LAPORAN DIAGNOSA BRUN ===\n")

# 1. CEK FILE CSV & HEADERNYA
print(f"1. Memeriksa file '{CSV_FILENAME}'...")
if os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        print(f"   ✅ File ditemukan!")
        print(f"   📋 HEADER (Nama Kolom) aslinya adalah:\n   {header}")
        print("\n   (Tolong copy-paste output HEADER di atas ke chat Vi ya!)")
else:
    print("   ❌ File CSV tidak ditemukan di folder ini!")

print("\n" + "-"*30 + "\n")

# 2. CEK ISI DATABASE CHROMADB
print(f"2. Memeriksa isi database di '{DB_PATH}'...")
try:
    client = chromadb.PersistentClient(path=DB_PATH)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.get_collection(name="anime_collection", embedding_function=emb_fn)
    jumlah_data = collection.count()
    print(f"   📊 Jumlah total data di dalam otak AI: {jumlah_data} item")
    
    if jumlah_data > 0:
        print("   🔍 Mengintip 3 data pertama:")
        peek = collection.peek(limit=3)
        for i, meta in enumerate(peek['metadatas']):
            print(f"      - ID: {peek['ids'][i]} | Judul: {meta.get('judul', 'Tanpa Judul')}")
    else:
        print("   ⚠️ Database KOSONG! (Pantas saja Naruto tidak ketemu)")

except Exception as e:
    print(f"   ❌ Gagal buka database: {e}")

print("\n=== DIAGNOSA SELESAI ===")