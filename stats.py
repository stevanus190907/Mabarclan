import streamlit as st
import pandas as pd
import random
from datetime import datetime
from streamlit_autorefresh import st_autorefresh 
import plotly.express as px 

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="MabarClan", 
    page_icon="🔱", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# AUTO-REFRESH SETIAP 10 DETIK UNTUK JAM LIVE
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
    /* Kotak Sampel Warna Legend */
    .color-box {
        display: inline-block;
        width: 14px;
        height: 14px;
        margin-right: 8px;
        border-radius: 3px;
        vertical-align: middle;
        border: 1px solid rgba(255,255,255,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & LOGIKA RANK ---
syarat_title = {
    "THE LORD": {"min_kelebihan": 500000, "min_xp": 2000000, "icon": "👑", "color": "#FFFFFF", "desc": "Legenda hidup MabarClan."},
    "THE LEGEND": {"min_kelebihan": 150000, "min_xp": 200000, "icon": "🔱", "color": "#FFD700", "desc": "Dewa donasi dan grinding."},
    "THE SULTAN": {"min_kelebihan": 75000, "min_xp": 0, "icon": "💎", "color": "#00FFFF", "desc": "Donatur kelas berat klan."},
    "THE GRINDER": {"min_kelebihan": 0, "min_xp": 150000, "icon": "⚔️", "color": "#FF4500", "desc": "Pejuang XP sangat aktif."},
    "THE DISCIPLINE": {"min_kelebihan": 0, "min_xp": 0, "icon": "🛡️", "color": "#32CD32", "desc": "Selalu tepat waktu."},
    "THE CASUAL": {"min_kelebihan": -9999999, "min_xp": 0, "icon": "🐢", "color": "#808080", "desc": "Status sedang nunggak."}
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
        df_member['Nama'] = df_member['Nama'].astype(str).str.strip()
        df_list['Nama'] = df_list['Nama'].astype(str).str.strip()
        df_member = df_member[~df_member['Nama'].isin(['nan', 'None', '', 'NaN'])]
        df_member['Tanggal_Join'] = pd.to_datetime(df_member['Tanggal_Join'])
        df_member['Total_Gems_Stats'] = pd.to_numeric(df_member['Total_Gems_Stats'], errors='coerce').fillna(0).astype(int)
        df_member['Total_XP_Stats'] = pd.to_numeric(df_member['Total_XP_Stats'], errors='coerce').fillna(0).astype(int)
        return df_member, df_master, df_list
    except Exception as e:
        st.error(f"Error Load Data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🎮 MabarClan")
    now = datetime.now()
    st.markdown(f"""
        <div style="background-color: #1e2130; padding: 15px; border-radius: 10px; border: 2px solid #32CD32; text-align: center;">
            <h1 style="color: #32CD32; margin: 0; font-family: 'Courier New';">{now.strftime('%H:%M:%S')}</h1>
            <p style="font-size: 0.9em; margin: 0; color: #808080;">{now.strftime('%A, %d %b %Y')}</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    periode = st.selectbox("Pilih Periode Data:", ["All Time", "April", "Mei", "Juni"])
    st.info("**Version:** 1.2\n- Fixed Visual UI/UX for Light Mode\n- New Interactive System\n- New Pie Chart Contribution\n- Added XP Input")

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

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Personal Tracker", "🥇 Global Leaderboard", "📜 Kompensasi Log", "ℹ️ Info Rank"])

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
                if not match.empty: bonus_val += int(match.iloc[0]['Gems Kompensasi'])
            
            gems_now = st.number_input("Gems Stats Saat Ini (HARAP UPDATE MANUAL):", value=int(data_u['Total_Gems_Stats']), step=100)
            xp_now = st.number_input("XP Stats Saat Ini (HARAP UPDATE MANUAL):", value=int(data_u['Total_XP_Stats']), step=100)
            
            if st.button("🚀 Update & Cek Status"):
                kelebihan_temp = int((gems_now + bonus_val) - target_kumulatif)
                rank_temp = analisis_profil(kelebihan_temp, xp_now)
                if kelebihan_temp >= 0:
                    st.toast(f"Mantap {nama_user}! Kontribusi aman. 🔥", icon="✅")
                    if rank_temp in ["THE LORD", "THE LEGEND"]: st.balloons()
                else:
                    st.toast(f"Ayo {nama_user}, target belum tercapai. 🐢", icon="⚠️")

        with col_out:
            kelebihan = int((gems_now + bonus_val) - target_kumulatif)
            rank_now = analisis_profil(kelebihan, xp_now)
            st.markdown(f"## {nama_user} | {get_styled_title(rank_now)}", unsafe_allow_html=True)
            
            st.markdown("### 📋 Status Gems Aman/Nunggak:")
            if kelebihan >= 0:
                st.success(f"✅ **Gems:** Aman (Kelebihan {kelebihan:,} Gems)")
            else:
                st.error(f"⚠️ **Gems:** Nunggak (Kurang {abs(kelebihan):,} Gems)")
            
            # --- SYNERGY CONTRIBUTION CHART (COLOR LOCKED) ---
            share_gems = (gems_now / total_gems_clan) if total_gems_clan > 0 else 0
            share_xp = (xp_now / total_xp_clan) if total_xp_clan > 0 else 0
            total_synergy_share = (share_gems + share_xp) / 2
            
            # Persiapkan data dengan label spesifik untuk color_discrete_map
            pie_data = pd.DataFrame({
                "Kategori": ["Diri Sendiri", "Member Lain"],
                "Nilai": [total_synergy_share, max(0, 1 - total_synergy_share)]
            })
            
            fig_synergy = px.pie(
                pie_data,
                values="Nilai", 
                names="Kategori",
                hole=0.6,
                # Pemetaan warna wajib sinkron dengan label di atas
                color="Kategori",
                color_discrete_map={
                    "Diri Sendiri": "#32CD32", 
                    "Member Lain": "#262730"
                },
                title=f"Skor Kontribusi Klan: {nama_user}"
            )
            fig_synergy.update_layout(showlegend=False, height=260, margin=dict(t=50, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            fig_synergy.update_traces(textinfo='percent', textfont_size=14)
            st.plotly_chart(fig_synergy, use_container_width=True)
            
            # Legenda Visual yang Sesuai dengan Chart
            st.markdown(f"""
                <div style="display: flex; justify-content: center; gap: 30px; font-size: 0.95em; background-color: rgba(128,128,128,0.05); padding: 12px; border-radius: 10px; border: 1px solid rgba(128,128,128,0.1);">
                    <div><span class="color-box" style="background-color: #32CD32; box-shadow: 0 0 5px #32CD32;"></span><b>Kontribusi {nama_user} (Hijau)</b></div>
                    <div><span class="color-box" style="background-color: #262730; border: 1px solid #444;"></span><b>Member Klan Lain (Abu)</b></div>
                </div>
            """, unsafe_allow_html=True)

            # --- PROGRESS RANK ---
            ranks_order = ["THE CASUAL", "THE DISCIPLINE", "THE GRINDER", "THE SULTAN", "THE LEGEND", "THE LORD"]
            if rank_now != "THE LORD":
                current_idx = ranks_order.index(rank_now)
                target_rank = ranks_order[current_idx + 1]
                info_target = syarat_title[target_rank]
                prog_gems = min(100, int((max(0, kelebihan) / info_target['min_kelebihan'] * 100))) if info_target['min_kelebihan'] > 0 else 100
                prog_xp = min(100, int((xp_now / info_target['min_xp'] * 100))) if info_target['min_xp'] > 0 else 100
                total_progress = int((prog_gems + prog_xp) / 2)
                
                st.write(f"**Progress ke {target_rank}: {total_progress}%**")
                st.progress(total_progress / 100)
                
                st.markdown(f"### 🚀 Syarat Naik ke {get_styled_title(target_rank)}:", unsafe_allow_html=True)
                if kelebihan < info_target['min_kelebihan']:
                    st.write(f"🔸 Gems Kurang: **{int(info_target['min_kelebihan'] - kelebihan):,} Gems**")
                if xp_now < info_target['min_xp']:
                    st.write(f"🔸 XP Kurang: **{int(info_target['min_xp'] - xp_now):,} XP**")
                
            st.divider()
            res1, res2, res3 = st.columns(3)
            res1.metric("Lama Bergabung", f"{hari_aktif} Hari")
            res2.metric("Total Bonus", f"+{int(bonus_val):,}")
            res3.metric("Score Kontribusi", f"{(total_synergy_share * 100):.2f}%")

    with tab2:
        leader_list = []
        for _, row in df.iterrows():
            b_total = 0
            u_b = df_list[df_list['Nama'] == row['Nama']]
            for _, b in u_b.iterrows():
                m = df_master[df_master['Jenis Kompensasi'] == b['Jenis Kompensasi']]
                if not m.empty: b_total += int(m.iloc[0]['Gems Kompensasi'])
            days = max(1, (datetime.now() - row['Tanggal_Join']).days)
            surp = int((row['Total_Gems_Stats'] + b_total) - (days * 3000))
            leader_list.append({"Nama": row['Nama'], "Kelebihan": surp, "XP": int(row['Total_XP_Stats']), "Rank": analisis_profil(surp, int(row['Total_XP_Stats']))})
        
        df_lead = pd.DataFrame(leader_list)
        cl1, cl2 = st.columns(2)
        with cl1:
            st.subheader("🥇 Top Gems Kelebihan")
            dg = df_lead.sort_values('Kelebihan', ascending=False).head(15).reset_index(drop=True)
            dg.index += 1
            st.table(dg[['Nama', 'Kelebihan', 'Rank']])
        with cl2:
            st.subheader("🏆 Top Grinder XP")
            dx = df_lead.sort_values('XP', ascending=False).head(15).reset_index(drop=True)
            dx.index += 1
            st.table(dx[['Nama', 'XP', 'Rank']])

    with tab3:
        st.subheader("📜 Log Kompensasi Clan")
        st.dataframe(df_list, use_container_width=True)

    with tab4:
        st.subheader("🔱 Informasi Rank")
        order = ["THE LORD", "THE LEGEND", "THE SULTAN", "THE GRINDER", "THE DISCIPLINE", "THE CASUAL"]
        for k in order:
            v = syarat_title[k]
            rk, ds, rq = st.columns([1, 2, 1.5])
            with rk: st.markdown(f"### {get_styled_title(k)}", unsafe_allow_html=True)
            with ds: st.write(f"**Deskripsi:** \n{v['desc']}")
            with rq:
                st.write("**Syarat Minimal:**"); st.write(f"💎 Gems: {int(v['min_kelebihan']):,}"); st.write(f"⚔️ XP: {int(v['min_xp']):,}")
            st.divider()

else:
    st.warning("Data tidak terbaca.")

st.markdown("<br><hr><center><b>MabarClan System v1.2 </b></center>", unsafe_allow_html=True)
