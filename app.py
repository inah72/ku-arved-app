import pandas as pd
import streamlit as st

st.set_page_config(page_title="KÜ Arvete Jaotaja", layout="wide")

st.title("🏢 Korteriühistu Arvete Jaotaja (18 korterit)")
st.write(
    "Sisesta üldarved ja korterite näidud ning arvuta iga korteri makseosa."
)

default_korterid = [
    {"nr": i, "pindala_m2": 50.0, "kulm_vesi_m3": 3.0, "soe_vesi_m3": 1.5}
    for i in range(1, 19)
]

col1, col2 = st.columns([1, 2])

with col1:
  st.subheader("1. Üldarved (EUR)")
  kute_eur = st.number_input("Küte (€)", value=850.00, step=10.0)
  remondifond_eur = st.number_input("Remondifond (€)", value=300.00, step=10.0)
  haldus_eur = st.number_input("Haldustasu (€)", value=150.00, step=5.0)
  prygi_eur = st.number_input("Prügivedu (€)", value=120.00, step=5.0)
  uldelekter_eur = st.number_input("Üldelekter (€)", value=45.00, step=5.0)

  st.subheader("2. Vee hinnad")
  kulm_vesi_m3_hind = st.number_input("Külm vesi (€/m³)", value=2.50, step=0.1)
  soe_vesi_soojendus_eur = st.number_input(
      "Sooja vee soojendamine kokku (€)", value=180.00, step=10.0
  )

with col2:
  st.subheader("3. Korterite pindalad ja näidud")
  df_input = pd.DataFrame(default_korterid)

  edited_df = st.data_editor(
      df_input,
      num_rows="fixed",
      column_config={
          "nr": st.column_config.NumberColumn("Krt nr", disabled=True),
          "pindala_m2": st.column_config.NumberColumn(
              "Pindala (m²)", format="%.1f m²"
          ),
          "kulm_vesi_m3": st.column_config.NumberColumn(
              "Külm vesi (m³)", format="%.1f m³"
          ),
          "soe_vesi_m3": st.column_config.NumberColumn(
              "Soe vesi (m³)", format="%.1f m³"
          ),
      },
      hide_index=True,
      use_container_width=True,
  )

st.divider()

if st.button("🚀 Arvuta korterite arved", type="primary"):
  korterid = edited_df.to_dict("records")

  kokku_pindala = sum(k["pindala_m2"] for k in korterid)
  korterite_arv = len(korterid)
  kokku_soe_vesi = sum(k["soe_vesi_m3"] for k in korterid)

  kute_m2 = kute_eur / kokku_pindala if kokku_pindala > 0 else 0
  remondifond_m2 = remondifond_eur / kokku_pindala if kokku_pindala > 0 else 0
  haldus_m2 = haldus_eur / kokku_pindala if kokku_pindala > 0 else 0

  prygi_krt = prygi_eur / korterite_arv if korterite_arv > 0 else 0
  uldelekter_krt = uldelekter_eur / korterite_arv if korterite_arv > 0 else 0

  soe_soojendus_m3_hind = (
      soe_vesi_soojendus_eur / kokku_soe_vesi if kokku_soe_vesi > 0 else 0
  )

  tulemused = []
  for k in korterid:
    kute = k["pindala_m2"] * kute_m2
    remondi = k["pindala_m2"] * remondifond_m2
    haldus = k["pindala_m2"] * haldus_m2

    prygi = prygi_krt
    uldelekter = uldelekter_krt

    kulm_vesi_eur = k["kulm_vesi_m3"] * kulm_vesi_m3_hind
    soe_vesi_vesi_eur = k["soe_vesi_m3"] * kulm_vesi_m3_hind
    soe_vesi_soojendus_eur_krt = k["soe_vesi_m3"] * soe_soojendus_m3_hind
    soe_vesi_kokku_eur = soe_vesi_vesi_eur + soe_vesi_soojendus_eur_krt

    summa = (
        kute
        + remondi
        + haldus
        + prygi
        + uldelekter
        + kulm_vesi_eur
        + soe_vesi_kokku_eur
    )

    tulemused.append({
        "Krt nr": int(k["nr"]),
        "Pindala (m²)": round(k["pindala_m2"], 1),
        "Küte (€)": round(kute, 2),
        "Remondifond (€)": round(remondi, 2),
        "Haldus (€)": round(haldus, 2),
        "Prügi (€)": round(prygi, 2),
        "Üldelekter (€)": round(uldelekter, 2),
        "Külm vesi (€)": round(kulm_vesi_eur, 2),
        "Soe vesi (€)": round(soe_vesi_kokku_eur, 2),
        "KOKKU (€)": round(summa, 2),
    })

  res_df = pd.DataFrame(tulemused)

  st.subheader("📊 Arvutuse tulemused")
  st.dataframe(res_df, use_container_width=True, hide_index=True)

  # CSV allalaadimine
  csv = res_df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Lae tulemused alla CSV failina",
      data=csv,
      file_name="ku_arved_tulemus.csv",
      mime="text/csv",
  )