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
syarat_title = {
    "CO-LEADER": {"min_kelebihan": 500000, "min_xp": 2000000, "icon": "👑", "color": "#FFFFFF", "desc": "Legenda hidup MabarClan."},
    "ELDER": {"min_kelebihan": 150000, "min_xp": 1000000, "icon": "🔱", "color": "#FFD700", "desc": "Dewa donasi dan grinding."},
    "VETERAN-GEMS": {"min_kelebihan": 75000, "min_xp": 0, "icon": "💎", "color": "#00FFFF", "desc": "Donatur gems kelas berat klan."},
    "VETERAN-XP": {"min_kelebihan": 0, "min_xp": 500000, "icon": "⚔️", "color": "#FF4500", "desc": "Pejuang XP sangat aktif."},
    "MEMBER": {"min_kelebihan": 0, "min_xp": 0, "icon": "🛡️", "color": "#32CD32", "desc": "Berkontribusi setidaknya 7 hari di klan sesuai syarat."},
    "ROOKIE": {"min_kelebihan": -9999999, "min_xp": 0, "icon": "🐢", "color": "#808080", "desc": "Status sedang nunggak atau member baru."}
}

def analisis_profil(kelebihan, xp):
    if kelebihan >= 500000 and xp >= 2000000: return "CO-LEADER"
    elif kelebihan >= 150000 and xp >= 1000000: return "ELDER"
    elif kelebihan >= 75000: return "VETERAN-GEMS"
    elif xp >= 500000: return "VETERAN-XP"
    elif kelebihan >= 0: return "MEMBER"
    else: return "ROOKIE"

def get_styled_title(title_name):
    info = syarat_title.get(title_name, {"icon": "❓", "color": "white"})
    return f'<span style="color:{info["color"]}; font-weight:bold; text-shadow: 1px 1px 2px black;">{info["icon"]} {title_name}</span>'

# --- 4. DATA LOADING ---
@st.cache_data(ttl=60)
def load_data(sheet):
    try:
        file = 'data_member_fix6.xlsx'
        df_member = pd.read_excel(file, sheet_name=sheet)
        df_master = pd.read_excel(file, sheet_name='Kompensasi')
        df_list = pd.read_excel(file, sheet_name='List Kompensasi')
        
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

# --- 5. SIDEBAR & TIME ---
tz_jkt = pytz.timezone('Asia/Jakarta')
now_jkt = datetime.now(tz_jkt)
now_naive = now_jkt.replace(tzinfo=None)

with st.sidebar:
    st.header("🎮 MabarClan")
    st.markdown(f"""
        <div style="background-color: #1e2130; padding: 15px; border-radius: 10px; border: 2px solid #32CD32; text-align: center;">
            <h1 style="color: #32CD32; margin: 0; font-family: 'Courier New';">{now_jkt.strftime('%H:%M:%S')}</h1>
            <p style="font-size: 0.9em; margin: 0; color: #808080;">{now_jkt.strftime('%A, %d %b %Y')}</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    periode = st.selectbox("Pilih Periode Data:", ["All Time", "April", "Mei", "Juni"])
    st.info("**Version:** 1.2.3\n- Leaderboard shows Pure Surplus Gems\n- Compensation accumulated to Surplus\n- Tracker Bonus Summary")

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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Tracker", "🥇 Leaderboard", "📜 Kompensasi", "ℹ️ Info Rank", "⚖️ Rules Rank"])

    with tab1:
        col_in, col_out = st.columns([1, 2])
        with col_in:
            st.subheader("Cek Statusmu")
            nama_user = st.selectbox("Pilih Nama:", sorted(df['Nama'].unique()))
            data_u = df[df['Nama'] == nama_user].iloc[0]
            
            # Hitung Hari & Target
            tgl_join = data_u['Tanggal_Join'].replace(tzinfo=None)
            hari_aktif = max(1, (now_naive - tgl_join).days)
            target_kumulatif = hari_aktif * 3000
            
            # Hitung Total Bonus
            bonus_val = 0
            if not df_list.empty:
                user_bonuses = df_list[df_list['Nama'] == nama_user]
                for _, b in user_bonuses.iterrows():
                    match = df_master[df_master['Jenis Kompensasi'] == b['Jenis Kompensasi']]
                    if not match.empty: 
                        bonus_val += int(match.iloc[0]['Gems Kompensasi'])

            gems_now = st.number_input("Gems Stats Saat Ini:", value=int(data_u['Total_Gems_Stats']), step=100)
            xp_now = st.number_input("XP Stats Saat Ini:", value=int(data_u['Total_XP_Stats']), step=100)
            
            if st.button("🚀 Update & Cek Status"):
                kelebihan_temp = int((gems_now + bonus_val) - target_kumulatif)
                if kelebihan_temp >= 0: st.toast(f"Mantap {nama_user}! Kontribusi aman. 🔥", icon="✅")
                else: st.toast(f"Ayo {nama_user}, target belum tercapai. 🐢", icon="⚠️")
            
            st.markdown("---")
            st.metric("Total Bonus Kompensasi", f"{bonus_val:,} Gems")
            st.caption("Bonus otomatis menambah nilai 'Kelebihan Gems' Anda.")

        with col_out:
            total_gems_user = gems_now + bonus_val
            kelebihan = int(total_gems_user - target_kumulatif)
            rank_now = analisis_profil(kelebihan, xp_now)
            
            st.markdown(f"## {nama_user} | {get_styled_title(rank_now)}", unsafe_allow_html=True)
            
            if kelebihan >= 0: 
                st.success(f"✅ **Kelebihan Gems:** {kelebihan:,}")
            else: 
                st.error(f"⚠️ **Nunggak Gems:** {abs(kelebihan):,}")
            
            st.write(f"Rumus: (Stats {gems_now:,} + Bonus {bonus_val:,}) - Target {target_kumulatif:,}")

            # Synergy Pie
            share_gems = (total_gems_user / total_gems_clan) if total_gems_clan > 0 else 0
            share_xp = (xp_now / total_xp_clan) if total_xp_clan > 0 else 0
            total_synergy_share = (share_gems + share_xp) / 2
            
            pie_data = pd.DataFrame({"Kategori": ["Diri Sendiri", "Member Lain"], "Nilai": [total_synergy_share, max(0, 1 - total_synergy_share)]})
            fig_synergy = px.pie(pie_data, values="Nilai", names="Kategori", hole=0.6, color="Kategori", color_discrete_map={"Diri Sendiri": "#32CD32", "Member Lain": "#262730"})
            fig_synergy.update_layout(showlegend=False, height=260, margin=dict(t=30, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig_synergy, use_container_width=True)
            
            # Info Naik Rank
            ranks_order = ["ROOKIE", "MEMBER", "VETERAN-XP", "VETERAN-GEMS", "ELDER", "CO-LEADER"]
            if rank_now != "CO-LEADER":
                idx = ranks_order.index(rank_now); target_rank = ranks_order[idx + 1]; info_target = syarat_title[target_rank]
                st.markdown(f"### 🚀 Syarat ke {get_styled_title(target_rank)}:", unsafe_allow_html=True)
                if kelebihan < info_target['min_kelebihan']: st.write(f"🔸 Kurang Kelebihan: **{int(info_target['min_kelebihan'] - kelebihan):,} Gems**")
                if xp_now < info_target['min_xp']: st.write(f"🔸 Kurang XP: **{int(info_target['min_xp'] - xp_now):,} XP**")
            
            st.divider()
            r1, r2, r3 = st.columns(3)
            r1.metric("Lama Join", f"{hari_aktif} Hari")
            r2.metric("Tanggal Join", data_u['Tanggal_Join'].strftime('%d %b %Y'))
            r3.metric("Kontribusi", f"{(total_synergy_share * 100):.2f}%")

    with tab2:
        leader_list = []
        for _, row in df.iterrows():
            b_total = 0
            if not df_list.empty:
                u_b = df_list[df_list['Nama'] == row['Nama']]
                for _, b in u_b.iterrows():
                    m = df_master[df_master['Jenis Kompensasi'] == b['Jenis Kompensasi']]
                    if not m.empty: b_total += int(m.iloc[0]['Gems Kompensasi'])
            
            h_aktif = max(1, (now_naive - row['Tanggal_Join'].replace(tzinfo=None)).days)
            # HITUNG KELEBIHAN SAJA (Stats + Bonus - Target)
            kelebihan_murni = int((row['Total_Gems_Stats'] + b_total) - (h_aktif * 3000))
            
            leader_list.append({
                "Nama": row['Nama'], 
                "Kelebihan Gems": kelebihan_murni, 
                "XP": int(row['Total_XP_Stats']), 
                "Rank": analisis_profil(kelebihan_murni, int(row['Total_XP_Stats']))
            })
            
        df_lead = pd.DataFrame(leader_list)
        cl1, cl2 = st.columns(2)
        with cl1:
            st.subheader("🥇 Top Kelebihan Gems (Net)")
            # Tampilkan hanya kolom Kelebihan Gems
            dg = df_lead.sort_values('Kelebihan Gems', ascending=False).head(15).reset_index(drop=True); dg.index += 1
            st.table(dg[['Nama', 'Kelebihan Gems', 'Rank']])
        with cl2:
            st.subheader("🏆 Top Grinder XP")
            dx = df_lead.sort_values('XP', ascending=False).head(15).reset_index(drop=True); dx.index += 1
            st.table(dx[['Nama', 'XP', 'Rank']])

    with tab3:
        st.subheader("📜 Log Kompensasi Clan")
        st.dataframe(df_list, use_container_width=True)

    with tab4:
        st.subheader("🔱 Informasi Rank")
        view_order = ["CO-LEADER", "ELDER", "VETERAN-GEMS", "VETERAN-XP", "MEMBER", "ROOKIE"]
        for k in view_order:
            v = syarat_title[k]
            rk, ds, rq = st.columns([1.5, 2, 1.5])
            with rk: st.markdown(f"#### {get_styled_title(k)}", unsafe_allow_html=True)
            with ds: st.write(f"*{v['desc']}*")
            with rq: st.write(f"💎 Gems: {int(v['min_kelebihan']):,}"); st.write(f"⚔️ XP: {int(v['min_xp']):,}")
            st.divider()

    with tab5:
        st.subheader("⚖️ Rules Role/Jabatan")
        st.error("**⚠️ PERINGATAN KERAS:** Pelanggaran berat bisa berakibat Kick/Blacklist dan ganti rugi aset klan.")
        c_eld, c_co = st.columns(2)
        with c_eld:
            st.markdown(f"### {get_styled_title('ELDER')}", unsafe_allow_html=True)
            st.info("Berhak moderasi member nunggak & invite member baru. Wajib jaga stats tetap di level Elder.")
        with c_co:
            st.markdown(f"### {get_styled_title('CO-LEADER')}", unsafe_allow_html=True)
            st.warning("Dilarang merusak tatanan World Clan. Berhak moderasi penuh & invite. Wajib performa stabil.")
else:
    st.warning("Data tidak terbaca atau Excel kosong.")

st.markdown("<br><hr><center><b>MabarClan System v1.2.3</b></center>", unsafe_allow_html=True)
