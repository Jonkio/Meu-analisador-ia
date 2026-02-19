import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configurações de Layout e Estética
st.set_page_config(page_title="SUPER IA ANALYZER - MODO MAGO", layout="wide")

def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #0f172a; color: #ffffff; }
    .card-sinal-critico { 
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
        padding: 30px; border-radius: 20px; text-align: center; color: white;
        border: 4px solid #60a5fa; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.5);
    }
    .status-estabilidade { padding: 5px 15px; border-radius: 50px; font-weight: bold; margin-bottom: 10px; display: inline-block; }
    .estavel { background-color: #dc2626; color: white; }
    .caos { background-color: #2563eb; color: white; }
    .carta-hist { display: inline-block; background: #fff; color: #000; padding: 5px 12px; border-radius: 6px; border: 2px solid #333; font-weight: bold; margin: 3px; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória Global
for key in ['historico', 'banca_atual', 'logs_banca', 'greens_dia', 'reds_dia', 'aguardando_gale']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'logs' in key: st.session_state[key] = [1000.0]
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- CÉREBRO DE RECONHECIMENTO DE PADRÕES (ROADMAP) ---
def analisar_bacbo_avancado(dados):
    if len(dados) < 5: return None
    v = [d['Vencedor'][0] for d in dados[:10]]
    v_limpo = [x for x in v if x != 'E'] # Foca em P e B
    
    if len(v_limpo) < 4: return None

    # Padrão Dragão (Sequência)
    if v_limpo[0] == v_limpo[1] == v_limpo[2]:
        return {"estrategia": "Dragão", "sug": "Player" if v_limpo[0]=='P' else "Banker", "conf": 92, "msg": "Nunca corte o Dragão! Siga o fluxo."}
    
    # Padrão Pinguim (Alternância)
    if v_limpo[0] != v_limpo[1] and v_limpo[1] != v_limpo[2] and v_limpo[2] != v_limpo[3]:
        return {"estrategia": "Pinguim", "sug": "Player" if v_limpo[0]=='B' else "Banker", "conf": 88, "msg": "Zigue-Zague detectado. Aposte no oposto."}
    
    # Colar de Pérolas (Duplas)
    if v_limpo[2] == v_limpo[3] and v_limpo[0] == v_limpo[1] and v_limpo[0] != v_limpo[2]:
        return {"estrategia": "Pérolas", "sug": "Player" if v_limpo[0]=='P' else "Banker", "conf": 86, "msg": "Formação de duplas PP-BB."}

    return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧙‍♂️ Painel de Gestão")
    jogo_ativo = st.selectbox("Escolha o Jogo:", ["Bac Bo", "Roleta", "Dragon Tiger"])
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual))
    perc_entrada = st.slider("Entrada (%)", 1, 30, 15) / 100
    stop_limit = st.number_input("Stop Win/Loss", 1, 30, 5)
    
    st.divider()
    st.subheader("📊 Caminhos Derivados")
    estabilidade = st.radio("Tabelas Menores:", ["Estável (Vermelho)", "Caos (Azul)"])
    
    if st.button("RESETAR SISTEMA"):
        st.session_state.clear(); st.rerun()

is_stopped = st.session_state.greens_dia >= stop_limit or st.session_state.reds_dia >= stop_limit
entrada_v = st.session_state.banca_atual * perc_entrada

st.title(f"🚀 SUPER IA ANALYZER - {jogo_ativo.upper()}")

if is_stopped:
    st.error("### 🛑 META ATINGIDA! Operações finalizadas por segurança.")
else:
    c_reg, c_prev = st.columns([1, 1.4])

    with c_reg:
        st.subheader("📥 Registro")
        if jogo_ativo == "Bac Bo":
            res = st.radio("Resultado:", ["Player", "Banker", "Empate"], horizontal=True)
            if st.button("PROCESSAR", use_container_width=True):
                st.session_state.historico.insert(0, {"Vencedor": res, "Jogo": "BB", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()
        
        elif jogo_ativo == "Roleta":
            massa = st.text_area("Números em Massa ou Único:")
            if st.button("ALIMENTAR ROLETA"):
                nums = [int(s) for s in re.findall(r'\b\d+\b', massa) if 0 <= int(s) <= 36]
                for n in reversed(nums):
                    st.session_state.historico.insert(0, {"Vencedor": n, "Jogo": "ROL", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()
        
        elif jogo_ativo == "Dragon Tiger":
            cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
            az = st.selectbox("Dragão", cartas); ver = st.selectbox("Tigre", cartas)
            if st.button("PROCESSAR DT"):
                venc = "Azul" if az > ver else "Vermelho"
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"{az}x{ver}", "Az": az, "Ver": ver, "Jogo": "DT"})
                st.rerun()

    with c_prev:
        st.subheader("🔮 Sinal 85%+")
        if estabilidade == "Caos (Azul)":
            st.warning("⚠️ **MERCADO SEM PADRÃO.** Aguarde estabilidade nos círculos vermelhos.")
        elif st.session_state.historico:
            sinal = analisar_bacbo_avancado(st.session_state.historico)
            
            if sinal and sinal['conf'] >= 85:
                st.markdown(f"""
                    <div class="card-sinal-critico">
                        <div class="status-estabilidade estavel">ESTRATÉGIA: {sinal['estrategia']}</div>
                        <h1 style="font-size: 70px; margin: 0;">{sinal['sug'].upper()}</h1>
                        <p><b>{sinal['msg']}</b></p>
                        <p>Confiança: {sinal['conf']}% | Aposta: R$ {entrada_v:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
                play_sound()
            else:
                st.info("🔎 Escaneando Roadmaps... Aguardando padrão crítico.")

st.divider()
st.subheader("🕒 Tendência e Fluxo")

if st.session_state.historico:
    hist_f = [h for h in st.session_state.historico if h['Jogo'] == ("BB" if jogo_ativo == "Bac Bo" else "ROL" if jogo_ativo == "Roleta" else "DT")][:12]
    cols = st.columns(12)
    for i, h in enumerate(hist_f):
        v = h['Vencedor']
        cor = "azul" if v == "Player" or v == "Azul" else "vermelho" if v == "Banker" or v == "Vermelho" else "amarelo"
        cols[i].markdown(f"<div style='text-align:center'><span class='bola {cor}'></span><br>{v}</div>", unsafe_allow_html=True)
