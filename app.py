import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import os
import re
from groq import Groq
import time
import pandas as pd
import csv

# --- CSV SYNC SETTINGS ---
CSV_PATH = "./dataset_anime_indonesia.csv"

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Anime AI - Groq Speed",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Anime Finder x Groq AI")
st.markdown("---")
st.write("Chatbot Anime Super Cepat! (Powered by Groq Cloud)")

# --- 2. CONFIG GROQ ---
# API Key ambil dari secrets.toml (Aman untuk GitHub)
if "GROQ_API_KEY" in st.secrets:
    SECRET_KEY = st.secrets["GROQ_API_KEY"]
else:
    SECRET_KEY = "gsk_..." # Fallback dummy atau error handling
    st.error("API Key belum diset di secrets.toml!")

client_groq = Groq(api_key=SECRET_KEY)

# --- 3. PREPROCESSING QUERY ---
def preprocess_query(query):
    query = query.lower()
    stopwords = [
        'adakah', 'apakah', 'ada', 'apa', 'disini', 'di sini', 'kah',
        'yang', 'tentang', 'mengenai', 'cari', 'carikan', 'tolong',
        'dong', 'yah', 'sih', 'nih', 'deh', 'punya', 'kan'
    ]
    for word in stopwords:
        query = re.sub(r'\b' + word + r'\b', '', query)
    query = re.sub(r'[^\w\s]', '', query)
    return ' '.join(query.split()).strip()

# --- 3.5 CSV SYNC LOGIC ---
def sync_add_csv(new_id, title, genre, synopsis):
    try:
        # Append ke CSV tanpa baca full (lebih efisien)
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([new_id, title, genre, synopsis])
        print(f"✅ CSV Add: {title}")
    except Exception as e:
        print(f"❌ CSV Error: {e}")

def sync_update_csv(t_id, title, genre, synopsis):
    try:
        df = pd.read_csv(CSV_PATH)
        # Pastikan kolom ID string untuk comparison
        df['id'] = df['id'].astype(str)
        t_id_str = str(t_id)
        
        if t_id_str in df['id'].values:
            idx = df.index[df['id'] == t_id_str].tolist()[0]
            df.at[idx, 'judul'] = title
            df.at[idx, 'genre'] = genre
            df.at[idx, 'sinopsis'] = synopsis
            df.to_csv(CSV_PATH, index=False)
            print(f"✅ CSV Update: {title}")
    except Exception as e:
        print(f"❌ CSV Update Error: {e}")

def sync_delete_csv(t_id):
    try:
        df = pd.read_csv(CSV_PATH)
        df['id'] = df['id'].astype(str)
        t_id_str = str(t_id)
        
        if t_id_str in df['id'].values:
            df = df[df['id'] != t_id_str]
            df.to_csv(CSV_PATH, index=False)
            print(f"✅ CSV Delete: {t_id}")
    except Exception as e:
        print(f"❌ CSV Delete Error: {e}")

# --- 4. LOAD DATABASE ---
# @st.cache_resource  <-- Matikan cache dulu biar yakin data selalu fresh
def load_db():
    try:
        print("🔄 Memuat ulang database...")
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        client = chromadb.PersistentClient(path="./my_db_anime")
        model_name = "intfloat/multilingual-e5-small"
        local_model_path = "./models/multilingual-e5-small"
        if os.path.exists(local_model_path):
            model_name = local_model_path
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
        collection = client.get_or_create_collection(name="anime_collection", embedding_function=emb_fn)
        return collection
    except Exception as e:
        print(f"❌ Error loading DB: {e}")
        return None

collection = load_db()

# --- 5. FUNGSI CHAT KE GROQ ---
def tanya_groq(query, context):
    prompt = f"""
    Kamu adalah asisten anime yang sangat ramah dan bersemangat.
    Tugasmu merekomendasikan anime berdasarkan DATA DATABASE di bawah.

    PERTANYAAN USER: "{query}"

    DATA DATABASE (Context):
    {context}

    INSTRUKSI:
    1. Gunakan Bahasa Indonesia yang natural.
    2. Jawab HANYA berdasarkan Data Database di atas.
    3. Jika tidak ada di data, katakan "Belum ada di database kami" dengan sopan.
    4. Jangan berhalusinasi judul yang tidak ada di context.
    """
    try:
        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # Model Groq terbaru
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error Groq: {e}"

# --- 6. INTERFACE UTAMA ---
def page_chat():
    st.header("💬 Chat Asisten Anime")
    
    if "messages_groq" not in st.session_state:
        st.session_state.messages_groq = [
            {"role": "assistant", "content": "Halo! Anime apa yang kamu cari hari ini? ⚡"}
        ]

    for msg in st.session_state.messages_groq:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tanya anime..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages_groq.append({"role": "user", "content": prompt})
        
        cleaned_query = preprocess_query(prompt)

        if collection:
            # PENTING: Pakai prefix "query: " untuk model e5
            final_query = f"query: {cleaned_query}"
            results = collection.query(
                query_texts=[final_query], 
                n_results=10 # Perbanyak kandidat retrieval
            )
            
            context_text = ""
            if results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    judul = results['metadatas'][0][i]['judul']
                    genre = results['metadatas'][0][i]['genre']
                    sinops = results['metadatas'][0][i].get('sinopsis', results['documents'][0][i])
                    context_text += f"- {judul} ({genre}): {sinops}\n"
            else:
                context_text = "Data kosong."

            with st.chat_message("assistant"):
                with st.spinner("⚡ Groq sedang berpikir..."):
                    final_answer = tanya_groq(prompt, context_text)
                    st.markdown(final_answer)
            st.session_state.messages_groq.append({"role": "assistant", "content": final_answer})
        else:
            st.error("Database gagal dimuat.")

def page_manage():
    st.header("🛠️ Manajemen Database Anime")
    if not collection: return

    # Style form
    st.markdown("""<style>div[data-testid="stForm"] {border: 2px solid #4CAF50; padding: 20px; border-radius: 10px;}</style>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Tambah", "✏️ Edit (Update)", "🗑️ Hapus (Delete)"])

    # --- TAB 1: ADD ---
    with tab1:
        st.subheader("Tambah Anime")
        with st.form("add_form", clear_on_submit=True):
            title = st.text_input("Judul Anime (Wajib)")
            genre = st.text_input("Genre")
            synops = st.text_area("Sinopsis (Wajib)")
            new_id = st.text_input("ID Unik (Kosongkan utk Auto)")
            
            if st.form_submit_button("💾 Simpan"):
                if not title or not synops:
                    st.error("Wajib isi Judul & Sinopsis!")
                else:
                    # LOGIC AUTO ID (N+1)
                    if not new_id:
                        try:
                            # Baca CSV untuk cari ID terakhir
                            df_temp = pd.read_csv(CSV_PATH)
                            # Pastikan ID dianggap angka
                            df_temp['id'] = pd.to_numeric(df_temp['id'], errors='coerce')
                            max_id = int(df_temp['id'].max())
                            new_id = str(max_id + 1)
                        except Exception as e:
                            # Fallback kalau CSV kosong/error
                            print(f"Gagal generate ID n+1: {e}")
                            new_id = str(int(time.time())) 

                    doc_text = f"{title} {genre} {synops}"
                    
                    try:
                        with st.spinner("⏳ Menyimpan data ke memori & CSV..."):
                            collection.add(
                                ids=[new_id], 
                                documents=[doc_text], 
                                metadatas=[{"judul":title, "genre":genre, "sinopsis":synops}]
                            )
                            # Sync CSV
                            sync_add_csv(new_id, title, genre, synops)
                            time.sleep(0.5)
                        st.success(f"Anime '{title}' masuk database!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # --- TAB 2: UPDATE (EDIT) ---
    with tab2:
        st.subheader("Edit Data")
        
        # State Management
        if 'edit_target_id' not in st.session_state: st.session_state.edit_target_id = None
        if 'edit_page' not in st.session_state: st.session_state.edit_page = 1

        def reset_edit_state():
            st.session_state.edit_page = 1
            st.session_state.edit_target_id = None

        # --- VIEW A: FORM EDIT ---
        if st.session_state.edit_target_id:
            t_id = st.session_state.edit_target_id
            
            # Fetch data by ID
            data = collection.get(ids=[t_id])
            if not data['ids']:
                st.error("Data tidak ditemukan (mungkin sudah dihapus).")
                if st.button("Kembali"): reset_edit_state(); st.rerun()
            else:
                meta = data['metadatas'][0]
                doc = data['documents'][0]
                
                # Header Form
                col_back, col_title = st.columns([1, 5])
                with col_back:
                    if st.button("⬅️ Kembali"):
                        st.session_state.edit_target_id = None
                        st.rerun()
                with col_title:
                    st.markdown(f"### 📝 Edit: {meta['judul']}")
                
                # Form Update
                with st.form("real_edit_form"):
                    et = st.text_input("Judul", value=meta['judul'])
                    eg = st.text_input("Genre", value=meta['genre'])
                    # Fallback sinopsis
                    old_syn = meta.get('sinopsis', doc)
                    if not old_syn or len(old_syn) < 5: old_syn = doc
                    es = st.text_area("Sinopsis", value=old_syn, height=180)
                    
                    if st.form_submit_button("✅ Simpan Perubahan"):
                        with st.spinner("⏳ Memperbarui data ke sistem & CSV..."):
                            new_doc = f"{et} {eg} {es}"
                            collection.update(
                                ids=[t_id],
                                documents=[new_doc],
                                metadatas=[{"judul":et, "genre":eg, "sinopsis":es}]
                            )
                            # Sync CSV
                            sync_update_csv(t_id, et, eg, es)
                            time.sleep(0.5)
                        
                        st.success("✨ Data Berhasil Diupdate!")
                        time.sleep(0.5)
                        st.session_state.edit_target_id = None # Balik ke list search
                        st.rerun()

        # --- VIEW B: SEARCH & CARD LIST ---
        else:
            q_edit = st.text_input("🔍 Cari Anime (Edit):", placeholder="Contoh: Isekai...", key="q_edit_card", on_change=reset_edit_state)
            
            if q_edit:
                # 1. Query Data 
                res = collection.query(query_texts=[f"query: {q_edit}"], n_results=50)
                ids = res['ids'][0]
                metas = res['metadatas'][0]
                total_data = len(ids)

                if total_data == 0:
                    st.info("🤷‍♂️ Tidak ditemukan anime dengan kata kunci itu.")
                else:
                    # 2. Config Pagination
                    ITEMS_PER_PAGE = 10
                    total_pages = (total_data + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
                    if st.session_state.edit_page > total_pages: st.session_state.edit_page = 1
                    
                    # 3. Kontrol Navigasi
                    c_prev, c_info, c_next = st.columns([1, 3, 1])
                    with c_prev:
                        if st.session_state.edit_page > 1:
                            if st.button("◀️ Mundur"):
                                st.session_state.edit_page -= 1
                                st.rerun()
                    with c_info:
                        st.markdown(f"<div style='text-align:center; font-weight:bold'>Halaman {st.session_state.edit_page} dari {total_pages}<br><small>(Total: {total_data} Anime)</small></div>", unsafe_allow_html=True)
                    with c_next:
                        if st.session_state.edit_page < total_pages:
                            if st.button("Lanjut ▶️"):
                                st.session_state.edit_page += 1
                                st.rerun()
                    
                    st.divider()

                    # 4. Slice Data & Render Cards
                    start_idx = (st.session_state.edit_page - 1) * ITEMS_PER_PAGE
                    end_idx = start_idx + ITEMS_PER_PAGE
                    curr_ids = ids[start_idx:end_idx]
                    curr_metas = metas[start_idx:end_idx]

                    for cid, cmeta in zip(curr_ids, curr_metas):
                        with st.container(border=True):
                            col_txt, col_act = st.columns([5, 1])
                            with col_txt:
                                st.subheader(cmeta['judul'])
                                st.caption(f"🆔 {cid} | 🎭 {cmeta['genre']}")
                                syn = cmeta.get('sinopsis', '...')
                                if len(syn) > 200: syn = syn[:200] + "..."
                                st.write(syn)
                            with col_act:
                                st.write("")
                                if st.button("✏️ Edit", key=f"btn_edit_{cid}"):
                                    st.session_state.edit_target_id = cid
                                    st.rerun()

    with tab3:
        st.subheader("Hapus Data")
        
        # State Management Delete
        if 'del_page' not in st.session_state: st.session_state.del_page = 1
        if 'confirm_del_id' not in st.session_state: st.session_state.confirm_del_id = None # State untuk konfirmasi hapus

        def reset_del_state(): 
            st.session_state.del_page = 1
            st.session_state.confirm_del_id = None
        
        q_del = st.text_input("🔍 Cari Hapus:", placeholder="Contoh: Naruto...", key="search_del", on_change=reset_del_state)
        
        # Default tampilkan random jika kosong, atau hasil search
        ids_show, metas_show = [], []
        if q_del:
            res = collection.query(query_texts=[f"query: {q_del}"], n_results=50)
            ids_show, metas_show = res['ids'][0], res['metadatas'][0]
        else:
            # Kalau kosong intip 20 data terakhir
            p = collection.peek(20)
            ids_show, metas_show = p['ids'], p['metadatas']
            
        total_data = len(ids_show)
        
        if total_data == 0:
            st.info("Belum ada data / tidak ditemukan.")
        else:
            # 2. Config Pagination
            ITEMS_PER_PAGE_DEL = 10
            total_pages_del = (total_data + ITEMS_PER_PAGE_DEL - 1) // ITEMS_PER_PAGE_DEL
            if st.session_state.del_page > total_pages_del: st.session_state.del_page = 1
            
            # 3. Kontrol Navigasi
            c_prev_d, c_info_d, c_next_d = st.columns([1, 3, 1])
            with c_prev_d:
                if st.session_state.del_page > 1:
                    if st.button("◀️ Mundur", key="del_prev"):
                        st.session_state.del_page -= 1
                        st.rerun()
            with c_info_d:
                st.markdown(f"<div style='text-align:center; font-weight:bold'>Halaman {st.session_state.del_page} dari {total_pages_del}<br><small>(Total: {total_data} Item)</small></div>", unsafe_allow_html=True)
            with c_next_d:
                if st.session_state.del_page < total_pages_del:
                    if st.button("Lanjut ▶️", key="del_next"):
                        st.session_state.del_page += 1
                        st.rerun()
            
            st.divider()
            
            # 4. Slice Data & Render Cards
            start_idx = (st.session_state.del_page - 1) * ITEMS_PER_PAGE_DEL
            end_idx = start_idx + ITEMS_PER_PAGE_DEL
            curr_ids_d = ids_show[start_idx:end_idx]
            curr_metas_d = metas_show[start_idx:end_idx]

            for cid, cmeta in zip(curr_ids_d, curr_metas_d):
                with st.container(border=True):
                    # Bagian Atas: Info + Tombol Hapus Utama
                    col_txt, col_act = st.columns([5, 1])
                    with col_txt:
                        st.subheader(cmeta['judul'])
                        st.caption(f"Genre: {cmeta['genre']}")
                        syn = cmeta.get('sinopsis', '...')
                        if len(syn) > 150: syn = syn[:150] + "..."
                        st.write(syn)
                    with col_act:
                        st.write("")
                        # Tombol Hapus pemicu
                        if st.session_state.confirm_del_id != cid:
                             if st.button("Hapus", key=f"del_{cid}"):
                                st.session_state.confirm_del_id = cid
                                st.rerun()

                    # Bagian Bawah: Konfirmasi (Hanya muncul jika ID match)
                    if st.session_state.confirm_del_id == cid:
                        st.divider()
                        st.warning(f"⚠️ Apakah Anda yakin ingin menghapus permanent **{cmeta['judul']}**?")
                        
                        col_y, col_n = st.columns([1, 1])
                        with col_y:
                            if st.button("✅ YA, HAPUS", key=f"yes_{cid}", use_container_width=True):
                                with st.spinner("⏳ Menghapus dari memori & CSV..."):
                                    collection.delete(ids=[cid])
                                    # Sync CSV
                                    sync_delete_csv(cid)
                                    time.sleep(0.5)
                                st.toast(f"Dihapus: {cmeta['judul']}")
                                st.session_state.confirm_del_id = None
                                st.rerun()
                        with col_n:
                            if st.button("❌ BATAL", key=f"no_{cid}", use_container_width=True):
                                st.session_state.confirm_del_id = None
                                st.rerun()

# --- NAVIGASI ---
with st.sidebar:
    st.title("⚡ Menu")
    page = st.radio("Pilih Mode:", ["Chat AI", "Kelola Database"])
    st.caption("v2.2 Hybrid Sync")

if page == "Chat AI": page_chat()
else: page_manage()