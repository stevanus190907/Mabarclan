import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh 
import plotly.express as px 

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="MabarClan", 
    page_icon="🔱", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# AUTO-REFRESH SETIAP 10 DETIK
st_autorefresh(interval=10000, key="datarefresh")

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.3);
        padding: 15px 20px;
        border-radius: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #32CD32;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & LOGIKA RANK ---
# Menyesuaikan Nama Rank sesuai urutan baru
syarat_title = {
    "CO-LEADER": {"min_kelebihan": 500000, "min_xp": 2000000, "icon": "👑", "color": "#FFFFFF", "desc": "Legenda hidup MabarClan."},
    "ELDER": {"min_kelebihan": 150000, "min_xp": 1000000, "icon": "🔱", "color": "#FFD700", "desc": "Dewa donasi dan grinding."},
    "VETERAN-GEMS": {"min_kelebihan": 75000, "min_xp": 0, "icon": "💎", "color": "#00FFFF", "desc": "Donatur kelas berat klan."},
    "VETERAN-XP": {"min_kelebihan": 0, "min_xp": 500000, "icon": "⚔️", "color": "#FF4500", "desc": "Pejuang XP sangat aktif."},
    "MEMBER": {"min_kelebihan": 21000, "min_xp": 0, "icon": "🛡️", "color": "#32CD32", "desc": "Selalu tepat waktu & berkontribusi."},
    "ROOKIE": {"min_kelebihan": -9999999, "min_xp": 0, "icon": "🐢", "color": "#808080", "desc": "Status sedang nunggak atau member baru."}
}

def analisis_profil(kelebihan, xp):
    if kelebihan >= 500000 and xp >= 2000000: return "CO-LEADER"
    elif kelebihan >= 150000 and xp >= 1000000: return "ELDER"
    elif kelebihan >= 75000: return "VETERAN-GEMS"
    elif xp >= 500000: return "VETERAN-XP"
    elif kelebihan >= 21000: return "MEMBER"
    else: return "ROOKIE"

def get_styled_title(title_name):
    info = syarat_title.get(title_name, {"icon": "❓", "color": "white"})
    return f'<span style="color:{info["color"]}; font-weight:bold; text-shadow: 1px 1px 2px black;">{info["icon"]} {title_name}</span>'

# --- 4. DATA LOADING ---
@st.cache_data(ttl=60)
def load_data(sheet):
    try:
        file = 'data_member_fix5.xlsx'
        xls = pd.ExcelFile(file)
        
        df_member = pd.read_excel(file, sheet_name=sheet) if sheet in xls.sheet_names else pd.DataFrame()
        df_master = pd.read_excel(file, sheet_name='Kompensasi') if 'Kompensasi' in xls.sheet_names else pd.DataFrame()
        df_list = pd.read_excel(file, sheet_name='List Kompensasi') if 'List Kompensasi' in xls.sheet_names else pd.DataFrame()
        
        if not df_member.empty:
            df_member = df_member.dropna(subset=['Nama'])
            df_member['Nama'] = df_member['Nama'].astype(str).str.strip()
            df_member['Tanggal_Join'] = pd.to_datetime(df_member['Tanggal_Join'], errors='coerce')
            df_member = df_member.dropna(subset=['Tanggal_Join'])
            df_member['Total_Gems_Stats'] = pd.to_numeric(df_member['Total_Gems_Stats'], errors='coerce').fillna(0).astype(int)
            df_member['Total_XP_Stats'] = pd.to_numeric(df_member['Total_XP_Stats'], errors='coerce').fillna(0).astype(int)
        
        return df_member, df_master, df_list
    except Exception as e:
        st.error(f"Error Load Data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🎮 MabarClan")
    tz_jkt = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz_jkt)
    st.markdown(f"""
        <div style="background-color: #1e2130; padding: 15px; border-radius: 10px; border: 2px solid #32CD32; text-align: center;">
            <h1 style="color: #32CD32; margin: 0; font-family: 'Courier New';">{now.strftime('%H:%M:%S')}</h1>
            <p style="font-size: 0.9em; margin: 0; color: #808080;">{now.strftime('%A, %d %b %Y')}</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    periode = st.selectbox("Pilih Periode Data:", ["All Time", "April", "Mei", "Juni"])

df, df_master, df_list = load_data(periode)

if not df.empty:
    st.title(f"🏆 Clan Dashboard - {periode}")
    
    total_gems_clan = int(df['Total_Gems_Stats'].sum())
    total_xp_clan = int(df['Total_XP_Stats'].sum())
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Gems Clan", f"{total_gems_clan:,}")
    c2.metric("Total XP Clan", f"{total_xp_clan:,}")
    c3.metric("Populasi Member", len(df))
    c4.metric("Target Harian", "3,000 Gems")

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Personal Tracker", "🥇 Global Leaderboard", "📜 Kompensasi Log", "ℹ️ Info Rank"])

    with tab1:
        col_in, col_out = st.columns([1, 2])
        with col_in:
            st.subheader("Cek Statusmu")
            nama_user = st.selectbox("Pilih Nama:", df['Nama'].unique())
            data_u = df[df['Nama'] == nama_user].iloc[0]
            
            hari_aktif = max(1, (datetime.now(tz_jkt).replace(tzinfo=None) - data_u['Tanggal_Join']).days)
            target_kumulatif = hari_aktif * 3000
            
            bonus_val = 0
            if not df_list.empty:
                user_bonuses = df_list[df_list['Nama'] == nama_user]
                for _, b in user_bonuses.iterrows():
                    match = df_master[df_master['Jenis Kompensasi'] == b['Jenis Kompensasi']]
                    if not match.empty: bonus_val += int(match.iloc[0]['Gems Kompensasi'])
            
            gems_now = st.number_input("Gems Stats Saat Ini:", value=int(data_u['Total_Gems_Stats']), step=100)
            xp_now = st.number_input("XP Stats Saat Ini:", value=int(data_u['Total_XP_Stats']), step=100)
            
            if st.button("🚀 Update & Cek Status"):
                kelebihan_temp = int((gems_now + bonus_val) - target_kumulatif)
                rank_temp = analisis_profil(kelebihan_temp, xp_now)
                st.toast(f"Status {nama_user} diperbarui!", icon="ℹ️")

        with col_out:
            kelebihan = int((gems_now + bonus_val) - target_kumulatif)
            rank_now = analisis_profil(kelebihan, xp_now)
            st.markdown(f"## {nama_user} | {get_styled_title(rank_now)}", unsafe_allow_html=True)
            
            if kelebihan >= 0:
                st.success(f"✅ **Gems:** Aman (Kelebihan {kelebihan:,} Gems)")
            else:
                st.error(f"⚠️ **Gems:** Nunggak (Kurang {abs(kelebihan):,} Gems)")
            
            # Progress Rank
            ranks_order = ["ROOKIE", "MEMBER", "VETERAN-XP", "VETERAN-GEMS", "ELDER", "CO-LEADER"]
            if rank_now != "CO-LEADER":
                idx = ranks_order.index(rank_now)
                target_rank = ranks_order[idx + 1]
                info_t = syarat_title[target_rank]
                
                st.markdown(f"### 🚀 Syarat Naik ke {get_styled_title(target_rank)}:", unsafe_allow_html=True)
                if kelebihan < info_t['min_kelebihan']:
                    st.write(f"🔸 Gems Kurang: **{int(info_t['min_kelebihan'] - kelebihan):,} Gems**")
                if xp_now < info_t['min_xp']:
                    st.write(f"🔸 XP Kurang: **{int(info_t['min_xp'] - xp_now):,} XP**")

    with tab2:
        leader_list = []
        for _, row in df.iterrows():
            # (Logika perhitungan leaderboard sama dengan tracker)
            leader_list.append({"Nama": row['Nama'], "XP": row['Total_XP_Stats'], "Rank": analisis_profil(0, row['Total_XP_Stats'])})
        st.dataframe(pd.DataFrame(leader_list), use_container_width=True)

    with tab3:
        st.dataframe(df_list, use_container_width=True)

    with tab4:
        st.subheader("🔱 Informasi Rank")
        # Urutan tampilan rank dari tertinggi ke terendah
        view_order = ["CO-LEADER", "ELDER", "VETERAN-GEMS", "VETERAN-XP", "MEMBER", "ROOKIE"]
        for k in view_order:
            v = syarat_title[k]
            rk, ds, rq = st.columns([1.5, 2, 1.5])
            with rk: st.markdown(f"#### {get_styled_title(k)}", unsafe_allow_html=True)
            with ds: st.write(f"*{v['desc']}*")
            with rq: 
                st.write(f"💎 Gems: {int(v['min_kelebihan']):,}")
                st.write(f"⚔️ XP: {int(v['min_xp']):,}")
            st.divider()

else:
    st.warning("Data tidak tersedia.")
