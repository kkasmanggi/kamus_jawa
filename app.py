import streamlit as st
import google.generativeai as genai
import os

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(
    page_title="Chatbot Kamus Bahasa Jawa",
    page_icon="📖",
)

st.title("📖 Chatbot Kamus Bahasa Jawa")
st.markdown("Masukkan kata dalam bahasa Jawa untuk dicari artinya.")
st.divider()

# --- Pengaturan API Key ---
# Ambil API key dari Streamlit Secrets.
# Ini adalah cara paling aman untuk menyimpan kredensial di Streamlit Community Cloud.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key Gemini tidak ditemukan. Harap tambahkan 'GEMINI_API_KEY' ke Streamlit Secrets.")
    st.stop()

# --- Pengaturan Model Gemini ---
MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    MODEL_NAME,
    generation_config=genai.types.GenerationConfig(
        temperature=0.4,
        max_output_tokens=500
    )
)

# --- Konteks Awal Chat ---
# Konteks awal yang akan digunakan untuk menginisialisasi sesi chat.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah kamus bahasa jawa. Masukkan kata yang ingin kalian cari tahu artinya dalam bahasa jawa. Jawaban singkat. Tolak pertanyaan selain bahasa jawa."]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan kata yang akan dicari artinya."]
    }
]

# --- Inisialisasi Riwayat Chat ---
# Menggunakan st.session_state untuk menyimpan riwayat chat.
# Ini penting agar riwayat chat tidak hilang saat halaman di-refresh.
if "history" not in st.session_state:
    st.session_state["history"] = INITIAL_CHATBOT_CONTEXT

if "chat_session" not in st.session_state:
    st.session_state["chat_session"] = model.start_chat(history=st.session_state["history"])

# --- Menampilkan Riwayat Chat ---
for message in st.session_state.history:
    if message["role"] != "system":  # Abaikan pesan sistem
        with st.chat_message(message["role"]):
            st.markdown(message["parts"][0])

# --- Logika Input Pengguna ---
user_input = st.chat_input("Tanyakan sesuatu...")

if user_input:
    # Tampilkan pesan pengguna di antarmuka
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Tambahkan input pengguna ke riwayat
    st.session_state.history.append({"role": "user", "parts": [user_input]})

    # Kirim pesan ke Gemini API dan dapatkan respons
    try:
        with st.spinner("Sedang mencari arti..."):
            response = st.session_state.chat_session.send_message(user_input, request_options={"timeout": 60})
            
        # Tampilkan respons dari Gemini
        with st.chat_message("model"):
            if response and response.text:
                st.markdown(response.text)
                st.session_state.history.append({"role": "model", "parts": [response.text]})
            else:
                st.markdown("Maaf, saya tidak bisa memberikan balasan.")
    
    except Exception as e:
        st.error(f"Terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
        st.info("Pastikan API Key Anda benar dan koneksi internet stabil.")
