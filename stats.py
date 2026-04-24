import streamlit as st
import pandas as pd
import random
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(page_title="MabarClan Stats Calculator", page_icon="💎")

# 2. Database Pesan Random (Biar suasana clan tetap positif)
pesan_semangat = [
    "Mantap! Terus pertahankan ritme farming-mu, Clan sangat terbantu! 🔥",
    "Gokil! Kamu salah satu pilar kekuatan MabarClan hari ini. 🛡️",
    "GGWP! Tabungan gems aman, bisa santai sejenak sambil ngopi. ☕",
    "Luar biasa kontribusinya! Semoga gacha kamu wangi terus ya! ✨",
    "Keren banget! Dengan member kayak kamu, Clan kita bakal level up cepat! 🚀"
]

pesan_dukungan = [
    "Semangat farming-nya! Pelan tapi pasti, kita kejar bareng-bareng. 💪",
    "Jangan menyerah! Sedikit lagi target tercapai, kamu pasti bisa. ✨",
    "Yuk cicil lagi gems-nya. Kalau ada kendala, jangan ragu lapor ke Steve ya! 🤝",
    "Fokus grinding hari ini, kita butuh kekuatan kamu untuk grow bareng! 📈",
    "Tenang, masih ada waktu buat ngejar. Semangat lunasin nunggaknya! ⚡"
]

# 3. Fungsi Load Data dari Excel
@st.cache_data
def load_member_data():
    try:
        # Membaca file excel (Pastikan file ini ada di folder yang sama di GitHub/PC)
        df = pd.read_excel('data_member.xlsx')
        df['Tanggal_Join'] = pd.to_datetime(df['Tanggal_Join'])
        return df
    except Exception as e:
        st.error(f"Gagal membaca file Excel: {e}")
        return pd.DataFrame()

# Tampilkan Judul
st.title("💎 MabarClan Stats Calculator")
st.caption("Management System by Steve")

df_member = load_member_data()

if not df_member.empty:
    # 4. Input Area
    with st.container():
        nama_pilihan = st.selectbox("Pilih Nama Member", df_member['Nama'].tolist())
        
        # Ambil data spesifik member
        data_user = df_member[df_member['Nama'] == nama_pilihan].iloc[0]
        tgl_join = data_user['Tanggal_Join']
        status_komp = data_user['Kompensasi']
        
        # Hitung selisih hari otomatis (Mencegah TypeError dengan .days)
        hari_ini = datetime.now()
        total_hari_di_clan = (hari_ini - tgl_join).days
        
        # Pengaman jika baru join hari ini
        if total_hari_di_clan <= 0: total_hari_di_clan = 1
        
        st.info(f"📅 Tanggal Join: {tgl_join.strftime('%d %B %Y')} | ⏳ Masa Aktif: {total_hari_di_clan} Hari")

    # 5. Input Gems dari Stats Game
    gems_game = st.number_input(f"Masukkan Total Gems sesuai stats {nama_pilihan} di Game:", min_value=0, step=100)

    if st.button("Cek Status"):
        # --- LOGIKA PERHITUNGAN ---
        
        # Bonus 30.000 Gems jika status Kompensasi = Ya (Setara 10 hari)
        bonus_kompensasi = 30000 if status_komp == 'Ya' else 0
        total_donasi_akumulasi = gems_game + bonus_kompensasi
        
        # Target: 3.000 Gems per Hari Masa Aktif
        target_seharusnya = total_hari_di_clan * 3000
        
        # Selisih dalam Gems
        selisih_gems = total_donasi_akumulasi - target_seharusnya
        
        # Hitung konversi hari (Pembulatan ke bawah menggunakan //)
        jumlah_hari_selisih = abs(selisih_gems) // 3000
        
        st.divider()
        
        # Tampilan Metrik Utama
        col1, col2 = st.columns(2)
        col1.metric("Total Donasi (+Bonus)", f"{total_donasi_akumulasi:,} Gems")
        col2.metric("Target Seharusnya", f"{target_seharusnya:,} Gems")

        if selisih_gems >= 0:
            # Tampilan jika Aman
            st.success(f"✅ **{nama_pilihan} AMAN**")
            st.balloons()
            st.write(f"💬 _{random.choice(pesan_semangat)}_")
            st.write(f"Kelebihan Donasi: **{selisih_gems:,} Gems**")
            st.write(f"📈 Status: Member ini **kelebihan {jumlah_hari_selisih} hari** (Bisa libur setor).")
        else:
            # Tampilan jika Nunggak
            st.error(f"❌ **{nama_pilihan} NUNGGAK**")
            st.write(f"💬 _{random.choice(pesan_dukungan)}_")
            st.write(f"Kekurangan Donasi: **{abs(selisih_gems):,} Gems**")
            st.warning(f"⚠️ Status: Member ini **tertinggal {jumlah_hari_selisih} hari** setoran.")
            
        # Catatan kaki untuk transparansi
        if status_komp == 'Ya':
            st.caption("💡 *Note: Total donasi sudah termasuk Bonus Kompensasi 10 hari (30.000 Gems) karena kontribusi sejak Clan LV 1.*")

else:
    st.warning("⚠️ Data member kosong. Pastikan file 'data_member.xlsx' sudah diunggah ke GitHub.")

# Sidebar info
st.sidebar.markdown(f"""
### **Info Clan**
- **Nama:** MabarClan
- **Leader:** Steve
- **Rules:** 3.000 Gems / Day
- **Date:** {datetime.now().strftime('%d %m %Y')}
""")
