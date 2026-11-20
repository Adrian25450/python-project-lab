"""Streamlit weather dashboard using Open-Meteo public endpoints."""
from datetime import datetime
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Clima · Weather Lab",page_icon="🌦️",layout="wide")
st.markdown("""<style>.stApp{background:linear-gradient(150deg,#071526,#102842 60%,#123d4b);color:#eef7ff}.block-container{max-width:1120px;padding-top:2rem}.metric-card{padding:22px;border:1px solid #35526a;border-radius:16px;background:#142d4388}</style>""",unsafe_allow_html=True)
st.caption("PYTHON PROJECT LAB · OPEN-METEO")
st.title("Pronóstico del clima")
st.write("Consulta condiciones actuales y próximos días para una ciudad.")
city=st.text_input("Ciudad",value="Cartago, Colombia",placeholder="Ej.: Cali, Colombia")

@st.cache_data(ttl=900,show_spinner=False)
def get_weather(query):
    geo=requests.get("https://geocoding-api.open-meteo.com/v1/search",params={"name":query,"count":1,"language":"es","format":"json"},timeout=12)
    geo.raise_for_status(); results=geo.json().get("results",[])
    if not results: raise ValueError("No encontré esa ciudad; prueba con ciudad y país.")
    place=results[0]
    forecast=requests.get("https://api.open-meteo.com/v1/forecast",params={"latitude":place["latitude"],"longitude":place["longitude"],"current":"temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code","daily":"temperature_2m_max,temperature_2m_min,precipitation_probability_max","timezone":"auto","forecast_days":7},timeout=12)
    forecast.raise_for_status(); return place,forecast.json()

if st.button("Consultar clima",type="primary"):
    if not city.strip(): st.warning("Escribe una ciudad para continuar.")
    else:
        try:
            with st.spinner("Consultando pronóstico…"): place,data=get_weather(city.strip())
            current=data["current"]; st.subheader(f"{place['name']}, {place.get('admin1','')} · {place.get('country','')}")
            a,b,c,d=st.columns(4)
            a.metric("Temperatura",f"{current['temperature_2m']} °C")
            b.metric("Sensación",f"{current['apparent_temperature']} °C")
            c.metric("Humedad",f"{current['relative_humidity_2m']} %")
            d.metric("Viento",f"{current['wind_speed_10m']} km/h")
            daily=data["daily"]
            frame=pd.DataFrame({"Fecha":pd.to_datetime(daily["time"]),"Máxima (°C)":daily["temperature_2m_max"],"Mínima (°C)":daily["temperature_2m_min"],"Prob. lluvia (%)":daily["precipitation_probability_max"]})
            left,right=st.columns([1.6,1]);
            with left:
                st.markdown("### Temperatura por día")
                chart=px.line(frame,x="Fecha",y=["Máxima (°C)","Mínima (°C)"],markers=True,color_discrete_sequence=["#65dfd1","#7fb1ff"])
                chart.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#e7f2ff",legend_title_text="",margin=dict(l=10,r=10,t=15,b=10))
                st.plotly_chart(chart,use_container_width=True)
            with right:
                st.markdown("### Probabilidad de lluvia")
                bar=px.bar(frame,x="Fecha",y="Prob. lluvia (%)",color_discrete_sequence=["#51a7db"])
                bar.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#e7f2ff",margin=dict(l=10,r=10,t=15,b=10))
                st.plotly_chart(bar,use_container_width=True)
            st.caption(f"Actualizado: {datetime.fromisoformat(current['time']).strftime('%d/%m/%Y %H:%M')} · Fuente: Open-Meteo")
        except (requests.RequestException,KeyError,ValueError) as error: st.error(f"No se pudo consultar el clima: {error}")
else: st.info("Pulsa **Consultar clima** para cargar condiciones y gráficos.")

