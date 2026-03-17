import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Configuração de Layout Ultra-Wide
st.set_page_config(page_title="IA ANALYZER - ÁPICE V5.2", layout="wide")

def play_sound():
    # Som discreto de confirmação
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/button-3.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #020617; color: #ffffff; }
    .card-apex { 
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); 
        padding: 25px; border-radius: 20px; text-align: center; color: white;
        border: 2px solid #6366f1; box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(99, 102, 241, 0); }
        100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
    }
    .monitor-item { background: rgba(30, 41, 59, 0.7); padding: 12px; border-radius: 8px; border-left: 4px solid #6366f1; margin-bottom: 8px; }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória e Máximas Automáticas
if 'deck_count' not in st.session_state:
    st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
    for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32

for key in ['historico', 'banca_atual', 'max_seq_home', 'max_seq_away', 'rodadas_lock', 'wins_sessao', 'total_sinais', 'perfil_risco']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 3000.0
        elif key == 'perfil_risco': st.session_state[key] = "Moderado (1%)"
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- MOTORES DE INTELIGÊNCIA ---

def analisar_mago_v5(dados, deck):
    if len(dados) < 5 or st.session_state.rodadas_lock > 0: return None
    
    v = [h['Vencedor'][0] for h in dados if h.get('Vencedor')]
    v_str = "".join(v[:12])
    
    # 1. Ruptura de Máxima Dinâmica
    seq = 1
    for i in range(len(v)-1):
        if v[i] == v[i+1] and v[i] != 'E': seq += 1
        else: break
    
    # Atualiza Máximas da Sessão
    if v[0] == 'H' and seq > st.session_state.max_seq_home: st.session_state.max_seq_home = seq
    if v[0] == 'A' and seq > st.session_state.max_seq_away: st.session_state.max_seq_away = seq
        
    if v_str.startswith('H') and seq >= st.session_state.max_seq_home and seq >= 4: 
        return {"sug": "Away", "est": "Ruptura de Máxima", "conf": 97}
    if v_str.startswith('A') and seq >= st.session_state.max_seq_away and seq >= 4: 
        return {"sug": "Home", "est": "Ruptura de Máxima", "conf": 97}

    # 2. Padrão Xadrez (Alternância)
    if len(v) >= 4 and v[0] != v[1] and v[1] != v[2] and v[2] != v[3]:
        sug_x = "Home" if v[0] == "A" else "Away"
        return {"sug": sug_x, "est": "Quebra de Xadrez", "conf": 89}

    # 3. Probabilidade Física do Baralho
    total = sum(deck.values())
    altas = sum([deck[c] for c in ['10', 'J', 'Q', 'K', 'A']])
    prob_alta = (altas / total * 100) if total > 0 else 0
    
    if v_str.startswith("HHA") and prob_alta > 42: return {"sug": "Home", "est": "Escala + Deck High", "conf": 94}
    if v_str.startswith("AAH") and prob_alta > 42: return {"sug": "Away", "est": "Escala + Deck High", "conf": 94}

    return None

# --- INTERFACE ---
st.title("⚽ FOOTBALL STUDIO IA - ÁPICE V5.2")

with st.sidebar:
    st.header("⚙️ Configurações")
    st.session_state.perfil_risco = st.selectbox("Perfil de Risco", ["Conservador (0.5%)", "Moderado (1%)", "Agressivo (2.5%)"], index=1)
    
    total_c = sum(st.session_state.deck_count.values())
    p_altas = (sum([st.session_state.deck_count[c] for c in ['10','J','Q','K','A']]) / total_c * 100) if total_c > 0 else 0
    p_medias = (sum([st.session_state.deck_count[c] for c in ['6','7','8','9']]) / total_c * 100) if total_c > 0 else 0
    p_baixas = (sum([st.session_state.deck_count[c] for c in ['2','3','4','5']]) / total_c * 100) if total_c > 0 else 0

    st.subheader("🃏 Deck Scan")
    st.write(f"Altas (10-A): **{p_altas:.1f}%**")
    st.progress(p_altas/100)
    st.write(f"Médias (6-9): **{p_medias:.1f}%**")
    st.progress(p_medias/100)
    st.write(f"Baixas (2-5): **{p_baixas:.1f}%**")
    st.progress(p_baixas/100)

    if st.button("🔄 Shuffle (Reset Deck)"):
        st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
        for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32
        st.rerun()

c_input, c_sinal, c_apex = st.columns([1, 1.2, 1])

with c_input:
    st.subheader("📥 Entrada")
    cartas = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    col1, col2 = st.columns(2)
    h_c = col1.selectbox("Casa", cartas, key="h_input")
    a_c = col2.selectbox("Fora", cartas, key="a_input")
    
    if st.button("REGISTRAR JOGADA", use_container_width=True):
        p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
        v_h, v_a = p_map[h_c], p_map[a_c]
        venc = "Home" if v_h > v_a else "Away" if v_a > v_h else "Empate"
        
        st.session_state.deck_count[h_c] -= 1
        st.session_state.deck_count[a_c] -= 1
        
        status = "None"
        risco_val = 0.005 if "Conservador" in st.session_state.perfil_risco else 0.01 if "Moderado" in st.session_state.perfil_risco else 0.025
        
        if st.session_state.historico and "prev" in st.session_state.historico[0]:
            st.session_state.total_sinais += 1
            if venc == st.session_state.historico[0]["prev"]:
                status = "Green"; st.session_state.wins_sessao += 1
                st.session_state.banca_atual += (st.session_state.banca_atual * risco_val)
                play_sound()
            elif venc != "Empate":
                status = "Red"; st.session_state.banca_atual -= (st.session_state.banca_atual * risco_val)

        if venc == "Empate": st.session_state.rodadas_lock = 2
        elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
        
        st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_c, "A": a_c, "status": status})
        st.rerun()

with c_sinal:
    st.subheader("🔮 Sinal de Elite")
    sinal = analisar_mago_v5(st.session_state.historico, st.session_state.deck_count)
    if st.session_state.rodadas_lock > 0:
        st.warning(f"Mesa em Observação (Lock: {st.session_state.rodadas_lock})")
    elif sinal:
        cor = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
        st.markdown(f"""
            <div class="card-apex">
                <small>{sinal['est'].upper()}</small>
                <h1 style="color:{cor}; font-size:65px; margin:0;">{sinal['sug'].upper()}</h1>
                <p style="font-size:20px;">Confiança: <b>{sinal['conf']}%</b></p>
                <small>Aposta Sugerida: R$ {(st.session_state.banca_atual * (0.01 if "Moderado" in st.session_state.perfil_risco else 0.005 if "Conservador" in st.session_state.perfil_risco else 0.025)):.2f}</small>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.historico[0]["prev"] = sinal['sug']
    else:
        st.info("Escaneando padrões HFT...")

with c_apex:
    st.subheader("🛰️ Global Status")
    rate = (st.session_state.wins_sessao / st.session_state.total_sinais * 100) if st.session_state.total_sinais > 0 else 0
    st.markdown(f"""
        <div class="monitor-item">🏷️ <b>Assertividade:</b> {rate:.1f}%</div>
        <div class="monitor-item">💰 <b>Saldo Atual:</b> R$ {st.session_state.banca_atual:.2f}</div>
        <div class="monitor-item">🐉 <b>Máxima Sessão:</b> H:{st.session_state.max_seq_home} | A:{st.session_state.max_seq_away}</div>
    """, unsafe_allow_html=True)

st.divider()
if st.session_state.historico:
    st.subheader("🕒 Roadmap Tático")
    cols = st.columns(12)
    for i, h in enumerate(st.session_state.historico[:12]):
        c = "casa" if h['Vencedor'] == 'Home' else 'fora' if h['Vencedor'] == 'Away' else 'empate'
        border = "3px solid #22c55e" if h.get('status') == "Green" else "3px solid #ef4444" if h.get('status') == "Red" else "1px solid #334155"
        cols[i].markdown(f"""
            <div style='text-align:center; border:{border}; border-radius:10px; padding:8px; background: rgba(255,255,255,0.05)'>
                <span class='bola {c}'></span><br>
                <b style='font-size:14px'>{h['H']} x {h['A']}</b>
            </div>
        """, unsafe_allow_html=True)
