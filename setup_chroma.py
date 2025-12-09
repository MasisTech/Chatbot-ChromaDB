import chromadb
from chromadb.utils import embedding_functions
import csv
import os

# Set mirror
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# --- KONFIGURASI ---
CSV_FILENAME = 'dataset_anime_indonesia.csv'
DB_PATH = "./my_db_anime"
COLLECTION_NAME = "anime_collection"

def main():
    print("🚀 Memulai SETUP FINAL (Versi Anti-Error)...")

    # 1. Setup Client
    print(f"📂 Mengakses database di '{DB_PATH}'...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Cek model lokal
    model_name = "intfloat/multilingual-e5-small"
    local_model_path = "./models/multilingual-e5-small"
    if os.path.exists(local_model_path):
        print(f"🧠 Menggunakan model lokal: {local_model_path}")
        model_name = local_model_path
        
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    
    # --- BAGIAN PERBAIKAN ---
    # Kita coba hapus dulu biar bersih. 
    # Kalau error (karena belum ada), kita "tangkap" errornya biar gak crash.
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("🗑️  Collection lama berhasil dihapus (Reset).")
    except Exception as e:
        # Kalau errornya "NotFoundError", berarti aman, lanjut aja.
        print("ℹ️  Database masih kosong/baru, siap membuat collection baru...")

    # Buat collection baru
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)
    print("✨ Collection baru SIAP!")

    # 2. Baca CSV
    print(f"📖 Membaca {CSV_FILENAME}...")
    
    ids_list = []
    documents_list = [] 
    metadatas_list = [] 

    try:
        with open(CSV_FILENAME, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            count = 0
            naruto_found = False 

            for row in csv_reader:
                # --- MAPPING DATA ---
                judul = row['judul'].strip()
                genre = row['genre'].strip()
                sinopsis = row['sinopsis'].strip()
                id_data = row['id'].strip()

                if not sinopsis or not judul:
                    continue

                # DETEKTOR NARUTO
                if "naruto" in judul.lower():
                    print(f"🦊 NARUTO DITEMUKAN! (ID: {id_data})")
                    naruto_found = True

                ids_list.append(id_data)
                # MODIFIKASI: Gabungkan Judul + Sinopsis untuk Embedding yang lebih akurat
                combined_text = f"{judul}: {sinopsis}"
                documents_list.append(combined_text)
                metadatas_list.append({"judul": judul, "genre": genre})
                count += 1

            if not naruto_found:
                print("⚠️ Peringatan: Naruto tidak terdeteksi di CSV ini.")

            print(f"✅ Berhasil memproses {len(ids_list)} baris data.")

            # 3. Masukkan ke ChromaDB
            if len(ids_list) > 0:
                print("⚙️  Sedang menanamkan data... (Tunggu sebentar)")
                
                # Batch processing
                batch_size = 100
                for i in range(0, len(ids_list), batch_size):
                    end = min(i + batch_size, len(ids_list))
                    collection.add(
                        ids=ids_list[i:end],
                        documents=documents_list[i:end],
                        metadatas=metadatas_list[i:end]
                    )
                
                print(f"🎉 SUKSES BESAR! {len(ids_list)} anime sudah masuk database.")
                print("➡️  Sekarang jalankan 'ujicoba_2.py'!")
            else:
                print("❌ Data kosong.")

    except KeyError as e:
        print(f"❌ ERROR HEADER: Kolom {e} tidak ditemukan di CSV!")
    except FileNotFoundError:
        print(f"❌ File {CSV_FILENAME} gak ketemu!")

if __name__ == "__main__":
    main()