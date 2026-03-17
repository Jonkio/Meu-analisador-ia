import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Configuração de Layout
st.set_page_config(page_title="IA ANALYZER - V6.3 PRO", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f1f5f9; color: #1e293b; }
    .card-sinal-on { 
        background-color: #ffffff; 
        padding: 30px; border-radius: 15px; text-align: center;
        border: 5px solid #22c55e; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    h1, h2, h3, p, span { color: #1e293b !important; }
    .monitor-item { 
        background-color: #ffffff; padding: 10px; border-radius: 10px; 
        margin-bottom: 8px; border: 2px solid #6366f1;
        font-weight: bold; font-size: 16px;
    }
    .scanner-box { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border: 2px solid #cbd5e1;
    }
    .bola { height: 14px; width: 14px; border-radius: 50%; display: inline-block; margin: 0 3px; border: 1px solid #94a3b8; }
    .casa { background-color: #dc2626; } 
    .fora { background-color: #2563eb; } 
    .empate { background-color: #eab308; } 
    .stButton>button {
        background-color: #1e293b !important; color: white !important;
        font-weight: bold !important; border-radius: 8px !important;
    }
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

def categorizar_carta(carta):
    if carta in ['2', '3', '4', '5']: return "Baixa"
    if carta in ['6', '7', '8', '9']: return "Neutra"
    if carta in ['10']: return "Alta"
    if carta in ['J', 'Q', 'K', 'A']: return "Letra"
    return "N/A"

def analisar_mago_final(dados):
    if len(dados) < 5 or st.session_state.rodadas_lock > 0: return None
    v = [h['Vencedor'][0] for h in dados if h.get('Vencedor')]
    v_str = "".join(v[:12])
    seq = 1
    for i in range(len(v)-1):
        if v[i] == v[i+1] and v[i] != 'E': seq += 1
        else: break
    if v[0] == 'H' and seq >= st.session_state.max_seq_home and seq >= 4: return {"sug": "Away", "est": "QUEBRA DE MÁXIMA", "conf": 97}
    if v[0] == 'A' and seq >= st.session_state.max_seq_away and seq >= 4: return {"sug": "Home", "est": "QUEBRA DE MÁXIMA", "conf": 97}
    if v_str.startswith("HHA"): return {"sug": "Home", "est": "ESCALA 2x1", "conf": 94}
    if v_str.startswith("AAH"): return {"sug": "Away", "est": "ESCALA 2x1", "conf": 94}
    return None

# --- INTERFACE ---
if st.session_state.sessao_ativa:
    st.markdown("<h1 style='text-align: center;'>⚽ FOOTBALL STUDIO IA - V6.3 PRO</h1>", unsafe_allow_html=True)
    
    # ÁREA DE GESTÃO NO TOPO (COM SALDO MODIFICÁVEL)
    col_gestao1, col_gestao2, col_gestao3, col_gestao4 = st.columns([1, 1, 1, 1])
    with col_gestao1:
        st.session_state.banca_inicial = st.number_input("BANCA INICIAL (R$)", value=float(st.session_state.banca_inicial), step=50.0)
    with col_gestao2:
        # SALDO ATUAL AGORA É EDITÁVEL PELO USUÁRIO
        novo_saldo = st.number_input("SALDO ATUAL (R$)", value=float(st.session_state.banca_atual), step=10.0)
        st.session_state.banca_atual = novo_saldo
    with col_gestao3:
        perfil = st.selectbox("MODO DE JOGO", ["CALMA (0.5%)", "MODERADA (1%)", "ATACANTE (2.5%)"], index=1)
    with col_gestao4:
        st.write("") # Espaçamento
        if st.button("⛔ ENCERRAR SESSÃO", use_container_width=True):
            st.session_state.sessao_ativa = False
            st.rerun()

    st.divider()

    c_in, c_sinal, c_apex = st.columns([1, 1.4, 1])

    with c_in:
        st.subheader("📥 REGISTRO")
        cartas = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        h_c = st.selectbox("CASA", cartas)
        a_c = st.selectbox("FORA", cartas)
        
        if st.button("REGISTRAR JOGADA", use_container_width=True):
            p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
            venc = "Home" if p_map[h_c] > p_map[a_c] else "Away" if p_map[a_c] > p_map[h_c] else "Empate"
            st.session_state.deck_count[h_c] -= 1; st.session_state.deck_count[a_c] -= 1
            
            status = "None"
            risco_val = 0.005 if "CALMA" in perfil else 0.01 if "MODERADA" in perfil else 0.025
            
            if st.session_state.historico and "prev" in st.session_state.historico[0]:
                st.session_state.total_sinais += 1
                if venc == st.session_state.historico[0]["prev"]:
                    status = "Green"; st.session_state.wins_sessao += 1; st.session_state.seq_greens_atual += 1
                    st.session_state.maior_seq_greens = max(st.session_state.maior_seq_greens, st.session_state.seq_greens_atual)
                    st.session_state.banca_atual += (st.session_state.banca_atual * risco_val)
                elif venc != "Empate":
                    status = "Red"; st.session_state.seq_greens_atual = 0
                    st.session_state.banca_atual -= (st.session_state.banca_atual * risco_val)
            
            if venc == "Empate": st.session_state.rodadas_lock = 2
            elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
            
            st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_c, "A": a_c, "status": status, "cat_h": categorizar_carta(h_c), "cat_a": categorizar_carta(a_c)})
            st.rerun()

    with c_sinal:
        st.subheader("🔮 SINAL DE ENTRADA")
        sinal = analisar_mago_final(st.session_state.historico)
        if st.session_state.rodadas_lock > 0: st.warning(f"Aguarde mesa estabilizar ({st.session_state.rodadas_lock})")
        elif sinal:
            cor_txt = "#dc2626" if sinal['sug'] == "Home" else "#2563eb"
            st.markdown(f"""
                <div class="card-sinal-on">
                    <h2 style="color:#1e293b; margin:0;">ENTRADA CONFIRMADA</h2>
                    <p style="color:#64748b;">Estratégia: {sinal['est']}</p>
                    <h1 style="color:{cor_txt}; font-size:90px; margin:10px 0;">{sinal['sug'].upper()}</h1>
                    <h3 style="color:#1e293b;">CONFIANÇA: {sinal['conf']}%</h3>
                </div>
            """, unsafe_allow_html=True)
            st.session_state.historico[0]["prev"] = sinal['sug']
        else: st.info("Escaneando padrões...")

    with c_apex:
        st.subheader("🛰️ STATUS")
        lucro = st.session_state.banca_atual - st.session_state.banca_inicial
        st.markdown(f"""
            <div class="monitor-item" style="border-color:#16a34a;">💰 SALDO ATUAL: R$ {st.session_state.banca_atual:.2f}</div>
            <div class="monitor-item" style="color:#16a34a !important;">📈 LUCRO: R$ {lucro:.2f}</div>
            <div class="monitor-item">🔥 SEQUÊNCIA: {st.session_state.seq_greens_atual} ✅</div>
        """, unsafe_allow_html=True)

    st.divider()
    
    if st.session_state.historico:
        st.subheader("🔍 SCANNER DE CARTAS (Últimas 12)")
        col_h, col_a = st.columns(2)
        ultimas_12 = st.session_state.historico[:12]
        with col_h:
            cat_h = [h['cat_h'] for h in ultimas_12]
            st.markdown("<div class='scanner-box'><h3 style='text-align:center; color:#dc2626 !important;'>CASA (HOME)</h3>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Letras", cat_h.count("Letra"), delta_color="off")
            c2.metric("Altas", cat_h.count("Alta"), delta_color="off")
            c3.metric("Neutras", cat_h.count("Neutra"), delta_color="off")
            c4.metric("Baixas", cat_h.count("Baixa"), delta_color="off")
            st.markdown("</div>", unsafe_allow_html=True)
        with col_a:
            cat_a = [h['cat_a'] for h in ultimas_12]
            st.markdown("<div class='scanner-box'><h3 style='text-align:center; color:#2563eb !important;'>FORA (AWAY)</h3>", unsafe_allow_html=True)
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Letras", cat_a.count("Letra"), delta_color="off")
            f2.metric("Altas", cat_a.count("Alta"), delta_color="off")
            f3.metric("Neutras", cat_a.count("Neutra"), delta_color="off")
            f4.metric("Baixas", cat_a.count("Baixa"), delta_color="off")
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    if st.session_state.historico:
        cols = st.columns(12)
        for i, h in enumerate(st.session_state.historico[:12]):
            c = "casa" if h['Vencedor'] == 'Home' else 'fora' if h['Vencedor'] == 'Away' else 'empate'
            border = "4px solid #16a34a" if h.get('status') == "Green" else "4px solid #dc2626" if h.get('status') == "Red" else "1px solid #94a3b8"
            cols[i].markdown(f"<div style='text-align:center; border:{border}; border-radius:10px; padding:8px; background:white;'><span class='bola {c}'></span><br><b>{h['H']}x{h['A']}</b></div>", unsafe_allow_html=True)

else:
    lucro = st.session_state.banca_atual - st.session_state.banca_inicial
    st.markdown(f"""
        <div style="text-align:center; padding:50px; background:white; border:5px solid #16a34a; border-radius:20px;">
            <h1 style="color:#16a34a !important;">SESSÃO ENCERRADA</h1>
            <hr>
            <h2>LUCRO LÍQUIDO: R$ {lucro:.2f}</h2>
            <h3>MELHOR SEQUÊNCIA: {st.session_state.maior_seq_greens} ✅</h3>
        </div>
    """, unsafe_allow_html=True)
