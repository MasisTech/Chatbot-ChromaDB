import chromadb
from chromadb.utils import embedding_functions

# 1. Setup Client (Path folder SAMA seperti sebelumnya biar data lama kebaca)
client = chromadb.PersistentClient(path="./my_db_anime")
# model lama
# sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
#m odel baru
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="intfloat/multilingual-e5-small")
collection = client.get_or_create_collection(name="anime_collection", embedding_function=sentence_transformer_ef)

# --- BAGIAN INPUT DATA BARU ---
# Kita cek dulu, kalau id 'id5' belum ada, kita tambahkan Chainsaw Man
existing_ids = collection.get()['ids']

# =========================================================================
# 🕵️ START DEBUG AREA (Cek Apa Isi ID 20 Sebenarnya)
# =========================================================================
print("\n--- 🕵️ DEBUG: MENGECEK DATA NARUTO (ID 20) ---")
try:
    data_naruto = collection.get(ids=["20"])
    
    # Cek apakah ID 20 ditemukan
    if len(data_naruto['ids']) > 0:
        sinopsis_tersimpan = data_naruto['documents'][0]
        judul_tersimpan = data_naruto['metadatas'][0]['judul']
        
        print(f"✅ ID 20 Ditemukan!")
        print(f"   Judul: '{judul_tersimpan}'")
        print(f"   Isi Sinopsis: '{sinopsis_tersimpan}'") # <--- Kita lihat ini isinya apa!
        
        if sinopsis_tersimpan.strip() == "":
            print("⚠️ ANEH: Sinopsisnya kosong melompong!")
        elif "Naruto" not in sinopsis_tersimpan:
            print("⚠️ ANEH: Kata 'Naruto' tidak ada di dalam sinopsis!")
    else:
        print("❌ ID 20 TIDAK DITEMUKAN sama sekali di collection ini.")

except Exception as e:
    print(f"❌ Error saat debug: {e}")

print("=========================================================================\n")
# =========================================================================

# if "id5" not in existing_ids:
#     print("Menambahkan data Chainsaw Man & Hollow Knight...")
#     collection.add(
#         documents=[
#             "Seorang pemuda miskin yang bergabung dengan iblis gergaji peliharaannya untuk memburu iblis jahat demi melunasi hutang.",
#             "Seorang pelindung kerajaan serangga yang lincah bertarung menggunakan jarum dan benang di dunia bawah tanah yang hancur."
#             # "Dua remaja bertukar tubuh secara misterius dan mencoba bertemu satu sama lain saat komet mendekat.", # Kimi no Na wa
#             # "Sekelompok bajak laut berlayar mencari harta karun legendaris bernama One Piece." # One Piece
#         ],
#         metadatas=[
#             {"judul": "Chainsaw Man", "genre": "Action/Horror"},
#             {"judul": "Hollow Knight: Silksong", "genre": "Metroidvania"}
#             # {"judul": "Kimi no Na wa", "genre": "Romance"},
#             # {"judul": "One Piece", "genre": "Adventure"} 
#         ],
#         ids=["id5", "id6"]
#     )
# else:
#     print("Data baru sudah ada di database, siap mencari!")
    
#-----------------------------------------------------------------------------------------
# MENGINTIP DATA (Pengganti GUI)
# Ini fungsinya mirip "SELECT * FROM table LIMIT 5" di SQL

print("\n--- MENGINTIP ISI DATABASE ---")
hasil_intip = collection.peek(limit=3) # Lihat 3 data teratas

print("ID Data:", hasil_intip['ids'])
print("Metadata (Judul):", hasil_intip['metadatas'])
# print("Embeddings:", hasil_intip['embeddings']) # <-- Ini kalau mau lihat angka vektornya (bikin pusing, jangan dulu)
#---------------------------------------------------------------------------------------------

# --- BAGIAN PENCARIAN INTERAKTIF (LOOP) ---
print("\n=== MESIN PENCARI ANIME/GAME (Ketik 'exit' untuk keluar) ===")

while True:
    # Mengambil input langsung dari keyboard kamu
    query_user = input("\nMasukkan kata kunci pencarian: ")
    
    # Cara keluar dari loop
    if query_user.lower() == 'exit':
        print("Sampai jumpa!")
        break
    
    # Lakukan pencarian
    results = collection.query(
        query_texts=[query_user],
        n_results=3 # Tampilkan 3 hasil teratas
    )
    
    print(f"--- Hasil untuk '{query_user}' ---")
    for i in range(len(results['ids'][0])):
        judul = results['metadatas'][0][i]['judul']
        jarak = results['distances'][0][i]
        sinopsis = results['documents'][0][i]
        
        # Tampilkan judul dan score kemiripan
        print(f"{i+1}. {judul} (Score: {jarak:.4f})")
        # print(f"   Sinopsis: {sinopsis}") # Uncomment kalau mau lihat sinopsisnya