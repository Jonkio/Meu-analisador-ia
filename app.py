import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Configuração de Layout Ultra-Wide
st.set_page_config(page_title="IA ANALYZER - COCKPIT V6.0", layout="wide")

st.markdown("""
<style>
    .main { background-color: #020617; color: #ffffff; }
    
    /* Card de Sinal com Animação de Brilho */
    .card-sinal-on { 
        background: linear-gradient(135deg, #065f46 0%, #064e3b 100%); 
        padding: 30px; border-radius: 20px; text-align: center;
        border: 4px solid #10b981; box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
        animation: glow 1.5s infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 0 10px #10b981; }
        to { box-shadow: 0 0 30px #10b981; }
    }
    
    .monitor-item { background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-bottom: 3px solid #6366f1; }
    .scanner-box { background: rgba(15, 23, 42, 0.8); padding: 15px; border-radius: 12px; border: 1px solid #334155; }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
    
    /* Títulos Estilizados */
    .h-title { font-size: 24px; font-weight: bold; background: -webkit-linear-gradient(#fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória
for key in ['historico', 'banca_inicial', 'banca_atual', 'max_seq_home', 'max_seq_away', 'rodadas_lock', 
            'wins_sessao', 'total_sinais', 'sessao_ativa', 'seq_greens_atual', 'maior_seq_greens', 'deck_count']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 3000.0
        elif key == 'sessao_ativa': st.session_state[key] = True
        elif key == 'deck_count':
            st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
            for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- LÓGICA DE CATEGORIZAÇÃO ---
def categorizar_carta(carta):
    if carta in ['2', '3', '4', '5']: return "Baixa"
    if carta in ['6', '7', '8', '9']: return "Neutra"
    if carta in ['10']: return "Alta"
    if carta in ['J', 'Q', 'K', 'A']: return "Letra"
    return "N/A"

# --- MOTOR DE ANÁLISE ---
def analisar_mago_v6(dados):
    if len(dados) < 5 or st.session_state.rodadas_lock > 0: return None
    v = [h['Vencedor'][0] for h in dados if h.get('Vencedor')]
    v_str = "".join(v[:12])
    
    # Ruptura de Máxima
    seq = 1
    for i in range(len(v)-1):
        if v[i] == v[i+1] and v[i] != 'E': seq += 1
        else: break
    
    if v[0] == 'H' and seq >= st.session_state.max_seq_home and seq >= 4: return {"sug": "Away", "est": "RUPTURA DE MÁXIMA", "conf": 97}
    if v[0] == 'A' and seq >= st.session_state.max_seq_away and seq >= 4: return {"sug": "Home", "est": "RUPTURA DE MÁXIMA", "conf": 97}
    
    # Padrão Clássico 2x1
    if v_str.startswith("HHA"): return {"sug": "Home", "est": "ESCALA 2x1", "conf": 94}
    if v_str.startswith("AAH"): return {"sug": "Away", "est": "ESCALA 2x1", "conf": 94}
    return None

# --- INTERFACE ---
if st.session_state.sessao_ativa:
    st.markdown("<h1 style='text-align: center; color: #6366f1;'>⚽ COMMAND CENTER - V6.0 PRO</h1>", unsafe_allow_html=True)
    
    c_in, c_sinal, c_apex = st.columns([1, 1.4, 1])

    with c_in:
        st.markdown("<p class='h-title'>📥 REGISTRO</p>", unsafe_allow_html=True)
        cartas = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        h_c = st.selectbox("CASA", cartas)
        a_c = st.selectbox("FORA", cartas)
        
        if st.button("CONFIRMAR JOGADA", use_container_width=True):
            p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
            venc = "Home" if p_map[h_c] > p_map[a_c] else "Away" if p_map[a_c] > p_map[h_c] else "Empate"
            
            st.session_state.deck_count[h_c] -= 1
            st.session_state.deck_count[a_c] -= 1
            
            # Validação de Lucro
            status = "None"
            if st.session_state.historico and "prev" in st.session_state.historico[0]:
                st.session_state.total_sinais += 1
                if venc == st.session_state.historico[0]["prev"]:
                    status = "Green"; st.session_state.wins_sessao += 1
                    st.session_state.seq_greens_atual += 1
                    st.session_state.maior_seq_greens = max(st.session_state.maior_seq_greens, st.session_state.seq_greens_atual)
                    st.session_state.banca_atual += (st.session_state.banca_atual * 0.01)
                elif venc != "Empate":
                    status = "Red"; st.session_state.seq_greens_atual = 0
                    st.session_state.banca_atual -= (st.session_state.banca_atual * 0.01)

            if venc == "Empate": st.session_state.rodadas_lock = 2
            elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
            
            st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_c, "A": a_c, "status": status, "cat_h": categorizar_carta(h_c), "cat_a": categorizar_carta(a_c)})
            st.rerun()

    with c_sinal:
        st.markdown("<p class='h-title'>🔮 INTELIGÊNCIA ARTIFICIAL</p>", unsafe_allow_html=True)
        sinal = analisar_mago_v6(st.session_state.historico)
        
        if st.session_state.rodadas_lock > 0:
            st.warning(f"MESA EM LOCK: {st.session_state.rodadas_lock} RODADAS")
        elif sinal:
            cor = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
            st.markdown(f"""
                <div class="card-sinal-on">
                    <h3 style="margin:0; color:#10b981;">OPORTUNIDADE DETECTADA</h3>
                    <small>{sinal['est']}</small>
                    <h1 style="color:{cor}; font-size:80px; margin:10px 0;">{sinal['sug'].upper()}</h1>
                    <p style="font-size:18px;">CONFIANÇA: <b>{sinal['conf']}%</b></p>
                </div>
            """, unsafe_allow_html=True)
            st.session_state.historico[0]["prev"] = sinal['sug']
        else:
            st.info("Varrendo Roadmap em busca de brechas...")

    with c_apex:
        st.markdown("<p class='h-title'>🛰️ GLOBAL STATUS</p>", unsafe_allow_html=True)
        lucro = st.session_state.banca_atual - st.session_state.banca_inicial
        st.markdown(f"""
            <div class="monitor-item">💰 <b>SALDO:</b> R$ {st.session_state.banca_atual:.2f}</div>
            <div class="monitor-item">📈 <b>LUCRO:</b> R$ {lucro:.2f}</div>
            <div class="monitor-item">🔥 <b>STREAK ATUAL:</b> {st.session_state.seq_greens_atual} GREENS</div>
        """, unsafe_allow_html=True)
        if st.button("⛔ ENCERRAR SESSÃO", use_container_width=True):
            st.session_state.sessao_ativa = False
            st.rerun()

    st.divider()
    
    # --- ÁREA DE TENDÊNCIA (O QUE VOCÊ CIRCULOU) ---
    if st.session_state.historico:
        st.markdown("<p class='h-title' style='text-align:center;'>🔍 SCANNER DE PREDOMINÂNCIA (Últimas 12)</p>", unsafe_allow_html=True)
        col_h, col_a = st.columns(2)
        ultimas_12 = st.session_state.historico[:12]
        
        with col_h:
            cat_h = [h['cat_h'] for h in ultimas_12]
            st.markdown("<div class='scanner-box'>", unsafe_allow_html=True)
            st.write("🔴 **CASA (HOME)**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Letras", cat_h.count("Letra"))
            c2.metric("Altas", cat_h.count("Alta"))
            c3.metric("Neutras", cat_h.count("Neutra"))
            c4.metric("Baixas", cat_h.count("Baixa"))
            st.markdown("</div>", unsafe_allow_html=True)

        with col_a:
            cat_a = [h['cat_a'] for h in ultimas_12]
            st.markdown("<div class='scanner-box'>", unsafe_allow_html=True)
            st.write("🔵 **FORA (AWAY)**")
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Letras", cat_a.count("Letra"))
            f2.metric("Altas", cat_a.count("Alta"))
            f3.metric("Neutras", cat_a.count("Neutra"))
            f4.metric("Baixas", cat_a.count("Baixa"))
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    # Roadmap tático
    if st.session_state.historico:
        cols = st.columns(12)
        for i, h in enumerate(st.session_state.historico[:12]):
            c = "casa" if h['Vencedor'] == 'Home' else 'fora' if h['Vencedor'] == 'Away' else 'empate'
            border = "3px solid #22c55e" if h.get('status') == "Green" else "3px solid #ef4444" if h.get('status') == "Red" else "1px solid #334155"
            cols[i].markdown(f"<div style='text-align:center; border:{border}; border-radius:10px; padding:8px'><span class='bola {c}'></span><br><small>{h['H']}x{h['A']}</small></div>", unsafe_allow_html=True)

else:
    # TELA DE RELATÓRIO
    st.balloons()
    lucro = st.session_state.banca_atual - st.session_state.banca_inicial
    st.markdown(f"""
        <div style="text-align:center; padding:50px; background:#0f172a; border-radius:20px; border:4px solid #10b981;">
            <h1 style="color:#10b981;">SESSÃO FINALIZADA COM SUCESSO!</h1>
            <hr>
            <h2 style="color:white;">💰 LUCRO LÍQUIDO: R$ {lucro:.2f}</h2>
            <h3 style="color:#94a3b8;">ASSERTIVIDADE: {(st.session_state.wins_sessao/max(1,st.session_state.total_sinais)*100):.1f}%</h3>
            <p style="font-size:20px;">🔥 Melhor sequência do dia: {st.session_state.maior_seq_greens} GREENS</p>
            <br>
            <button onclick="window.location.reload();" style="padding:15px 30px; border-radius:10px; border:none; background:#6366f1; color:white; font-weight:bold; cursor:pointer;">INICIAR NOVA JORNADA</button>
        </div>
    """, unsafe_allow_html=True)
