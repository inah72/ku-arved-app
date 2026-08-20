import streamlit as st
import pandas as pd

st.set_page_config(page_title="KÜ Arvete Kalkulaator", layout="wide")

st.title("🏢 Korteriühistu arvete ja veenäitude kalkulaator")

# ---------------------------------------------------------
# 1. SISEND: Üldarved ja üldmõõdiku andmed
# ---------------------------------------------------------
st.header("1. Üldarved ja ühistu üldnäidud")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("💧 Külm vesi (Üldarve)")
    yld_kv_m3 = st.number_input("Üldmõõdiku tarbimine kokku (m³)", min_value=0.0, value=100.0, step=1.0)
    yld_kv_euro = st.number_input("Külma vee üldarve summa (€)", min_value=0.0, value=250.0, step=0.01)

with col2:
    st.subheader("🔥 Sooja vee soojendamine")
    yld_sv_soojendamis_euro = st.number_input("Soojendamise arve summa (€)", min_value=0.0, value=150.0, step=0.01)

with col3:
    st.subheader("🏠 Üldkulud (pindala järgi)")
    yldkulu_euro = st.number_input("Muud üldkulud kokku (€)", min_value=0.0, value=300.0, step=0.01)

# ---------------------------------------------------------
# 2. SISEND: Korterite veenäidud ja pindalad (18 korterit)
# ---------------------------------------------------------
st.header("2. Korterite igakuised veenäidud ja andmed")

if "korterid_df" not in st.session_state:
    # Vaikimisi algandmed 18 korteri jaoks
    data = {
        "Korter": [f"Krt {i}" for i in range(1, 19)],
        "Pindala (m²)": [50.0] * 18,
        "KV eelmine näit": [100.0] * 18,
        "KV uus näit": [105.0] * 18,
        "SV eelmine näit": [50.0] * 18,
        "SV uus näit": [53.0] * 18,
    }
    st.session_state.korterid_df = pd.DataFrame(data)

st.write("Märgi tabelisse iga korteri eelmine ja uus näit ning pindala:")
edited_df = st.data_editor(st.session_state.korterid_df, num_rows="fixed", use_container_width=True)

# ---------------------------------------------------------
# 3. ARVUTUSED
# ---------------------------------------------------------

# Tarbimiste arvutamine (Uus näit - Eelmine näit)
edited_df["KV tarbimine (m³)"] = (edited_df["KV uus näit"] - edited_df["KV eelmine näit"]).clip(lower=0)
edited_df["SV tarbimine (m³)"] = (edited_df["SV uus näit"] - edited_df["SV eelmine näit"]).clip(lower=0)
edited_df["Vesi kokku (m³)"] = edited_df["KV tarbimine (m³)"] + edited_df["SV tarbimine (m³)"]

# Summaarsed näitajad
kokku_korterite_kv = edited_df["KV tarbimine (m³)"].sum()
kokku_korterite_sv = edited_df["SV tarbimine (m³)"].sum()
kokku_korterite_vesi = edited_df["Vesi kokku (m³)"].sum()
kokku_pindala = edited_df["Pindala (m²)"].sum()

# Veekadu (Üldmõõdik vs korterite summeeritud tarbimine)
veekadu_m3 = max(0.0, yld_kv_m3 - kokku_korterite_vesi)

# Ühikuhinnad
kv_yhikuhind = yld_kv_euro / yld_kv_m3 if yld_kv_m3 > 0 else 0.0
sv_soojenduse_yhikuhind = yld_sv_soojendamis_euro / kokku_korterite_sv if kokku_korterite_sv > 0 else 0.0
yldkulu_ruutmeetri_hind = yldkulu_euro / kokku_pindala if kokku_pindala > 0 else 0.0

# Veekao maksumus ja jagamine korterite vahel (proportsionaalselt tarbimisele)
veekao_kokku_euro = veekadu_m3 * kv_yhikuhind

# Korteripõhised summad (€)
edited_df["Külm vesi (€)"] = edited_df["KV tarbimine (m³)"] * kv_yhikuhind
edited_df["Soe vesi (€)"] = edited_df["SV tarbimine (m³)"] * (kv_yhikuhind + sv_soojenduse_yhikuhind)

# Veekao jagamine tarbitud m³ alusel
if kokku_korterite_vesi > 0:
    edited_df["Veekadu (€)"] = (edited_df["Vesi kokku (m³)"] / kokku_korterite_vesi) * veekao_kokku_euro
else:
    edited_df["Veekadu (€)"] = 0.0

# Üldkulud pindala järgi
edited_df["Üldkulud (€)"] = edited_df["Pindala (m²)"] * yldkulu_ruutmeetri_hind

# Lõppsumma korteri kohta
edited_df["KOKKU ARVE (€)"] = (
    edited_df["Külm vesi (€)"] 
    + edited_df["Soe vesi (€)"] 
    + edited_df["Veekadu (€)"] 
    + edited_df["Üldkulud (€)"]
)

# ---------------------------------------------------------
# 4. TULEMUSTE KUVMINE
# ---------------------------------------------------------
st.header("3. Koondandmed ja tariifid")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Külma vee hind", f"{kv_yhikuhind:.3f} €/m³")
m2.metric("Soojendamise hind", f"{sv_soojenduse_yhikuhind:.3f} €/m³")
m3.metric("Tuvastatud veekadu", f"{veekadu_m3:.2f} m³", f"{veekao_kokku_euro:.2f} €")
m4.metric("Üldkulu ruutmeetrile", f"{yldkulu_ruutmeetri_hind:.3f} €/m²")

st.header("4. Korterite lõplikud arved")

# Tulemuste tabeli valikuline kuvamine
tulemused_df = edited_df[[
    "Korter", "Pindala (m²)", 
    "KV tarbimine (m³)", "SV tarbimine (m³)", 
    "Külm vesi (€)", "Soe vesi (€)", "Veekadu (€)", "Üldkulud (€)", 
    "KOKKU ARVE (€)"
]]

st.dataframe(
    tulemused_df.style.format({
        "Pindala (m²)": "{:.1f}",
        "KV tarbimine (m³)": "{:.2f}",
        "SV tarbimine (m³)": "{:.2f}",
        "Külm vesi (€)": "{:.2f}",
        "Soe vesi (€)": "{:.2f}",
        "Veekadu (€)": "{:.2f}",
        "Üldkulud (€)": "{:.2f}",
        "KOKKU ARVE (€)": "{:.2f}",
    }),
    use_container_width=True
)

# CSV allalaadimise nupp
csv = tulemused_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Laadi arvutuste tulemused alla (CSV)",
    data=csv,
    file_name="ku_arved_tulemused.csv",
    mime="text/csv",
)