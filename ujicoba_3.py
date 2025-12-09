import chromadb
from chromadb.utils import embedding_functions
import pandas as pd  # Kita panggil library Pandas

#-----------------------------------------------------------------------------------------------------------------
jawab = input("⚠️ PERINGATAN: Ini akan MENGHAPUS database lama dan membuat baru dari CSV. Yakin? (y/n): ")

if jawab.lower() != 'y':
    print("Oke, batal. Database aman.")
    exit() # Program berhenti di sini
#--------------------------------------------------------------------------------------------------------------

# 1. Setup Database
client = chromadb.PersistentClient(path="./my_db_anime")                                                      #menulis data ke Harddisk/SSD, dalam konteks ini dismimpan ke folder my_db_anime(si persistenclient)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="intfloat/multilingual-e5-small")              #ngubah teks jadi angka2 biar bisa difahami komputer

# Hapus collection lama kalau ada, biar kita bikin fresh dari CSV
try:
    client.delete_collection(name="anime_collection")
    print("Collection lama dihapus, membuat yang baru...")
except:
    pass # Kalau belum ada, ya lanjut aja

collection = client.create_collection(name="anime_collection", embedding_function=emb_fn)

# 2. BACA DATA DARI CSV
print("--- Sedang membaca file CSV... ---")
# Membaca file dataset_anime.csv
df = pd.read_csv('dataset_anime_indonesia.csv')

# Tampilkan data biar yakin kebaca
print(df.head())                                                                                    #df (data frame) - excel fersi kodingan (gampangnya gitu lah y kwwkw)
print(f"\nTotal data ditemukan: {len(df)} baris")                                                   #len ini ngitung panjang weh, masa lupa

# 3. MASUKKAN DATA CSV KE CHROMA
# Kita ubah kolom-kolom di CSV jadi list supaya bisa dimakan ChromaDB
ids = df['id'].astype(str).tolist()                                                                             #ngambil kolom yang judulnya id. soalnya chromadb hanya bisa baca dalam bentuk List biasa (standar Python).
documents = df['sinopsis'].tolist()#ngambil kolom sinopsis                                          #tolist() untuk ngubah format pandas series menjadi phyton list
                                                                                                    
# Metadata agak unik, harus bentuknya list of dictionaries
# Kita ambil kolom judul dan genre
metadatas = df[['judul', 'genre']].to_dict(orient='records')                                        #knp kurungnya 2? solanya pandas mau ambil lebih dari 1 kolom
#to_dict            -> Ubah tabel jadi Dictionary (Kamus). Dictionary itu format data yang punya pasangan Kunci (Key) dan Nilai (Value).
#orient = 'records' -> menyuruh Python untuk mengubah datanya Per Baris.

print("\n--- Memasukkan data ke Vector Database... ---")
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print("SUKSES! Semua data dari CSV sudah masuk database.")

# MENGINTIP DATA (Pengganti GUI)
# Ini fungsinya mirip "SELECT * FROM table LIMIT 5" di SQL

print("\n--- MENGINTIP ISI DATABASE ---")
hasil_intip = collection.peek(limit=3) # Lihat 3 data teratas

print("ID Data:", hasil_intip['ids'])
print("Metadata (Judul):", hasil_intip['metadatas'])
print("Embeddings:", hasil_intip['embeddings']) # <-- Ini kalau mau lihat angka vektornya (bikin pusing, jangan dulu)