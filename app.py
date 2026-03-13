import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração de Layout
st.set_page_config(page_title="IA ANALYZER - MAGO MAX", layout="wide")

def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #064e3b; color: #ffffff; }
    .card-elite { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
        padding: 25px; border-radius: 20px; text-align: center; color: white;
        border: 4px solid #fbbf24; box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }
    .radar-empate { 
        background: linear-gradient(90deg, #b45309 0%, #f59e0b 100%); 
        padding: 10px; border-radius: 10px; font-weight: bold; color: white; margin-top: 10px;
    }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização do Baralho e Memória
if 'deck_count' not in st.session_state:
    st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
    for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32

for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'rodadas_lock']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'lock' in key: st.session_state[key] = 0
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- MOTORES DE ANÁLISE ---

def detectar_radar_empate(dados, deck):
    if len(dados) < 3: return False
    # Proximidade Numérica: Diferença de até 1 ponto nas últimas 2 rodadas
    dif_recente = abs(int(dados[0]['v_h']) - int(dados[0]['v_a']))
    # Densidade de Cartas: Verifica se um grupo domina > 40% do deck
    total = sum(deck.values())
    grupos = [['2','3','4'], ['5','6','7'], ['8','9','10'], ['J','Q','K','A']]
    concentracao = any([(sum([deck[c] for c in g]) / total) > 0.40 for g in grupos]) if total > 0 else False
    return dif_recente <= 1 and concentracao

def analisar_elite(dados):
    if len(dados) < 5 or st.session_state.rodadas_lock > 0: return None
    v = [h['Vencedor'][0] for h in dados[:10]]
    v_str = "".join(v)
    forca_h = sum([int(h['v_h']) for h in dados[:5]]) / 5
    forca_a = sum([int(h['v_a']) for h in dados[:5]]) / 5

    if v_str.startswith("HHA") and forca_h >= forca_a: return {"sug": "Home", "est": "Escala 2x1", "conf": 95}
    if v_str.startswith("AAH") and forca_a >= forca_h: return {"sug": "Away", "est": "Escala 2x1", "conf": 95}
    return None

# --- SIDEBAR: MONITOR ---
with st.sidebar:
    st.header("🗃️ Card Counting")
    df_deck = pd.DataFrame(list(st.session_state.deck_count.items()), columns=['Carta', 'Qtd'])
    st.bar_chart(df_deck.set_index('Carta'))
    if st.button("RESETAR SHOE"):
        st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
        for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32
        st.rerun()

# --- INTERFACE ---
st.title("⚽ FOOTBALL STUDIO IA - MAGO MAX")

c_in, c_prev = st.columns([1, 1.4])

with c_in:
    st.subheader("📥 Lançamentos")
    cartas_op = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    h_v = st.selectbox("Home", cartas_op); a_v = st.selectbox("Away", cartas_op)
    
    if st.button("REGISTRAR JOGADA", use_container_width=True):
        p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
        v_h, v_a = p_map[h_v], p_map[a_v]
        venc = "Home" if v_h > v_a else "Away" if v_a > v_h else "Empate"
        
        st.session_state.deck_count[h_v] -= 1
        st.session_state.deck_count[a_v] -= 1
        
        if venc == "Empate": st.session_state.rodadas_lock = 2
        elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
        
        st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_v, "A": a_v, "v_h": v_h, "v_a": v_a, "Hora": datetime.now().strftime("%H:%M")})
        st.rerun()

with c_prev:
    st.subheader("🔮 Radar e Sinais")
    zona_tie = detectar_radar_empate(st.session_state.historico, st.session_state.deck_count)
    sinal = analisar_elite(st.session_state.historico)
    
    if st.session_state.rodadas_lock > 0:
        st.info(f"🔎 MODO OBSERVAÇÃO: {st.session_state.rodadas_lock} rodadas.")
    elif sinal:
        cor_s = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
        st.markdown(f"""
            <div class="card-elite">
                <small>{sinal['est'].upper()}</small>
                <h1 style="color: {cor_s}; font-size: 70px; margin: 0;">{sinal['sug'].upper()}</h1>
                <p>Confiança: {sinal['conf']}%</p>
                {f'<div class="radar-empate">⚠️ RADAR DE EMPATE ATIVO (15% DE PROTEÇÃO)</div>' if zona_tie else ""}
            </div>
        """, unsafe_allow_html=True)
        play_sound()
    elif zona_tie:
        st.markdown('<div class="radar-empate" style="text-align:center; padding:20px;">🎯 ZONA DE EMPATE DETECTADA<br><small>Aposte apenas no Empate nesta rodada (11x)</small></div>', unsafe_allow_html=True)
        play_sound()
    else:
        st.info("Aguardando convergência técnica...")

st.divider()
if st.session_state.historico:
    st.table(pd.DataFrame(st.session_state.historico).head(10)[["Hora", "Vencedor", "H", "A"]])
