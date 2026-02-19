import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração e Estética de Alto Contraste
st.set_page_config(page_title="IA ANALYZER PRO", layout="wide")

def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; color: #1e293b; }
    .card-sinal { 
        background-color: #ffffff; padding: 25px; border-radius: 15px; text-align: center; 
        border: 4px solid #3b82f6; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
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

# --- LÓGICA DRAGON TIGER (NUMÉRICA E REPETIÇÃO) ---
def categorizar_dt(v):
    if v in ['J', 'Q', 'K', 'A']: return "Alto"
    try:
        v_int = int(v)
        return "Baixo" if 1 <= v_int <= 6 else "Neutro" if 7 <= v_int <= 9 else "Alto"
    except: return "Neutro"

def analisar_dt_85(dados):
    hist_dt = [h for h in dados if h.get('Jogo') == "DT"]
    if len(hist_dt) < 3: return None
    
    padrao_atual = hist_dt[0].get('Padrao')
    matches = [h for h in hist_dt[1:] if h.get('Padrao') == padrao_atual]
    
    if matches:
        venc_f = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
        conf = ([m["Vencedor"] for m in matches].count(venc_f) / len(matches)) * 100
        if conf >= 85:
            return {"estrategia": f"Padrão Numérico {padrao_atual}", "sug": venc_f, "conf": conf}
    
    # Check de Repetição de Cor
    cores = [h['Vencedor'] for h in hist_dt[:3]]
    if len(set(cores)) == 1 and cores[0] != "Empate":
        sug_quebra = "Vermelho" if cores[0] == "Azul" else "Azul"
        return {"estrategia": "Quebra de Repetição", "sug": sug_quebra, "conf": 85}
    return None

# --- LÓGICA BAC BO (ROADMAPS) ---
def analisar_bacbo_roadmap(dados):
    hist_bb = [h for h in dados if h.get('Jogo') == "BB"]
    if len(hist_bb) < 4: return None
    v = [h['Vencedor'][0] for h in hist_bb[:10] if h.get('Vencedor')]
    v_limpo = [x for x in v if x != 'E']
    
    if len(v_limpo) < 3: return None
    if v_limpo[0] == v_limpo[1] == v_limpo[2]:
        return {"estrategia": "Dragão (Roadmap)", "sug": "Player" if v_limpo[0]=='P' else "Banker", "conf": 92}
    return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧙‍♂️ Gestão do Mago")
    jogo_ativo = st.selectbox("Escolha o Jogo:", ["Dragon Tiger", "Bac Bo", "Roleta"])
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual))
    perc_entrada = st.slider("Mão (%)", 1, 30, 15) / 100
    stop_limit = st.number_input("Stop Win/Loss", 1, 30, 5)
    
    if jogo_ativo == "Bac Bo":
        estabilidade = st.radio("Tabelas Menores:", ["Estável (Vermelho)", "Caos (Azul)"])
    
    if st.button("RESETAR SISTEMA"):
        st.session_state.clear(); st.rerun()

is_stopped = st.session_state.greens_dia >= stop_limit or st.session_state.reds_dia >= stop_limit
entrada_v = st.session_state.banca_atual * perc_entrada

st.title(f"🚀 ANALYZER - {jogo_ativo.upper()}")

if is_stopped:
    st.error("### 🛑 OPERAÇÕES BLOQUEADAS: META OU STOP ATINGIDO")
else:
    c_reg, c_prev = st.columns([1, 1.4])

    with c_reg:
        st.subheader("📥 Registro")
        if jogo_ativo == "Dragon Tiger":
            cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
            az = st.selectbox("Dragão", cartas); ver = st.selectbox("Tigre", cartas)
            if st.button("PROCESSAR DT"):
                p_map = {'J':11,'Q':12,'K':13,'A':14}
                n_az = p_map.get(az, int(az) if az.isdigit() else 0)
                n_ver = p_map.get(ver, int(ver) if ver.isdigit() else 0)
                venc = "Azul" if n_az > n_ver else "Vermelho" if n_ver > n_az else "Empate"
                padrao = f"{categorizar_dt(az)}x{categorizar_dt(ver)}"
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": padrao, "Jogo": "DT", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

        elif jogo_ativo == "Bac Bo":
            res = st.radio("Resultado:", ["Player", "Banker", "Empate"], horizontal=True)
            if st.button("PROCESSAR BB"):
                st.session_state.historico.insert(0, {"Vencedor": res, "Jogo": "BB", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

        elif jogo_ativo == "Roleta":
            massa = st.text_area("Números (Espaço ou Vírgula):")
            if st.button("ALIMENTAR ROLETA"):
                nums = [int(s) for s in re.findall(r'\b\d+\b', massa) if 0 <= int(s) <= 36]
                for n in reversed(nums):
                    st.session_state.historico.insert(0, {"Vencedor": n, "Jogo": "ROL", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

    with c_prev:
        st.subheader("🔮 Sinal 85%+")
        sinal = None
        if jogo_ativo == "Dragon Tiger":
            sinal = analisar_dt_85(st.session_state.historico)
        elif jogo_ativo == "Bac Bo" and estabilidade == "Estável (Vermelho)":
            sinal = analisar_bacbo_roadmap(st.session_state.historico)
        
        if sinal:
            cor_sinal = "#2563eb" if sinal['sug'] in ["Azul", "Player"] else "#dc2626"
            st.markdown(f"""
                <div class="card-sinal">
                    <small>{sinal['estrategia']}</small>
                    <h1 style="color: {cor_sinal}; font-size: 70px; margin: 0;">{sinal['sug'].upper()}</h1>
                    <p>Confiança: {sinal['conf']:.0f}% | Aposta: R$ {entrada_v:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            play_sound()
        else:
            st.info("Aguardando padrão crítico (85%+)...")

st.divider()
st.subheader("🕒 Tendência e Fluxo")
if st.session_state.historico:
    hist_f = [h for h in st.session_state.historico if h.get('Jogo') == ("DT" if jogo_ativo == "Dragon Tiger" else "BB" if jogo_ativo == "Bac Bo" else "ROL")][:12]
    if hist_f:
        cols = st.columns(len(hist_f))
        for i, h in enumerate(hist_f):
            v = h.get('Vencedor', '?')
            cor = "azul" if v in ["Azul", "Player"] else "vermelho" if v in ["Vermelho", "Banker"] else "amarelo"
            cols[i].markdown(f"<div style='text-align:center'><span class='bola {cor}'></span><br><b>{v}</b></div>", unsafe_allow_html=True)

    with st.expander("Ver Tabela Técnica"):
        df = pd.DataFrame(st.session_state.historico).head(15)
        # Proteção contra KeyError (Imagem 1 Corrigida)
        cols_final = [c for c in ["Hora", "Vencedor", "Padrao", "Jogo"] if c in df.columns]
        st.table(df[cols_final])
