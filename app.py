import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração de Layout e Performance
st.set_page_config(page_title="IA ANALYZER - FOOTBALL ESTRATÉGICO", layout="wide")

def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #064e3b; color: #ffffff; }
    .card-sinal-avancado { 
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%); 
        padding: 25px; border-radius: 15px; text-align: center; color: white;
        border: 4px solid #fbbf24; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória e Gestão
for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'aguardando_gale']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'aguardando' in key: st.session_state[key] = False
        else: st.session_state[key] = 0

# --- MOTOR DE PADRÕES E CONVERGÊNCIA ---

def analisar_estatistica_avancada(dados):
    if len(dados) < 6: return None
    
    # Extração de fluxo de cores (H=Home, A=Away)
    v = [h['Vencedor'][0] for h in dados[:10] if h.get('Vencedor')] 
    v_str = "".join(v)
    
    # Camada 1: Escalas (2x1, 3x2x1, 4x1)
    est = None
    sug = None
    conf = 0
    
    if v_str.startswith("HHA") or v_str.startswith("AAH"):
        est, sug, conf = "Escala 2x1", ("Home" if v[0]=='A' else "Away"), 87
    elif v_str.startswith("HHHAA") or v_str.startswith("AAAHH"):
        est, sug, conf = "Escala 3x2x1", ("Home" if v[0]=='A' else "Away"), 90
    elif v_str.startswith("HHHH") or v_str.startswith("AAAA"):
        est, sug, conf = "Exaustão (Quebra)", ("Away" if v[0]=='H' else "Home"), 85
    elif v[0] != v[1] and v[1] != v[2] and v[2] != v[3]:
        est, sug, conf = "Quebra de Cor Solo", v[0], 88

    # Camada 2: Convergência Numérica (Filtro 85%)
    if est:
        forca_recente = dados[0].get('Forca', 'Neutro')
        # Só confirma se o padrão de cor for suportado pela força da carta
        if (sug == "Home" and forca_recente == "Alto") or (sug == "Away" and forca_recente == "Alto") or conf > 88:
            return {"est": est, "sug": sug, "conf": conf}
            
    return None

def categorizar_carta(v):
    p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
    val = p_map.get(v, 0)
    if val <= 6: return "Baixo"
    if val >= 10: return "Alto"
    return "Neutro"

# --- INTERFACE E PROCESSAMENTO ---
with st.sidebar:
    st.header("🏟️ Tática do Mago")
    st.session_state.banca_atual = st.number_input("Banca R$", value=float(st.session_state.banca_atual))
    perc = st.slider("Entrada Base (%)", 1, 25, 10) / 100
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Gols", st.session_state.greens_dia)
    c2.metric("Faltas", st.session_state.reds_dia)
    if st.button("LIMPAR TUDO"):
        st.session_state.clear(); st.rerun()

st.title("⚽ FOOTBALL STUDIO - IA ESTRATÉGICA")

c_in, c_prev = st.columns([1, 1.4])

with c_in:
    st.subheader("📥 Registro")
    cartas = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    h_c = st.selectbox("Carta HOME", cartas); a_c = st.selectbox("Carta AWAY", cartas)
    
    if st.button("PROCESSAR JOGADA", use_container_width=True):
        p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
        venc = "Home" if p_map[h_c] > p_map[a_c] else "Away" if p_map[a_c] > p_map[h_c] else "Empate"
        
        # Lógica de Green e Gale
        if st.session_state.historico and "previsao" in st.session_state.historico[0]:
            prev = st.session_state.historico[0]["previsao"]
            if venc == prev:
                st.session_state.greens_dia += 1
                st.session_state.banca_atual += (st.session_state.banca_atual * perc) * (2 if st.session_state.aguardando_gale else 1)
                st.session_state.aguardando_gale = False
            elif venc != "Empate":
                if not st.session_state.aguardando_gale:
                    st.session_state.aguardando_gale = True
                else:
                    st.session_state.reds_dia += 1
                    st.session_state.banca_atual -= (st.session_state.banca_atual * perc) * 3
                    st.session_state.aguardando_gale = False
        
        st.session_state.historico.insert(0, {
            "Vencedor": venc, "Forca": categorizar_carta(h_c if p_map[h_c] > p_map[a_c] else a_c),
            "H": h_c, "A": a_c
        })
        st.rerun()

with c_prev:
    st.subheader("🔮 Palpite 85%+")
    sinal = analisar_estatistica_avancada(st.session_state.historico)
    
    if sinal:
        tipo_entrada = "⚠️ COBERTURA (GALE 1)" if st.session_state.aguardando_gale else "🎯 ENTRADA DIRETA"
        cor_s = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
        st.markdown(f"""
            <div class="card-sinal-avancado">
                <small>{tipo_entrada} | PADRÃO: {sinal['est']}</small>
                <h1 style="color: {cor_s}; font-size: 70px; margin: 0;">{sinal['sug'].upper()}</h1>
                <p>Confiança: {sinal['conf']}% | Aposta: R$ {(st.session_state.banca_atual * perc * (2 if st.session_state.aguardando_gale else 1)):.2f}</p>
            </div>
        """, unsafe_allow_html=True)
        play_sound()
        st.session_state.historico[0]["previsao"] = sinal['sug']
    else:
        st.info("🔎 Escaneando escalas e força das cartas...")

st.divider()
st.subheader("🕒 Roadmap de Fluxo")
if st.session_state.historico:
    hist_f = st.session_state.historico[:12]
    cols = st.columns(12)
    for i, h in enumerate(hist_f):
        c = "casa" if h['Vencedor']=="Home" else "fora" if h['Vencedor']=="Away" else "empate"
        cols[i].markdown(f"<div style='text-align:center'><span class='bola {c}'></span><br><small>{h['H']}x{h['A']}</small></div>", unsafe_allow_html=True)
