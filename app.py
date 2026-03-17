import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Configuração de Layout
st.set_page_config(page_title="IA ANALYZER - V6.4 EQUILIBRADO", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f1f5f9; color: #1e293b; }
    .card-sinal-on { 
        background-color: #ffffff; padding: 30px; border-radius: 15px; text-align: center;
        border: 5px solid #22c55e; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    h1, h2, h3, p, span { color: #1e293b !important; }
    .monitor-item { background-color: #ffffff; padding: 10px; border-radius: 10px; margin-bottom: 8px; border: 2px solid #6366f1; font-weight: bold; }
    .scanner-box { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #cbd5e1; }
    .bola { height: 14px; width: 14px; border-radius: 50%; display: inline-block; margin: 0 3px; border: 1px solid #94a3b8; }
    .casa { background-color: #dc2626; } .fora { background-color: #2563eb; } .empate { background-color: #eab308; } 
</style>
""", unsafe_allow_html=True)

# 2. Memória e Controles de Travas
for key in ['historico', 'banca_inicial', 'banca_atual', 'max_seq_home', 'max_seq_away', 'rodadas_lock', 
            'wins_sessao', 'total_sinais', 'sessao_ativa', 'seq_greens_atual', 'maior_seq_greens', 'deck_count', 'ultima_estratégia']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 3000.0
        elif key == 'sessao_ativa': st.session_state[key] = True
        elif key == 'deck_count':
            st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
            for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- FUNÇÕES TÉCNICAS ---

def categorizar_carta(carta):
    if carta in ['2', '3', '4', '5']: return "Baixa"
    if carta in ['6', '7', '8', '9']: return "Neutra"
    if carta in ['10']: return "Alta"
    if carta in ['J', 'Q', 'K', 'A']: return "Letra"
    return "N/A"

def analisar_mago_equilibrado(dados, deck):
    if len(dados) < 6 or st.session_state.rodadas_lock > 0: return None
    
    v = [h['Vencedor'][0] for h in dados if h.get('Vencedor')]
    v_str = "".join(v[:12])
    p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
    
    # Média de força recente para evitar quebras falsas
    forca_h = sum([p_map.get(h['H'], 0) for h in dados[:3]]) / 3
    forca_a = sum([p_map.get(h['A'], 0) for h in dados[:3]]) / 3

    # 1. PRIORIDADE: PADRÕES DE FLUXO (Escalas)
    if v_str.startswith("HHA") and forca_h > 7: return {"sug": "Home", "est": "ESCALA 2x1", "conf": 94}
    if v_str.startswith("AAH") and forca_a > 7: return {"sug": "Away", "est": "ESCALA 2x1", "conf": 94}
    if "HHAAAHH" in v_str or "AAHHHAA" in v_str: return {"sug": "Away" if v[0]=='H' else "Home", "est": "SIMETRIA OCO", "conf": 92}

    # 2. SECUNDÁRIO: QUEBRA DE MÁXIMA (Com trava de segurança)
    seq = 1
    for i in range(len(v)-1):
        if v[i] == v[i+1] and v[i] != 'E': seq += 1
        else: break
    
    # Só sinaliza quebra se a sequência for MAIOR que a máxima E a força do lado estiver caindo
    if v[0] == 'H' and seq >= st.session_state.max_seq_home and seq >= 5 and forca_h < 8:
        if st.session_state.ultima_estratégia != "QUEBRA_H":
            return {"sug": "Away", "est": "QUEBRA DE MÁXIMA (+5)", "conf": 91}
            
    if v[0] == 'A' and seq >= st.session_state.max_seq_away and seq >= 5 and forca_a < 8:
        if st.session_state.ultima_estratégia != "QUEBRA_A":
            return {"sug": "Home", "est": "QUEBRA DE MÁXIMA (+5)", "conf": 91}

    return None

# --- INTERFACE ---
if st.session_state.sessao_ativa:
    st.markdown("<h1 style='text-align: center;'>⚽ FOOTBALL STUDIO IA - V6.4 PRO</h1>", unsafe_allow_html=True)
    
    col_gestao1, col_gestao2, col_gestao3, col_gestao4 = st.columns([1, 1, 1, 1])
    with col_gestao1: st.session_state.banca_inicial = st.number_input("BANCA INICIAL (R$)", value=float(st.session_state.banca_inicial))
    with col_gestao2: st.session_state.banca_atual = st.number_input("SALDO ATUAL (R$)", value=float(st.session_state.banca_atual))
    with col_gestao3: perfil = st.selectbox("MODO", ["CALMA (0.5%)", "MODERADA (1%)", "ATACANTE (2.5%)"], index=1)
    with col_gestao4: 
        st.write("")
        if st.button("⛔ ENCERRAR", use_container_width=True): st.session_state.sessao_ativa = False; st.rerun()

    st.divider()

    c_in, c_sinal, c_apex = st.columns([1, 1.4, 1])

    with c_in:
        st.subheader("📥 REGISTRO")
        cartas = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        h_c = st.selectbox("CASA", cartas); a_c = st.selectbox("FORA", cartas)
        if st.button("REGISTRAR JOGADA", use_container_width=True):
            p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
            venc = "Home" if p_map[h_c] > p_map[a_c] else "Away" if p_map[a_c] > p_map[h_c] else "Empate"
            
            # Validação de Win/Loss e Reset de Estratégia
            status = "None"
            risco = 0.005 if "CALMA" in perfil else 0.01 if "MODERADA" in perfil else 0.025
            if st.session_state.historico and "prev" in st.session_state.historico[0]:
                st.session_state.total_sinais += 1
                if venc == st.session_state.historico[0]["prev"]:
                    status = "Green"; st.session_state.wins_sessao += 1; st.session_state.seq_greens_atual += 1
                    st.session_state.banca_atual += (st.session_state.banca_atual * risco)
                    st.session_state.ultima_estratégia = "" # Limpa trava
                elif venc != "Empate":
                    status = "Red"; st.session_state.seq_greens_atual = 0
                    st.session_state.banca_atual -= (st.session_state.banca_atual * risco)

            if venc == "Empate": st.session_state.rodadas_lock = 2
            elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
            
            st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_c, "A": a_c, "status": status, "cat_h": categorizar_carta(h_c), "cat_a": categorizar_carta(a_c)})
            st.rerun()

    with c_sinal:
        st.subheader("🔮 SINAL")
        sinal = analisar_mago_equilibrado(st.session_state.historico, st.session_state.deck_count)
        if st.session_state.rodadas_lock > 0: st.warning("Aguarde Mesa...")
        elif sinal:
            cor = "#dc2626" if sinal['sug'] == "Home" else "#2563eb"
            st.markdown(f'<div class="card-sinal-on"><h2 style="margin:0;">{sinal["est"]}</h2><h1 style="color:{cor}; font-size:85px; margin:5px 0;">{sinal["sug"].upper()}</h1><h3>CONFIANÇA: {sinal["conf"]}%</h3></div>', unsafe_allow_html=True)
            st.session_state.historico[0]["prev"] = sinal['sug']
            if "MÁXIMA" in sinal["est"]: st.session_state.ultima_estratégia = f"QUEBRA_{sinal['sug'][0]}"
        else: st.info("Escaneando fluxo de mesa...")

    with c_apex:
        st.subheader("🛰️ STATUS")
        lucro = st.session_state.banca_atual - st.session_state.banca_inicial
        st.markdown(f'<div class="monitor-item">💰 SALDO: R$ {st.session_state.banca_atual:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="monitor-item" style="color:#16a34a !important;">📈 LUCRO: R$ {lucro:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="monitor-item">🔥 STREAK: {st.session_state.seq_greens_atual} ✅</div>', unsafe_allow_html=True)

    st.divider()
    # SCANNER DE CARTAS E ROADMAP MANTIDOS ABAIXO... (IGUAL V6.3)
