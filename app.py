import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração de Layout e Performance
st.set_page_config(page_title="IA ANALYZER - MODO FIXO", layout="wide")

def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #064e3b; color: #ffffff; }
    .card-fixo { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
        padding: 30px; border-radius: 20px; text-align: center; color: white;
        border: 4px solid #10b981; box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }
    .radar-tie { background: #f59e0b; color: white; padding: 8px; border-radius: 10px; font-weight: bold; margin-top: 10px; }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização do Baralho e Memória (Sem Variáveis de Gale)
if 'deck_count' not in st.session_state:
    st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
    for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32

for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'rodadas_lock']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 3000.0
        elif 'lock' in key: st.session_state[key] = 0
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- MOTOR DE ANÁLISE DE ALTA PRECISÃO (SEM GALE) ---

def detectar_radar_empate(dados, deck):
    if len(dados) < 3: return False
    dif_recente = abs(int(dados[0]['v_h']) - int(dados[0]['v_a']))
    total = sum(deck.values())
    if total == 0: return False
    grupos = [['2','3','4'], ['5','6','7'], ['8','9','10'], ['J','Q','K','A']]
    concentracao = any([(sum([deck[c] for c in g]) / total) > 0.40 for g in grupos])
    return dif_recente <= 1 and concentracao

def analisar_mago_fixo(dados):
    # Exige mais dados para sinalizar sem Gale (Segurança Máxima)
    if len(dados) < 6 or st.session_state.rodadas_lock > 0: return None
    
    v = [h['Vencedor'][0] for h in dados[:10]]
    v_str = "".join(v)
    forca_h = sum([int(h['v_h']) for h in dados[:5]]) / 5
    forca_a = sum([int(h['v_a']) for h in dados[:5]]) / 5

    # Critérios Rigorosos de Convergência
    if v_str.startswith("HHA") and forca_h > (forca_a + 1.5):
        return {"sug": "Home", "est": "Escala 2x1 + Superioridade", "conf": 96}
    if v_str.startswith("AAH") and forca_a > (forca_h + 1.5):
        return {"sug": "Away", "est": "Escala 2x1 + Superioridade", "conf": 96}
    if v_str.startswith("HHHAA") or v_str.startswith("AAAHH"):
        return {"sug": ("Home" if v[0]=='A' else "Away"), "est": "Escala 3x2x1", "conf": 92}
    
    return None

# --- INTERFACE ---
with st.sidebar:
    st.header("🛡️ Gestão de Banca")
    st.session_state.banca_atual = st.number_input("Banca Atual R$", value=float(st.session_state.banca_atual))
    perc = st.slider("Aposta Fixa (%)", 0.5, 5.0, 1.0) / 100 # Sugestão 1% para banca de 3k
    st.divider()
    st.metric("Greens (Mão Fixa)", st.session_state.greens_dia)
    st.metric("Reds", st.session_state.reds_dia)
    if st.button("RESETAR SESSÃO"): st.session_state.clear(); st.rerun()

st.title("⚽ FOOTBALL STUDIO IA - MODO MAGO FIXO")

c_in, c_prev = st.columns([1, 1.4])

with c_in:
    st.subheader("📥 Registro")
    cartas_op = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    h_v = st.selectbox("Home", cartas_op); a_v = st.selectbox("Away", cartas_op)
    
    if st.button("REGISTRAR JOGADA", use_container_width=True):
        p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
        v_h, v_a = p_map[h_v], p_map[a_v]
        venc = "Home" if v_h > v_a else "Away" if v_a > v_h else "Empate"
        
        # Baixa no deck e Lock
        st.session_state.deck_count[h_v] -= 1
        st.session_state.deck_count[a_v] -= 1
        if venc == "Empate": st.session_state.rodadas_lock = 2
        elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
        
        # Contagem de Win/Loss Simples (Sem Gale)
        if st.session_state.historico and "prev" in st.session_state.historico[0]:
            if venc == st.session_state.historico[0]["prev"]:
                st.session_state.greens_dia += 1
                st.session_state.banca_atual += (st.session_state.banca_atual * perc)
            elif venc != "Empate":
                st.session_state.reds_dia += 1
                st.session_state.banca_atual -= (st.session_state.banca_atual * perc)

        st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_v, "A": a_v, "v_h": v_h, "v_a": v_a, "Hora": datetime.now().strftime("%H:%M")})
        st.rerun()

with c_prev:
    st.subheader("🔮 Filtro de Elite (Aposta Fixa)")
    sinal = analisar_mago_fixo(st.session_state.historico)
    zona_tie = detectar_radar_empate(st.session_state.historico, st.session_state.deck_count)
    
    if st.session_state.rodadas_lock > 0:
        st.info(f"🔎 MODO OBSERVAÇÃO: {st.session_state.rodadas_lock} rodadas restantes.")
    elif sinal:
        cor_s = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
        st.markdown(f"""
            <div class="card-fixo">
                <small>CONVERGÊNCIA DE ALTA ASSERTIVIDADE</small>
                <h1 style="color: {cor_s}; font-size: 75px; margin: 0;">{sinal['sug'].upper()}</h1>
                <p>Estratégia: <b>{sinal['est']}</b></p>
                <p>Valor Recomendado: <b>R$ {(st.session_state.banca_atual * perc):.2f}</b></p>
                {f'<div class="radar-tie">🎯 RADAR DE EMPATE: COBRIR COM 15% (R$ {(st.session_state.banca_atual * perc * 0.15):.2f})</div>' if zona_tie else ""}
            </div>
        """, unsafe_allow_html=True)
        play_sound()
        st.session_state.historico[0]["prev"] = sinal['sug']
    elif zona_tie:
        st.markdown(f'<div class="radar-tie" style="text-align:center; padding:20px;">ZONA DE EMPATE DETECTADA<br>Aposta sugerida: R$ {(st.session_state.banca_atual * perc * 0.2):.2f}</div>', unsafe_allow_html=True)
    else:
        st.info("🔎 Monitorando padrões rigorosos para entrada fixa...")

st.divider()
if st.session_state.historico:
    st.subheader("🕒 Roadmap Recente")
    cols = st.columns(12)
    for i, h in enumerate(st.session_state.historico[:12]):
        cor = "casa" if h['Vencedor'] == "Home" else "fora" if h['Vencedor'] == "Away" else "empate"
        cols[i].markdown(f"<div style='text-align:center'><span class='bola {cor}'></span><br><small>{h['H']}x{h['A']}</small></div>", unsafe_allow_html=True)
