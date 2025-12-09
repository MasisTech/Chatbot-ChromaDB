import chromadb
from chromadb.utils import embedding_functions
import numpy as np

# --- KONFIGURASI ---
DB_PATH = "./my_db_anime"
COLLECTION_NAME = "anime_collection"
MODEL_NAME = "intfloat/multilingual-e5-small"

def cosine_similarity(v1, v2):
    # Rumus matematika untuk menghitung kemiripan (0.0 - 1.0)
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

def main():
    print(f"🔬 DIAGNOSA VEKTOR & MATEMATIKA AI")
    print(f"   Model: {MODEL_NAME}")
    print("-" * 50)

    # 1. Setup Client
    client = chromadb.PersistentClient(path=DB_PATH)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)

    # 2. Ambil Data Naruto (ID 20) beserta Vektornya
    print("1. Mengambil data ID 20 dari Database...")
    data_naruto = collection.get(ids=["20"], include=["embeddings", "documents", "metadatas"])
    
    if len(data_naruto['ids']) == 0:
        print("❌ ID 20 HILANG! (Ini aneh, padahal tadi ada)")
        return

    # Ambil vektor dan teksnya
    vektor_db_naruto = data_naruto['embeddings'][0]
    teks_naruto = data_naruto['documents'][0]
    judul_naruto = data_naruto['metadatas'][0]['judul']
    
    print(f"   ✅ Data Ditemukan: {judul_naruto}")
    print(f"   📄 Cuplikan Sinopsis: {teks_naruto[:60]}...")
    print(f"   🔢 Panjang Vektor DB: {len(vektor_db_naruto)} dimensi") # Harusnya 384
    
    # Cek apakah vektornya Kosong/Nol semua?
    if np.all(np.array(vektor_db_naruto) == 0):
        print("   ⚠️ BAHAYA: Vektor di database isinya NOL semua! (Rusak)")
    else:
        print("   ✅ Vektor terlihat normal (bukan nol).")

    print("-" * 50)

    # 3. Tes Manual: Embedding Query "Naruto"
    print("2. Melakukan Tes Kecocokan Manual...")
    keyword = "Naruto"
    
    # Minta model membuat vektor baru untuk kata "Naruto" sekarang juga
    vektor_query_baru = sentence_transformer_ef([keyword])[0]
    
    # Hitung jarak manual
    similarity = cosine_similarity(vektor_db_naruto, vektor_query_baru)
    
    print(f"   🧮 Kemiripan Manual ('{keyword}' vs ID 20): {similarity:.4f}")
    
    # Interpretasi Skor
    if similarity > 0.4:
        print("\n✅ KESIMPULAN: Skor Bagus! (> 0.4)")
        print("   Masalahnya ada di INDEX PENCARIAN ChromaDB, bukan di datanya.")
        print("   Solusi: Kita harus reset index (hapus folder database & run setup lagi).")
    else:
        print("\n❌ KESIMPULAN: Skor BURUK! (< 0.4)")
        print("   Model AI menganggap kata 'Naruto' TIDAK NYAMBUNG dengan sinopsis Indonesianya.")
        print("   Solusi: Kita harus ganti Model AI ke versi 'Multilingual'.")

if __name__ == "__main__":
    main()