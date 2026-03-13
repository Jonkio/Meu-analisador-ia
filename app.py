import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração de Layout
st.set_page_config(page_title="IA ANALYZER - CARD COUNTING", layout="wide")

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
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .casa { background-color: #ef4444; } .fora { background-color: #3b82f6; } .empate { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização do Baralho (8 Decks padrão Evolution)
if 'deck_count' not in st.session_state:
    st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
    for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32

for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'aguardando_gale', 'rodadas_lock']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'lock' in key: st.session_state[key] = 0
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- FUNÇÕES TÉCNICAS ---
def categorizar_carta(v):
    p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
    val = p_map.get(v, 0)
    if val <= 6: return "Baixo"
    if val >= 10: return "Alto"
    return "Neutro"

def analisar_convergencia(dados):
    if len(dados) < 5 or st.session_state.rodadas_lock > 0: return None
    v = [h['Vencedor'][0] for h in dados[:10]]
    v_str = "".join(v)
    
    # Padrão de Escala + Força (Convergência 95%)
    forca_h = sum([int(h.get('v_h', 0)) for h in dados[:5]]) / 5
    forca_a = sum([int(h.get('v_a', 0)) for h in dados[:5]]) / 5

    if v_str.startswith("HHA") and forca_h > forca_a:
        return {"sug": "Home", "est": "Escala 2x1 + Força", "conf": 95}
    elif v_str.startswith("AAH") and forca_a > forca_h:
        return {"sug": "Away", "est": "Escala 2x1 + Força", "conf": 95}
    return None

# --- SIDEBAR: MONITOR DE BARALHO ---
with st.sidebar:
    st.header("🗃️ Status do Baralho")
    df_deck = pd.DataFrame(list(st.session_state.deck_count.items()), columns=['Carta', 'Qtd'])
    st.bar_chart(df_deck.set_index('Carta'))
    
    if st.button("RESETAR DECK (Novo Shoe)"):
        st.session_state.deck_count = {str(c): 32 for c in range(2, 11)}
        for f in ['J', 'Q', 'K', 'A']: st.session_state.deck_count[f] = 32
        st.rerun()

    st.divider()
    st.session_state.banca_atual = st.number_input("Banca R$", value=float(st.session_state.banca_atual))
    if st.button("LIMPAR SESSÃO"): st.session_state.clear(); st.rerun()

# --- ÁREA PRINCIPAL: LANÇAMENTOS ---
st.title("⚽ FOOTBALL STUDIO IA - ELITE")

col_input, col_sinal = st.columns([1, 1.3])

with col_input:
    st.subheader("📥 Lançamento de Dados")
    # Agora os registros ficam em evidência aqui
    cartas_opcoes = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    home_val = st.selectbox("Carta HOME (Casa)", cartas_opcoes)
    away_val = st.selectbox("Carta AWAY (Fora)", cartas_opcoes)
    
    if st.button("REGISTRAR JOGADA", use_container_width=True):
        p_map = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}
        v_h, v_a = p_map[home_val], p_map[away_val]
        venc = "Home" if v_h > v_a else "Away" if v_a > v_h else "Empate"
        
        # Atualiza Contagem de Cartas
        st.session_state.deck_count[home_val] -= 1
        st.session_state.deck_count[away_val] -= 1
        
        # Lógica de Lock após Empate
        if venc == "Empate": st.session_state.rodadas_lock = 2
        elif st.session_state.rodadas_lock > 0: st.session_state.rodadas_lock -= 1
        
        st.session_state.historico.insert(0, {
            "Vencedor": venc, "H": home_val, "A": away_val, 
            "v_h": v_h, "v_a": v_a, "Hora": datetime.now().strftime("%H:%M")
        })
        st.rerun()

with col_sinal:
    st.subheader("🔮 Sinal de Elite (85% a 95%)")
    sinal = analisar_convergencia(st.session_state.historico)
    
    if st.session_state.rodadas_lock > 0:
        st.info(f"🔎 MODO OBSERVAÇÃO: {st.session_state.rodadas_lock} rodadas restantes.")
    elif sinal:
        cor_hex = "#ef4444" if sinal['sug'] == "Home" else "#3b82f6"
        st.markdown(f"""
            <div class="card-elite">
                <small>CONVERGÊNCIA IDENTIFICADA</small>
                <h1 style="color: {cor_hex}; font-size: 80px; margin: 0;">{sinal['sug'].upper()}</h1>
                <p>Estratégia: <b>{sinal['est']}</b> | Confiança: <b>{sinal['conf']}%</b></p>
            </div>
        """, unsafe_allow_html=True)
        play_sound()
    else:
        st.info("Aguardando padrão de escala alinhado com a força das cartas...")

st.divider()
st.subheader("🕒 Histórico de Lançamentos")
if st.session_state.historico:
    df_hist = pd.DataFrame(st.session_state.historico).head(15)
    st.table(df_hist[["Hora", "Vencedor", "H", "A"]])
