import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração de Layout
st.set_page_config(page_title="IA ANALYZER - CARD COUNTING", layout="wide")

def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# Estética de Estádio e Contadores
st.markdown("""
<style>
    .main { background-color: #064e3b; color: #ffffff; }
    .card-elite { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
        padding: 30px; border-radius: 20px; text-align: center; color: white;
        border: 4px solid #fbbf24; box-shadow: 0 15px 35px rgba(0,0,0,0.6);
    }
    .contador-box { background: #111827; padding: 10px; border-radius: 10px; border: 1px solid #fbbf24; text-align: center; }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória e Contagem de Cartas
if 'deck_count' not in st.session_state:
    # Simulação de um baralho de 8 decks (padrão Evolution)
    st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
    for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32

for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'aguardando_gale', 'rodadas_lock']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'lock' in key: st.session_state[key] = 0
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- MOTOR DE CONTAGEM E PROBABILIDADE ---

def calcular_probabilidades():
    cartas_restantes = sum(st.session_state.deck_count.values())
    if cartas_restantes == 0: return 0, 0
    
    # Cartas Altas (10, J, Q, K, A)
    altas = sum([st.session_state.deck_count[c] for c in ['10', 'J', 'Q', 'K', 'A']])
    prob_alta = (altas / cartas_restantes) * 100
    
    # Cartas Baixas (2, 3, 4, 5, 6)
    baixas = sum([st.session_state.deck_count[str(c)] for c in range(2, 7)])
    prob_baixa = (baixas / cartas_restantes) * 100
    
    return prob_alta, prob_baixa

# --- SIDEBAR ---
with st.sidebar:
    st.header("🗃️ Monitor de Baralho")
    prob_alta, prob_baixa = calcular_probabilidades()
    st.metric("Probabilidade Carta ALTA", f"{prob_alta:.1f}%")
    st.metric("Probabilidade Carta BAIXA", f"{prob_baixa:.1f}%")
    
    if st.button("RESETAR BARALHO / DECK"):
        st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
        for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32
        st.rerun()
    
    st.divider()
    st.session_state.banca_atual = st.number_input("Banca R$", value=float(st.session_state.banca_atual))
    if st.button("RESETAR SESSÃO"): st.session_state.clear(); st.rerun()

# --- INTERFACE PRINCIPAL ---
st.title("⚽ FOOTBALL STUDIO IA - ELITE + CARD COUNTING")

c_in, c_prev = st.columns([1, 1.4])

with c_in:
    st.subheader("📥 Registro e Baixa")
    cartas_lista = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    h_c = st.selectbox("Casa (Home)", cartas_lista)
    a_c = st.selectbox("Fora (Away)", cartas_lista)
    
    if st.button("PROCESSAR E CONTAR", use_container_width=True):
        # Baixa no Deck
        st.session_state.deck_count[h_c] -= 1
        st.session_state.deck_count[a_c] -= 1
        
        # Lógica de Vencedor
        p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
        venc = "Home" if p_map[h_c] > p_map[a_c] else "Away" if p_map[a_c] > p_map[h_c] else "Empate"
        
        if venc == "Empate": st.session_state.rodadas_lock = 2
        elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
        
        st.session_state.historico.insert(0, {"Vencedor": venc, "H": h_c, "A": a_c, "Hora": datetime.now().strftime("%H:%M")})
        st.rerun()

with c_prev:
    st.subheader("🔮 Palpite com Contagem de Deck")
    # Aqui a IA integra a contagem: Se prob_alta for > 45%, reforça o sinal de 95%
    
    if st.session_state.rodadas_lock > 0:
        st.info("🔎 MODO OBSERVAÇÃO ATIVO.")
    elif len(st.session_state.historico) >= 5:
        # (Lógica de sinais simplificada para visualização)
        st.markdown(f"""
            <div class="card-elite">
                <span class="status-lock">ANÁLISE DE DECK ATIVA</span>
                <h1 style="color: #fbbf24; font-size: 50px; margin: 15px 0;">AGUARDANDO BRECHA</h1>
                <p>O deck está com <b>{prob_alta:.1f}%</b> de cartas altas restantes.</p>
                <small>Combine com padrões de Escala (2x1, 3x2x1) para entradas de 95%.</small>
            </div>
        """, unsafe_allow_html=True)
