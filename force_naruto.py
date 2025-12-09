import chromadb
from chromadb.utils import embedding_functions
import csv
import os

# --- KONFIGURASI ---
CSV_FILENAME = 'dataset_anime_indonesia.csv'
DB_PATH = "./my_db_anime"
COLLECTION_NAME = "anime_collection"

def main():
    print("🚑 MEMULAI OPERASI PENYELAMATAN NARUTO...")
    
    # 1. Konek ke Database
    client = chromadb.PersistentClient(path=DB_PATH)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="intfloat/multilingual-e5-small")
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)
    
    print(f"📊 Jumlah data saat ini: {collection.count()} item")

    # 2. Cari Naruto di CSV
    ids_to_add = []
    docs_to_add = []
    metas_to_add = []
    
    print(f"🔍 Mencari Naruto di {CSV_FILENAME}...")
    
    with open(CSV_FILENAME, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Bersihkan spasi
            judul = row['judul'].strip()
            id_data = row['id'].strip()
            sinopsis = row['sinopsis'].strip()
            genre = row['genre'].strip()
            
            # Cek apakah ini Naruto?
            if "naruto" in judul.lower():
                print(f"   👉 Menemukan: {judul} (ID: {id_data})")
                
                # Masukkan ke list antrian
                ids_to_add.append(id_data)
                docs_to_add.append(sinopsis)
                metas_to_add.append({"judul": judul, "genre": genre})

    # 3. Eksekusi Paksa
    if len(ids_to_add) > 0:
        print(f"\n⚙️  Mencoba menyuntikkan {len(ids_to_add)} data Naruto ke Database...")
        try:
            # Kita gunakan upsert (Update or Insert) biar gak error kalau ID udah ada
            collection.upsert(
                ids=ids_to_add,
                documents=docs_to_add,
                metadatas=metas_to_add
            )
            print("✅ BERHASIL MENYIMPAN! Tidak ada error.")
        except Exception as e:
            print(f"❌ GAGAL MENYIMPAN: {e}")
    else:
        print("❌ Tidak menemukan data Naruto di CSV.")

    # 4. Cek Hasil Akhir
    final_count = collection.count()
    print(f"\n📊 Jumlah data SETELAH operasi: {final_count} item")
    
    # 5. Tes Validasi Langsung
    print("\n🧐 Tes Cepat: Apakah ID 20 (Naruto) sudah ada?")
    cek = collection.get(ids=["20"])
    if len(cek['ids']) > 0:
        print("🎉 KONFIRMASI: Naruto sudah ada di dalam otak AI!")
    else:
        print("💀 Aneh... Masih belum masuk juga.")

if __name__ == "__main__":
    main()