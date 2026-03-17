import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Configuração de Layout Ultra-Wide
st.set_page_config(page_title="IA ANALYZER - ÁPICE ABSOLUTO", layout="wide")

def play_sound():
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/button-3.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #020617; color: #ffffff; }
    .card-apex { 
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); 
        padding: 25px; border-radius: 20px; text-align: center; color: white;
        border: 2px solid #6366f1; box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    }
    .monitor-item { background: rgba(30, 41, 59, 0.7); padding: 12px; border-radius: 8px; border-left: 4px solid #6366f1; margin-bottom: 8px; }
    .bola { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória Avançada
if 'deck_count' not in st.session_state:
    st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
    for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32

for key in ['historico', 'banca_atual', 'max_seq_home', 'max_seq_away', 'rodadas_lock', 'wins_sessao', 'total_sinais']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 3000.0
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- MOTORES DE INTELIGÊNCIA V5 ---

def calcular_indice_volatilidade(dados):
    if len(dados) < 10: return 50 
    acertos = sum([1 for h in dados[:10] if h.get('status') == 'Green'])
    return (acertos / 10) * 100

def analisar_mago_v5(dados, deck):
    volatilidade = calcular_indice_volatilidade(dados)
    if volatilidade < 40: return None # Filtro Anti-Recolhimento
    
    if len(dados) < 6 or st.session_state.rodadas_lock > 0: return None
    
    v = [h['Vencedor'][0] for h in dados[:12] if h.get('Vencedor')]
    v_str = "".join(v)
    p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
    
    # Ruptura de Máxima Histórica
    seq = 1
    for i in range(len(v)-1):
        if v[i] == v[i+1] and v[i] != 'E': seq += 1
        else: break
    if v[0] == 'H' and seq >= st.session_state.max_seq_home and seq >= 4: 
        return {"sug": "Away", "est": "Ruptura de Máxima", "conf": 97}
    if v[0] == 'A' and seq >= st.session_state.max_seq_away and seq >= 4: 
        return {"sug": "Home", "est": "Ruptura de Máxima", "conf": 97}

    # Escala + Filtro Físico (Deck High)
    total_cartas = sum(deck.values())
    altas_restantes = sum([deck[c] for c in ['10', 'J', 'Q', 'K', 'A']])
    prob_alta = (altas_restantes / total_cartas) * 100 if total_cartas > 0 else 0
    
    if v_str.startswith("HHA") and prob_alta > 40: return {"sug": "Home", "est": "Escala + Deck High", "conf": 95}
    if v_str.startswith("AAH") and prob_alta > 40: return {"sug": "Away", "est": "Escala + Deck High", "conf": 95}

    return None

# --- INTERFACE DE COMANDO ---
st.title("⚽ FOOTBALL STUDIO IA - ÁPICE V5")

c_input, c_sinal, c_apex = st.columns([1, 1.2, 1])

with c_input:
    st.subheader("📥 Terminal de Dados")
    cartas = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    h_c = st.selectbox("Casa", cartas); a_c = st.selectbox("Fora", cartas)
    if st.button("REGISTRAR JOGADA", use_container_width=True):
        p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
        v_h, v_a = p_map[h_c], p_map[a_c]
        venc = "Home" if v_h > v_a else "Away" if v_a > v_h else "Empate"
        
        st.session_state.deck_count[h_c] -= 1
        st.session_state.deck_count[a_c] -= 1
        
        # Gestão de Máximas
        if venc == 'Home': 
            curr_h = 1
            for h in st.session_state.historico:
                if h['Vencedor'] == 'Home': curr_h += 1
                else: break
            if curr_h > st.session_state.max_seq_home: st.session_state.max_seq_home = curr_h
        elif venc == 'Away':
            curr_a = 1
            for h in st.session_state.historico:
                if h['Vencedor'] == 'Away': curr_a += 1
                else: break
            if curr_a > st.session_state.max_seq_away: st.session_state.max_seq_away = curr_a

        status = "None"
        if st.session_state.historico and "prev" in st.session_state.historico[0]:
            st.session_state.total_sinais += 1
            if venc == st.session_state.historico[0]["prev"]:
                status = "Green"; st.session_state.wins_sessao += 1
                st.session_state.banca_atual += (st.session_state.banca_atual * 0.01)
            elif venc != "Empate":
                status = "Red"; st.session_state.banca_atual -= (st.session_state.banca_atual * 0.01)

        if venc == "Empate": st.session_state.rodadas_lock = 2
        elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
        
        st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_c, "A": a_c, "status": status})
        st.rerun()

with c_sinal:
    st.subheader("🔮 Processamento Elite")
    sinal = analisar_mago_v5(st.session_state.historico, st.session_state.deck_count)
    if st.session_state.rodadas_lock > 0: st.warning("⚠️ MESA EM LOCK (PÓS-EMPATE)")
    elif sinal:
        cor = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
        st.markdown(f'<div class="card-apex"><small>{sinal["est"]}</small><h1 style="color:{cor}; font-size:65px; margin:0;">{sinal["sug"].upper()}</h1><p>Confiança: {sinal["conf"]}%</p></div>', unsafe_allow_html=True)
        play_sound(); st.session_state.historico[0]["prev"] = sinal['sug']
    else: st.info("Aguardando Convergência de Alta Probabilidade...")

with c_apex:
    st.subheader("🛰️ Monitor de Ápice")
    vol = calcular_indice_volatilidade(st.session_state.historico)
    st.write(f"📊 **Calor da Mesa (Respeito a Padrões):** {vol}%")
    st.progress(vol/100)
    
    rate = (st.session_state.wins_sessao / st.session_state.total_sinais * 100) if st.session_state.total_sinais > 0 else 0
    st.markdown(f"""
        <div class="monitor-item">🏷️ <b>Assertividade Real:</b> {rate:.1f}%</div>
        <div class="monitor-item">🐉 <b>Máxima Home:</b> {st.session_state.max_seq_home}</div>
        <div class="monitor-item">🐉 <b>Máxima Away:</b> {st.session_state.max_seq_away}</div>
        <div class="monitor-item">💰 <b>Saldo Atual:</b> R$ {st.session_state.banca_atual:.2f}</div>
    """, unsafe_allow_html=True)

st.divider()
if st.session_state.historico:
    cols = st.columns(12)
    for i, h in enumerate(st.session_state.historico[:12]):
        c = "casa" if h['Vencedor'] == 'Home' else 'fora' if h['Vencedor'] == 'Away' else 'empate'
        cols[i].markdown(f"<div style='text-align:center'><span class='bola {c}'></span><br><small>{h['H']}x{h['A']}</small></div>", unsafe_allow_html=True)
