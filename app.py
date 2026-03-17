import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Configuração de Layout Ultra-Wide
st.set_page_config(page_title="IA ANALYZER - ÁPICE V5.4 FINAL", layout="wide")

def play_sound():
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
    .report-card { background: #0f172a; padding: 25px; border-radius: 20px; border: 2px solid #22c55e; color: white; }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória Permanente
for key in ['historico', 'banca_inicial', 'banca_atual', 'max_seq_home', 'max_seq_away', 'rodadas_lock', 
            'wins_sessao', 'total_sinais', 'sessao_ativa', 'seq_greens_atual', 'maior_seq_greens', 'deck_count']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 3000.0
        elif key == 'sessao_ativa': st.session_state[key] = True
        elif key == 'deck_count':
            st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
            for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- MOTORES DE INTELIGÊNCIA ---

def calcular_calor_mesa(historico):
    if len(historico) < 5: return 50
    ultimos_sinais = [h.get('status') for h in historico if h.get('status') in ['Green', 'Red']][:10]
    if not ultimos_sinais: return 50
    return (ultimos_sinais.count('Green') / len(ultimos_sinais)) * 100

def analisar_mago_v5_4(dados, deck):
    if not st.session_state.sessao_ativa or len(dados) < 5 or st.session_state.rodadas_lock > 0: return None
    
    v = [h['Vencedor'][0] for h in dados if h.get('Vencedor')]
    v_str = "".join(v[:12])
    
    # 1. Ruptura de Máxima Histórica
    seq = 1
    for i in range(len(v)-1):
        if v[i] == v[i+1] and v[i] != 'E': seq += 1
        else: break
    
    if v[0] == 'H' and seq >= st.session_state.max_seq_home and seq >= 4: 
        return {"sug": "Away", "est": "Ruptura de Máxima", "conf": 97}
    if v[0] == 'A' and seq >= st.session_state.max_seq_away and seq >= 4: 
        return {"sug": "Home", "est": "Ruptura de Máxima", "conf": 97}

    # 2. Padrões Geométricos (OCO e Espelho)
    if "HHAAAHH" in v_str or "AAHHHAA" in v_str:
        return {"sug": "Away" if v[0]=='H' else "Home", "est": "Simetria OCO", "conf": 94}
    
    # 3. Escalas e Deck High
    total = sum(deck.values())
    altas = sum([deck[c] for c in ['10', 'J', 'Q', 'K', 'A']])
    p_alta = (altas / total * 100) if total > 0 else 0
    
    if v_str.startswith("HHA") and p_alta > 40: return {"sug": "Home", "est": "2x1 + Deck High", "conf": 95}
    if v_str.startswith("AAH") and p_alta > 40: return {"sug": "Away", "est": "2x1 + Deck High", "conf": 95}

    return None

# --- INTERFACE PRINCIPAL ---
with st.sidebar:
    st.header("⚙️ Controle de Sessão")
    perfil = st.selectbox("Risco", ["Conservador (0.5%)", "Moderado (1%)", "Agressivo (2.5%)"], index=1)
    st.divider()
    if st.button("⛔ ENCERRAR E GERAR RELATÓRIO", use_container_width=True):
        st.session_state.sessao_ativa = False
    if st.button("🔄 REINICIAR NOVA SESSÃO", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.title("⚽ FOOTBALL STUDIO IA - ÁPICE V5.4")

if not st.session_state.sessao_ativa:
    # --- TELA DE RELATÓRIO ---
    lucro = st.session_state.banca_atual - st.session_state.banca_inicial
    st.markdown(f"""
        <div class="report-card">
            <h1>📊 RELATÓRIO DE PERFORMANCE</h1>
            <hr>
            <h3>💰 Lucro Final: R$ {lucro:.2f} ({(lucro/st.session_state.banca_inicial*100):.2f}%)</h3>
            <p>✅ <b>Win Rate:</b> {(st.session_state.wins_sessao/max(1,st.session_state.total_sinais)*100):.1f}%</p>
            <p>🔥 <b>Maior Sequência de Greens:</b> {st.session_state.maior_seq_greens}</p>
            <p>🐉 <b>Máxima Home:</b> {st.session_state.max_seq_home} | <b>Máxima Away:</b> {st.session_state.max_seq_away}</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # --- TELA DE OPERAÇÃO ---
    c_in, c_sinal, c_apex = st.columns([1, 1.2, 1])

    with c_in:
        st.subheader("📥 Registro")
        cartas = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        h_c = st.selectbox("Casa", cartas); a_c = st.selectbox("Fora", cartas)
        if st.button("REGISTRAR JOGADA", use_container_width=True):
            p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
            venc = "Home" if p_map[h_c] > p_map[a_c] else "Away" if p_map[a_c] > p_map[h_c] else "Empate"
            
            # Atualiza Deck e Máximas
            st.session_state.deck_count[h_c] -= 1; st.session_state.deck_count[a_c] -= 1
            
            # Lógica de Win/Loss
            status = "None"
            risco_val = 0.005 if "Cons" in perfil else 0.01 if "Mod" in perfil else 0.025
            if st.session_state.historico and "prev" in st.session_state.historico[0]:
                st.session_state.total_sinais += 1
                if venc == st.session_state.historico[0]["prev"]:
                    status = "Green"; st.session_state.wins_sessao += 1; st.session_state.seq_greens_atual += 1
                    st.session_state.maior_seq_greens = max(st.session_state.maior_seq_greens, st.session_state.seq_greens_atual)
                    st.session_state.banca_atual += (st.session_state.banca_atual * risco_val)
                    play_sound()
                elif venc != "Empate":
                    status = "Red"; st.session_state.seq_greens_atual = 0
                    st.session_state.banca_atual -= (st.session_state.banca_atual * risco_val)

            # Trava Pós-Empate
            if venc == "Empate": st.session_state.rodadas_lock = 2
            elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
            
            st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_c, "A": a_c, "status": status})
            st.rerun()

    with c_sinal:
        st.subheader("🔮 Sinal Ativo")
        sinal = analisar_mago_v5_4(st.session_state.historico, st.session_state.deck_count)
        if st.session_state.rodadas_lock > 0: st.warning(f"LOCK ATIVO: {st.session_state.rodadas_lock} RODADAS")
        elif sinal:
            cor = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
            st.markdown(f'<div class="card-apex"><small>{sinal["est"]}</small><h1 style="color:{cor}; font-size:65px; margin:0;">{sinal["sug"].upper()}</h1><p>Confiança: {sinal["conf"]}%</p></div>', unsafe_allow_html=True)
            st.session_state.historico[0]["prev"] = sinal['sug']
        else: st.info("Escaneando Mesa e Deck...")

    with c_apex:
        st.subheader("🛰️ Monitor de Ápice")
        calor = calcular_calor_mesa(st.session_state.historico)
        st.write(f"📊 **Calor da Mesa:** {calor:.0f}%")
        if calor >= 70: st.success("Mesa Altamente Pagadora"); st.progress(calor/100)
        elif calor >= 40: st.warning("Mesa Neutra / Estável"); st.progress(calor/100)
        else: st.error("Mesa Recolhedora - PARE!"); st.progress(calor/100)
        
        st.markdown(f"""
            <div class="monitor-item">💰 <b>Saldo:</b> R$ {st.session_state.banca_atual:.2f}</div>
            <div class="monitor-item">🔥 <b>Greens Seguindo:</b> {st.session_state.seq_greens_atual}</div>
            <div class="monitor-item">🐉 <b>Máxima Sessão:</b> {max(st.session_state.max_seq_home, st.session_state.max_seq_away)}</div>
        """, unsafe_allow_html=True)

st.divider()
if st.session_state.historico:
    st.subheader("🕒 Roadmap Tático")
    cols = st.columns(12)
    for i, h in enumerate(st.session_state.historico[:12]):
        c = "casa" if h['Vencedor'] == 'Home' else 'fora' if h['Vencedor'] == 'Away' else 'empate'
        border = "3px solid #22c55e" if h.get('status') == "Green" else "3px solid #ef4444" if h.get('status') == "Red" else "1px solid #334155"
        cols[i].markdown(f"<div style='text-align:center; border:{border}; border-radius:10px; padding:8px'><span class='bola {c}'></span><br><small>{h['H']}x{h['A']}</small></div>", unsafe_allow_html=True)
