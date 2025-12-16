# 🚀 Panduan Menjalankan Chatbot Anime (Clone dari GitHub)

Tutorial ini dibuat khusus untuk teman-teman yang ingin menjalankan projek **Chatbot Anime** ini di laptop masing-masing.

---

## 1. Persiapan Awal (Prerequisites)

Pastikan di laptop kalian sudah terinstall:
*   **Python** (Versi 3.9 ke atas lebih baik).
*   **Git Bash** (Untuk clone repository).
*   **VS Code** (Teks Editor).

---

## 2. Clone Repository

Buka terminal (Git Bash / CMD), lalu jalankan perintah ini untuk mendownload kode projek:

```bash
git clone https://github.com/MasisTech/Chatbot-ChromaDB.git
cd Chatbot-ChromaDB
```

---

## 3. Install Library yang Dibutuhkan

Biar gak error "Module Not Found", kita harus install semua paket yang dipakai di `requirements.txt`.
Disarankan pakai **Virtual Environment** biar rapi (Opsional tapi Recommended):

```bash
# Buat environment baru (Lakukan sekali saja di awal)
python -m venv venv

# Aktifkan environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install semua kebutuhan
pip install -r requirements.txt
```

---

## 4. 🔑 SETUP API KEY (PENTING!)

Karena API Key sifatnya rahasia, file kuncinya **TIDAK** ikut ter-upload di GitHub. Kalian harus buat sendiri codenya agar bisa jalan.

1.  Buka folder projek di VS Code.
2.  Lihat apakah ada folder bernama `.streamlit`. Jika tidak ada, **Buat Folder Baru** bernama `.streamlit`.
3.  Di dalam folder `.streamlit`, buat file baru bernama `secrets.toml`.
4.  Isi file `secrets.toml` dengan kode berikut (Minta API Key ke Ketua Kelompok atau buat di Console Groq):

**Isi File `.streamlit/secrets.toml`**:
```toml
GROQ_API_KEY = "gsk_..."  <-- GANTI DENGAN KUNCI ASLI KITA
```
> *Tanya API Key-nya ke saya (si Pembuat Repo) kalau belum punya.*

---

## 5. Menjalankan Aplikasi

Kalau semua sudah siap, tinggal jalankan aplikasinya dengan perintah:

```bash
streamlit run app.py
```

Tunggu sebentar sampai browser terbuka otomatis. Selamat mencoba fiturnya!

*   **Chat AI**: Tanya rekomendasi anime.
*   **Kelola Database**: Tambah/Edit/Hapus anime (otomatis sinkron ke CSV).

---

## 6. Kenapa Folder `.streamlit` dan `.venv` Sangat Penting?

Mungkin kalian bertanya-tanya tentang fungsi folder-folder misterius ini. Berikut alasannya:

### 📁 `.streamlit`: Pusat Kendali & Rahasia
Folder ini memegang dua peran vital:
1.  **`config.toml` (Sang Desainer)**: File ini mempercantik tampilan aplikasi. Ia mengatur tema warna dan font agar aplikasi terlihat premium dan nyaman dipandang.
2.  **`secrets.toml` (Sang Penjaga)**: File ini adalah brankas besi untuk menyimpan data sensitif seperti API Key. Kita menyimpan kunci rahasia di sini agar aman dan terpisah dari kode utama.

### 🐍 `.venv`: Ruang Kerja Eksklusif
Bayangkan `.venv` sebagai bengkel pribadi khusus untuk proyek ini.
*   **Wadah Terisolasi**: Semua alat (library) tersimpan rapi di sini.
*   **Stabilitas Terjamin**: Proyek tetap berjalan mulus tanpa gangguan dari versi library di proyek lain.
*   **Siap Tempur**: Dengan folder ini, kita memastikan aplikasi memiliki amunisi yang tepat untuk beroperasi.

---
**Catatan:**
Saat pertama kali dijalankan, aplikasi akan mendownload model AI (`multilingual-e5-small`) sekitar 500MB+ secara otomatis. Pastikan internet lancar ya! ☕
