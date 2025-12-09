import chromadb
from chromadb.utils import embedding_functions
import time

# --- KONFIGURASI ---
DB_FOLDER = "./my_db_anime"
COLLECTION_NAME = "anime_collection"
# PENTING: Harus sama persis dengan yang dipakai saat setup!
MODEL_NAME = "intfloat/multilingual-e5-small"

def main():
    print("⏳ Sedang memuat database (Loading)...")
    
    # 1. Konek ke Database
    try:
        client = chromadb.PersistentClient(path=DB_FOLDER)
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_func)
        
        # Hitung total data
        total_data = collection.count()
        print(f"✅ SIAP! Terhubung ke database dengan {total_data} anime.")
        
    except Exception as e:
        print(f"❌ Error: Tidak bisa membuka database. Pastikan sudah menjalankan 'reset_dan_tes.py' dulu!\nDetail: {e}")
        return

    # 2. Loop Pencarian
    print("\n" + "="*50)
    print("       MESIN PENCARI ANIME CANGGIH (AI)       ")
    print("         (Ketik 'exit' untuk keluar)          ")
    print("="*50)

    while True:
        query = input("\n🔍 Cari anime apa? (Contoh: ninja, sedih, robot): ")
        
        if query.strip().lower() in ['exit', 'keluar', 'quit']:
            print("👋 Sampai jumpa!")
            break
        
        if not query.strip():
            continue

        print("   🤖 AI sedang berpikir...")
        start_time = time.time()
        
        # Lakukan Query
        results = collection.query(
            query_texts=[query],
            n_results=5 # Kita tampilkan 5 biar lebih banyak pilihan
        )
        
        durasi = time.time() - start_time
        print(f"   (Selesai dalam {durasi:.2f} detik)\n")

        print(f"--- Hasil Top 5 untuk '{query}' ---")
        if len(results['ids'][0]) == 0:
            print("   😞 Tidak ditemukan hasil yang cocok.")
        else:
            for i in range(len(results['ids'][0])):
                judul = results['metadatas'][0][i]['judul']
                genre = results['metadatas'][0][i]['genre']
                score = results['distances'][0][i]
                
                # Trik visualisasi score:
                # Score 0.0 - 0.5 = Sangat Mirip (Hijau)
                # Score > 0.5     = Agak Mirip (Kuning/Merah)
                kualitas = "⭐⭐⭐⭐⭐ (Sangat Cocok)" if score < 0.4 else "⭐⭐⭐ (Lumayan)"
                
                print(f"{i+1}. {judul}")
                print(f"   Genre: {genre}")
                print(f"   Kecocokan: {kualitas} (Jarak: {score:.4f})")
                print("-" * 30)

if __name__ == "__main__":
    main()