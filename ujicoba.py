import chromadb
from chromadb.utils import embedding_functions

# 1. Setup Database (ChromaDB Client)
# Data akan disimpan sementara di memori (hilang kalau restart)
# Untuk menyimpan permanen, gunakan path: chromadb.PersistentClient(path="./my_db")
# client = chromadb.Client()
client = chromadb.PersistentClient(path="./my_db_anime")

# 2. Siapkan Model Embedding (Penerjemah Teks ke Angka)
# Kita pakai model default yang ringan
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="intfloat/multilingual-e5-small")

# 3. Buat Collection (Mirip 'Table' di SQL)
collection = client.create_collection(name="anime_collection", embedding_function=emb_fn)

# 4. Simulasi TRANSAKSI INSERT (Menambahkan Data)
print("--- Memasukkan Data ke Vector DB ---")
documents = [
    "Seorang remaja bernama Denji bergabung dengan pemburu iblis keamanan publik setelah menyatu dengan iblis gergaji mesin.", # Chainsaw Man
    "Seorang ninja muda yang berisik mencari pengakuan dan bermimpi menjadi Hokage.", # Naruto
    "Dua remaja bertukar tubuh secara misterius dan mencoba bertemu satu sama lain saat komet mendekat.", # Kimi no Na wa
    "Sekelompok bajak laut berlayar mencari harta karun legendaris bernama One Piece." # One Piece
]

metadatas = [
    {"judul": "Chainsaw Man", "genre": "Action"},
    {"judul": "Naruto", "genre": "Action"},
    {"judul": "Kimi no Na wa", "genre": "Romance"},
    {"judul": "One Piece", "genre": "Adventure"}
]

ids = ["id1", "id2", "id3", "id4"]

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)
print(f"Berhasil menyimpan {len(documents)} data anime!\n")

# 5. Simulasi TRANSAKSI SEARCH (Pencarian Semantik)
query_text = "Cowok yang bertarung melawan monster jahat" 
# Perhatikan: Tidak ada kata 'Iblis' atau 'Ninja' di query, tapi secara makna mirip.

print(f"Search Query: '{query_text}'")
print("--- Hasil Pencarian ---")

results = collection.query(
    query_texts=[query_text],
    n_results=2 # Tampilkan 2 hasil teratas
)

# Tampilkan hasil
for i in range(len(results['ids'][0])):
    judul = results['metadatas'][0][i]['judul']
    sinopsis = results['documents'][0][i]
    jarak = results['distances'][0][i] # Semakin kecil angka, semakin mirip
    print(f"{i+1}. {judul} (Distance: {jarak:.4f})")
    print(f"   Sinopsis: {sinopsis}")