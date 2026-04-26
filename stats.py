import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="MabarClan", 
    page_icon="🔱", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        border: 1px solid #2d313e;
    }
    /* Styling khusus tombol Cek Status agar mencolok di mobile */
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
syarat_title = {
    "THE LORD": {"min_kelebihan": 500000, "min_xp": 2000000, "icon": "👑", "color": "#FFFFFF", "desc": "Penguasa tertinggi MabarClan. Legenda hidup."},
    "THE LEGEND": {"min_kelebihan": 150000, "min_xp": 200000, "icon": "🔱", "color": "#FFD700", "desc": "Rank elit. Dewa donasi dan grinding."},
    "THE SULTAN": {"min_kelebihan": 75000, "min_xp": 0, "icon": "💎", "color": "#00FFFF", "desc": "Donatur kelas berat klan."},
    "THE GRINDER": {"min_kelebihan": 0, "min_xp": 150000, "icon": "⚔️", "color": "#FF4500", "desc": "Pejuang XP yang sangat aktif."},
    "THE DISCIPLINE": {"min_kelebihan": 0, "min_xp": 0, "icon": "🛡️", "color": "#32CD32", "desc": "Member teladan, selalu tepat waktu."},
    "THE CASUAL": {"min_kelebihan": -9999999, "min_xp": 0, "icon": "🐢", "color": "#808080", "desc": "Main santai atau sedang nunggak."}
}

def analisis_profil(kelebihan, xp):
    if kelebihan >= 500000 and xp >= 2000000: return "THE LORD"
    elif kelebihan >= 150000 and xp >= 200000: return "THE LEGEND"
    elif kelebihan >= 75000: return "THE SULTAN"
    elif xp >= 150000: return "THE GRINDER"
    elif kelebihan >= 0: return "THE DISCIPLINE"
    else: return "THE CASUAL"

def get_styled_title(title_name):
    info = syarat_title.get(title_name, {"icon": "❓", "color": "white"})
    return f'<span style="color:{info["color"]}; font-weight:bold; text-shadow: 1px 1px 2px black;">{info["icon"]} {title_name}</span>'

# --- 4. DATA LOADING ---
@st.cache_data
def load_data(sheet):
    try:
        file = 'data_member.xlsx'
        df_member = pd.read_excel(file, sheet_name=sheet)
        df_master = pd.read_excel(file, sheet_name='Kompensasi')
        df_list = pd.read_excel(file, sheet_name='List Kompensasi')
        
        df_member['Tanggal_Join'] = pd.to_datetime(df_member['Tanggal_Join'])
        df_member['Total_Gems_Stats'] = pd.to_numeric(df_member['Total_Gems_Stats'], errors='coerce').fillna(0).astype(int)
        df_member['Total_XP_Stats'] = pd.to_numeric(df_member['Total_XP_Stats'], errors='coerce').fillna(0).astype(int)
        
        return df_member.dropna(subset=['Nama']), df_master, df_list
    except Exception as e:
        st.error(f"Error Load Data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🎮 MabarClan")
    periode = st.selectbox("Pilih Periode Data:", ["All Time", "April", "Mei", "Juni"])
    st.divider()
    st.info(f"**Server Status:** Online 🟢\n\n**Version:** 1.1 \n- Mobile Optimized\n- New Rank\n- Smart Rank Requirement\n- All Time Leaderboard\n- Log Kompensasi")

df, df_master, df_list = load_data(periode)

if not df.empty:
    st.title(f"🏆 Clan Tracker Dashboard - {periode}")
    
    # Global Stats Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Gems Clan", f"{int(df['Total_Gems_Stats'].sum()):,}")
    c2.metric("Total XP Clan", f"{int(df['Total_XP_Stats'].sum()):,}")
    c3.metric("Populasi Member", len(df))
    c4.metric("Target Harian", "3,000 Gems")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["🎯 Personal Tracker", "🥇 Global Leaderboard", "📜 Kompensasi Log"])

    # --- TAB 1: PERSONAL TRACKER ---
    with tab1:
        col_in, col_out = st.columns([1, 2])
        with col_in:
            st.subheader("Cek Statusmu")
            nama_user = st.selectbox("Pilih Nama:", df['Nama'].unique())
            data_u = df[df['Nama'] == nama_user].iloc[0]
            
            hari_aktif = max(1, (datetime.now() - data_u['Tanggal_Join']).days)
            target_kumulatif = hari_aktif * 3000
            
            bonus_val = 0
            user_bonuses = df_list[df_list['Nama'] == nama_user]
            for _, b in user_bonuses.iterrows():
                match = df_master[df_master['Jenis Kompensasi'] == b['Jenis Kompensasi']]
                if not match.empty:
                    bonus_val += int(match.iloc[0]['Gems Kompensasi'])
            
            gems_now = st.number_input("Gems Stats Saat Ini:", value=int(data_u['Total_Gems_Stats']), step=1)
            xp_now = int(data_u['Total_XP_Stats'])
            
            # TOMBOL CEK STATUS UNTUK MOBILE
            if st.button("🚀 Cek Status"):
                st.rerun()
            
        with col_out:
            kelebihan = int((gems_now + bonus_val) - target_kumulatif)
            rank_now = analisis_profil(kelebihan, xp_now)
            
            st.markdown(f"## {nama_user} | {get_styled_title(rank_now)}", unsafe_allow_html=True)
            
            # Logika Persentase Rank Up
            ranks_order = ["THE CASUAL", "THE DISCIPLINE", "THE GRINDER", "THE SULTAN", "THE LEGEND", "THE LORD"]
            if rank_now != "THE LORD":
                current_idx = ranks_order.index(rank_now)
                target_rank = ranks_order[current_idx + 1]
                info_target = syarat_title[target_rank]
                
                prog_gems = min(100, int((kelebihan / info_target['min_kelebihan'] * 100))) if info_target['min_kelebihan'] > 0 else 100
                if kelebihan < 0: prog_gems = 0
                prog_xp = min(100, int((xp_now / info_target['min_xp'] * 100))) if info_target['min_xp'] > 0 else 100
                
                total_progress = int((prog_gems + prog_xp) / 2)
                st.write(f"**Persentase Kenaikan Rank ke {target_rank}: {total_progress}%**")
                st.progress(total_progress / 100)
                
                st.markdown("### 📋 Persyaratan Status (Nunggak/Aman):")
                if kelebihan >= 0:
                    st.success(f"✅ **Gems:** Aman (Kelebihan {kelebihan:,} Gems)")
                else:
                    st.error(f"❌ **Gems:** Kurang **{abs(kelebihan):,} Gems**")
                
                st.markdown(f"🚀 **Target Berikutnya:** {get_styled_title(target_rank)}", unsafe_allow_html=True)
                if kelebihan < info_target['min_kelebihan']:
                    st.write(f"🔸 Kurang **{int(info_target['min_kelebihan'] - kelebihan):,} Gems**")
                if xp_now < info_target['min_xp']:
                    st.write(f"🔸 Kurang **{int(info_target['min_xp'] - xp_now):,} XP**")
            else:
                st.write("**Persentase Kenaikan Rank: 100% (MAX)**")
                st.progress(1.0)
                st.warning("👑 Kamu adalah LORD! Rank tertinggi di MabarClan.")

            st.divider()
            res1, res2 = st.columns(2)
            res1.metric("Total Bonus", f"+{int(bonus_val):,}")
            res2.metric("Lama Bergabung", f"{hari_aktif} Hari")

    # --- TAB 2 & 3 TETAP SAMA ---
    with tab2:
        leader_list = []
        for _, row in df.iterrows():
            b_val = 0
            u_bon = df_list[df_list['Nama'] == row['Nama']]
            for _, b in u_bon.iterrows():
                m = df_master[df_master['Jenis Kompensasi'] == b['Jenis Kompensasi']]
                if not m.empty: b_val += int(m.iloc[0]['Gems Kompensasi'])
            days = max(1, (datetime.now() - row['Tanggal_Join']).days)
            surp = int((row['Total_Gems_Stats'] + b_val) - (days * 3000))
            leader_list.append({"Nama": row['Nama'], "Kelebihan": surp, "XP": int(row['Total_XP_Stats']), "Rank": analisis_profil(surp, int(row['Total_XP_Stats']))})
        df_lead = pd.DataFrame(leader_list)
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("🥇 Top Kelebihan Gems")
            dg = df_lead.sort_values('Kelebihan', ascending=False).head(10).copy()
            dg['Kelebihan'] = dg['Kelebihan'].apply(lambda x: f"{x:,}")
            st.table(dg[['Nama', 'Kelebihan', 'Rank']])
        with col_r:
            st.subheader("🏆 Top Grinder XP")
            dx = df_lead.sort_values('XP', ascending=False).head(10).copy()
            dx['XP'] = dx['XP'].apply(lambda x: f"{x:,}")
            st.table(dx[['Nama', 'XP', 'Rank']])

    with tab3:
        st.subheader("Log Kompensasi Clan")
        st.dataframe(df_list, use_container_width=True)
        st.divider()
        st.subheader("Informasi Rank")
        for k in ["THE LORD", "THE LEGEND", "THE SULTAN", "THE GRINDER", "THE DISCIPLINE", "THE CASUAL"]:
            v = syarat_title[k]
            st.markdown(f"{get_styled_title(k)}: {v['desc']}", unsafe_allow_html=True)
            st.caption(f"Syarat: > {int(v['min_kelebihan']):,} Gems & > {int(v['min_xp']):,} XP")

else:
    st.warning("Data tidak terbaca.")

st.markdown("<br><hr><center><b>MabarClan System v1.1</b></center>", unsafe_allow_html=True)
