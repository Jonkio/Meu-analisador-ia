import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração de Layout e Estética de Alto Contraste
st.set_page_config(page_title="IA ANALYZER PRO - SISTEMA MAGO", layout="wide")

# Função de Som para Alertas
def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; color: #1e293b; }
    .card-sinal-critico { 
        background-color: #ffffff; padding: 25px; border-radius: 15px; text-align: center; 
        border: 4px solid #3b82f6; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
    }
    .carta-hist { 
        display: inline-block; background: #fff; color: #000; padding: 5px 12px; 
        border-radius: 6px; border: 2px solid #333; font-weight: bold; margin: 3px; 
        box-shadow: 2px 2px 0px #000;
    }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .azul { background-color: #2563eb; } .vermelho { background-color: #dc2626; } .amarelo { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização Segura de Memória
for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'aguardando_gale']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- Lógicas de Apoio e Roadmap ---
def analisar_padroes_avancados(dados):
    if len(dados) < 5: return None
    # Proteção contra erros de índice (Imagem 6)
    v = [str(d.get('Vencedor', ''))[0] for d in dados[:10] if d.get('Vencedor')]
    v_limpo = [x for x in v if x != 'E'] 
    
    if len(v_limpo) < 4: return None

    # Padrão Dragão
    if v_limpo[0] == v_limpo[1] == v_limpo[2]:
        return {"estrategia": "Dragão", "sug": "Player" if v_limpo[0]=='P' else "Banker", "conf": 92}
    
    # Padrão Pinguim (Zigue-Zague)
    if v_limpo[0] != v_limpo[1] and v_limpo[1] != v_limpo[2] and v_limpo[2] != v_limpo[3]:
        return {"estrategia": "Pinguim", "sug": "Player" if v_limpo[0]=='B' else "Banker", "conf": 88}

    return None

# --- Sidebar ---
with st.sidebar:
    st.header("🧙‍♂️ Gestão do Mago")
    jogo_ativo = st.selectbox("Escolha o Jogo:", ["Bac Bo", "Roleta", "Dragon Tiger"])
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual))
    perc_entrada = st.slider("Mão (%)", 1, 30, 15) / 100
    stop_limit = st.number_input("Stop Win/Loss (Ciclos)", 1, 30, 5)
    
    st.divider()
    st.subheader("📊 Caminhos Derivados")
    estabilidade = st.radio("Tabelas Menores:", ["Estável (Vermelho)", "Caos (Azul)"])
    
    if st.button("RESETAR SISTEMA"):
        st.session_state.clear(); st.rerun()

is_stopped = st.session_state.greens_dia >= stop_limit or st.session_state.reds_dia >= stop_limit
entrada_v = st.session_state.banca_atual * perc_entrada

st.title(f"🚀 SUPER IA ANALYZER - {jogo_ativo.upper()}")

if is_stopped:
    tipo_stop = "META ATINGIDA! 🎉" if st.session_state.greens_dia >= stop_limit else "STOP LOSS ATINGIDO! 🛡️"
    st.error(f"### 🛑 OPERAÇÕES BLOQUEADAS: {tipo_stop}")
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
            massa = st.text_area("Cole os números (Espaço ou Vírgula):")
            if st.button("ALIMENTAR ROLETA"):
                nums = [int(s) for s in re.findall(r'\b\d+\b', massa) if 0 <= int(s) <= 36]
                for n in reversed(nums):
                    st.session_state.historico.insert(0, {"Vencedor": n, "Jogo": "ROL", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()
        
        elif jogo_ativo == "Dragon Tiger":
            cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
            az = st.selectbox("Dragão", cartas); ver = st.selectbox("Tigre", cartas)
            if st.button("PROCESSAR DT"):
                venc = "Azul" if az > ver else "Vermelho" if ver > az else "Empate"
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"{az}x{ver}", "Az": az, "Ver": ver, "Jogo": "DT", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

    with c_prev:
        st.subheader("🔮 Sinal 85%+")
        if estabilidade == "Caos (Azul)":
            st.warning("⚠️ **MERCADO SEM PADRÃO.** Aguarde círculos vermelhos.")
        elif st.session_state.historico:
            sinal = analisar_padroes_avancados(st.session_state.historico)
            
            if sinal and sinal['conf'] >= 85:
                tipo = "🎯 ENTRADA DIRETA"
                cor_sinal = "#2563eb" if sinal['sug'] in ["Player", "Azul"] else "#dc2626"
                st.markdown(f"""
                    <div class="card-sinal-critico">
                        <small style="color: #64748b;">{tipo} - ESTRATÉGIA: {sinal['estrategia']}</small>
                        <h1 style="color: {cor_sinal}; font-size: 70px; margin: 10px 0;">{sinal['sug'].upper()}</h1>
                        <p style="color: #1e293b; font-size: 20px;"><b>Confiança: {sinal['conf']}%</b> | Aposta: R$ {entrada_v:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
                play_sound()
            else:
                st.info("🔎 Escaneando Roadmaps... Aguardando padrão crítico (85%+).")

st.divider()
st.subheader("🕒 Tendência e Fluxo")

# Histórico Visual (Imagem 1 Corrigida com verificação de colunas)
if st.session_state.historico:
    hist_f = [h for h in st.session_state.historico if h.get('Jogo') == ("BB" if jogo_ativo == "Bac Bo" else "ROL" if jogo_ativo == "Roleta" else "DT")][:12]
    
    if hist_f:
        cols = st.columns(len(hist_f))
        for i, h in enumerate(hist_f):
            v = h.get('Vencedor', '?')
            cor = "azul" if v in ["Player", "Azul"] else "vermelho" if v in ["Banker", "Vermelho"] else "amarelo"
            cols[i].markdown(f"<div style='text-align:center'><span class='bola {cor}'></span><br><b>{v}</b></div>", unsafe_allow_html=True)

    with st.expander("Ver Tabela Técnica"):
        df = pd.DataFrame(st.session_state.historico).head(15)
        # Filtra apenas colunas que realmente existem para evitar KeyError (Imagem 1)
        cols_disponiveis = [c for c in ["Hora", "Vencedor", "Padrao", "Jogo"] if c in df.columns]
        st.table(df[cols_disponiveis])
