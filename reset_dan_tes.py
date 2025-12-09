import chromadb
from chromadb.utils import embedding_functions
import csv
import os
import shutil # Ini alat penghancur folder
import time

# --- KONFIGURASI ---
CSV_FILENAME = 'dataset_anime_indonesia.csv'
DB_FOLDER = "./my_db_anime"
COLLECTION_NAME = "anime_collection"
# Model "Si Pintar Bahasa" (Multilingual)
MODEL_NAME = "intfloat/multilingual-e5-small"

def main():
    print("🚀 MEMULAI PROSES RESET TOTAL...")
    print(f"   Target Model: {MODEL_NAME}")
    
    # 1. HAPUS FOLDER DATABASE LAMA (Wajib!)
    if os.path.exists(DB_FOLDER):
        print(f"💣 Menghapus folder database lama: {DB_FOLDER}...")
        try:
            shutil.rmtree(DB_FOLDER)
            print("   ✅ Folder lama berhasil dimusnahkan.")
            time.sleep(1) # Beri napas sebentar buat Windows
        except Exception as e:
            print(f"   ❌ Gagal hapus folder otomatis. Tutup semua terminal lain & hapus folder '{DB_FOLDER}' manual!")
            return
    else:
        print("   ℹ️  Folder database belum ada (Aman).")

    # 2. SETUP DATABASE BARU
    print("🏗️  Membangun database baru...")
    client = chromadb.PersistentClient(path=DB_FOLDER)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_func)
    print("   ✅ Database baru siap dengan otak Multilingual.")

    # 3. BACA CSV & IMPORT
    print(f"📖 Membaca {CSV_FILENAME}...")
    ids, docs, metas = [], [], []
    
    try:
        with open(CSV_FILENAME, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                judul = row['judul'].strip()
                sinopsis = row['sinopsis'].strip()
                id_data = row['id'].strip()
                genre = row['genre'].strip()

                if not judul or not sinopsis: continue

                ids.append(id_data)
                docs.append(sinopsis)
                metas.append({"judul": judul, "genre": genre})
                count += 1
        
        print(f"   ✅ Ditemukan {len(ids)} data di CSV.")

        # Masukkan ke Database (Batching biar aman)
        print("⚙️  Sedang menanamkan data (Ini mungkin butuh 1-2 menit karena modelnya lebih besar)...")
        batch_size = 50
        total_batches = (len(ids) + batch_size - 1) // batch_size
        
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            print(f"   Processing batch {i} - {end} ...")
            collection.add(
                ids=ids[i:end],
                documents=docs[i:end],
                metadatas=metas[i:end]
            )
        
        print("🎉 IMPORT SELESAI!")

    except Exception as e:
        print(f"❌ Error saat baca CSV: {e}")
        return

    # 4. TES PENCARIAN LANGSUNG
    print("\n" + "="*40)
    print("🔎 TES PENCARIAN OTOMATIS")
    print("="*40)
    
    queries = ["Naruto", "Bajak Laut", "Ninja"]
    
    for q in queries:
        print(f"\nMencari: '{q}' ...")
        results = collection.query(query_texts=[q], n_results=3)
        
        for i in range(len(results['ids'][0])):
            judul = results['metadatas'][0][i]['judul']
            score = results['distances'][0][i]
            print(f"   {i+1}. {judul} (Score: {score:.4f})")

if __name__ == "__main__":
    main()