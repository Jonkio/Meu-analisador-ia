import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração de Layout
st.set_page_config(page_title="SUPER IA ANALYZER - CRITICIDADE 85%", layout="wide")

def play_sound():
    # Som de notificação para sinais confirmados
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #f0f2f6; color: #1e293b; }
    .card-sinal-critico { 
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
        padding: 30px; border-radius: 20px; text-align: center; color: white;
        border: 4px solid #3b82f6; box-shadow: 0 10px 25px rgba(59, 130, 246, 0.5);
    }
    .status-badge { padding: 5px 15px; border-radius: 50px; font-weight: bold; background: #10b981; color: white; }
    .vela-box { display: inline-block; padding: 10px; border-radius: 8px; font-weight: bold; margin: 4px; color: white; min-width: 65px; text-align: center; }
    .vela-baixa { background-color: #3b82f6; } .vela-media { background-color: #8b5cf6; } .vela-rosa { background-color: #ec4899; }
</style>
""", unsafe_allow_html=True)

# 2. Memória do Sistema
for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia']:
    if key not in st.session_state:
        st.session_state[key] = 1000.0 if 'banca' in key else [] if 'historico' in key else 0

# --- Lógica de Criticidade ---
def calcular_confianca(jogo, padrao_atual):
    # Filtra o histórico apenas para o jogo atual
    hist = [h for h in st.session_state.historico if h['Jogo'] == jogo]
    if len(hist) < 5: return 0 # Amostragem mínima de 5 mãos para gerar sinal
    
    matches = [h for h in hist[1:] if h.get("Padrao") == padrao_atual]
    if not matches: return 0
    
    venc_f = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
    taxa_acerto = ([m["Vencedor"] for m in matches].count(venc_f) / len(matches)) * 100
    return taxa_acerto, venc_f

# --- Sidebar ---
with st.sidebar:
    st.header("🛡️ Filtro de Criticidade")
    st.success("Mínimo Exigido: 85%")
    jogo_ativo = st.selectbox("Mesa Ativa:", ["Aviator", "Dragon Tiger", "Bac Bo", "Roleta"])
    st.session_state.banca_atual = st.number_input("Saldo R$", value=float(st.session_state.banca_atual))
    perc = st.slider("Mão (%)", 1, 20, 10) / 100
    if st.button("RESETAR GERAL"):
        st.session_state.clear(); st.rerun()

st.title(f"🚀 IA ANALYZER - {jogo_ativo.upper()}")

c_reg, c_prev = st.columns([1, 1.2])

with c_reg:
    st.subheader("📥 Registro de Rodada")
    if jogo_ativo == "Aviator":
        v = st.number_input("Vela", 1.0, 500.0, 1.5)
        if st.button("REGISTRAR"):
            st.session_state.historico.insert(0, {"Valor": v, "Jogo": "AV", "Vencedor": "Win" if v >= 1.5 else "Loss", "Padrao": "Scalp"})
            st.rerun()
    elif jogo_ativo == "Dragon Tiger":
        az = st.selectbox("Dragão", [str(i) for i in range(1,11)]+['J','Q','K','A'])
        ver = st.selectbox("Tigre", [str(i) for i in range(1,11)]+['J','Q','K','A'])
        if st.button("REGISTRAR"):
            venc = "Azul" if az > ver else "Vermelho" # Simplificado para o exemplo
            st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"{az}x{ver}", "Jogo": "DT"})
            st.rerun()
    elif jogo_ativo == "Bac Bo":
        s1 = st.number_input("Azul", 2, 12, 7); s2 = st.number_input("Vermelho", 2, 12, 7)
        if st.button("REGISTRAR"):
            venc = "Azul" if s1 > s2 else "Vermelho"
            st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": "Soma", "Jogo": "BB"})
            st.rerun()
    elif jogo_ativo == "Roleta":
        n = st.number_input("Número", 0, 36)
        if st.button("REGISTRAR"):
            st.session_state.historico.insert(0, {"Vencedor": n, "Padrao": "Numero", "Jogo": "ROL"})
            st.rerun()

with c_prev:
    st.subheader("🎯 Oportunidade Qualificada")
    if st.session_state.historico:
        ult = st.session_state.historico[0]
        conf, sugestao = calcular_confianca(ult['Jogo'], ult.get('Padrao'))
        
        if conf >= 85:
            st.markdown(f'''
                <div class="card-sinal-critico">
                    <span class="status-badge">CONFIANÇA {conf:.0f}%</span>
                    <h1>ENTRADA CONFIRMADA</h1>
                    <h3>APOSTAR NO {str(sugestao).upper()}</h3>
                    <p>Valor Sugerido: R$ {st.session_state.banca_atual * perc:.2f}</p>
                </div>
            ''', unsafe_allow_html=True)
            play_sound()
        else:
            st.warning(f"⚠️ **AGUARDANDO CRITICIDADE (Atual: {conf:.0f}%)**")
            st.info("O sinal só será disparado quando a probabilidade de acerto for maior que 85% baseada no histórico de padrões.")

st.divider()
st.subheader("🕒 Histórico Recente")
hist_jogo = [h for h in st.session_state.historico if h['Jogo'] == ("AV" if jogo_ativo == "Aviator" else "DT" if jogo_ativo == "Dragon Tiger" else "BB" if jogo_ativo == "Bac Bo" else "ROL")][:10]
cols = st.columns(10)
for i, h in enumerate(hist_jogo):
    val = h.get('Valor', h.get('Vencedor'))
    cols[i].code(f"{val}")
