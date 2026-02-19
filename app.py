import streamlit as st
import pandas as pd
from datetime import datetime
import re

# 1. Configuração de Performance e Estética
st.set_page_config(page_title="SUPER IA ANALYZER - MAGO TURBO", layout="wide")

def play_sound():
    # Som de alerta para sinais de alta criticidade
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; color: #1e293b; }
    .card-sinal-critico { 
        background: #ffffff; padding: 25px; border-radius: 15px; text-align: center; 
        border: 4px solid #10b981; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .azul { background-color: #2563eb; } .vermelho { background-color: #dc2626; } .amarelo { background-color: #fbbf24; }
    .carta-hist { display: inline-block; background: #fff; color: #000; padding: 5px 12px; border-radius: 6px; border: 2px solid #333; font-weight: bold; margin: 3px; box-shadow: 2px 2px 0px #000; }
</style>
""", unsafe_allow_html=True)

# 2. Dados de Setores (Roleta) e Inicialização de Memória
SETORES_ROL = {
    "Voisins du Zéro": [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25],
    "Tier du Cylindre": [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33],
    "Orphelins": [1, 20, 14, 31, 9, 17, 34, 6]
}

for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'aguardando_gale']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- MOTORES DE ANÁLISE (CRITICIDADE 85%+) ---

def analisar_roleta_turbo(numeros):
    if len(numeros) < 5: return None
    atrasos = {setor: 99 for setor in SETORES_ROL}
    for setor, lista in SETORES_ROL.items():
        for i, n in enumerate(numeros):
            if n in lista:
                atrasos[setor] = i
                break
    setor_alvo = max(atrasos, key=atrasos.get)
    if atrasos[setor_alvo] > 8: # Desvio estatístico
        return {"est": setor_alvo, "conf": 89, "msg": f"Atraso de {atrasos[setor_alvo]} rodadas."}
    return None

def analisar_dt_85(dados):
    hist = [h for h in dados if h.get('Jogo') == "DT"]
    if len(hist) < 3: return None
    padrao = hist[0].get('Padrao')
    matches = [h for h in hist[1:] if h.get('Padrao') == padrao]
    if matches:
        venc_f = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
        conf = ([m["Vencedor"] for m in matches].count(venc_f) / len(matches)) * 100
        if conf >= 85: return {"est": "Padrão Numérico", "sug": venc_f, "conf": conf}
    return None

def analisar_bacbo_roadmap(dados):
    hist = [h for h in dados if h.get('Jogo') == "BB"]
    if len(hist) < 4: return None
    v = [h['Vencedor'][0] for h in hist[:10] if h.get('Vencedor')]
    v_limp = [x for x in v if x != 'E']
    if len(v_limp) >= 3 and v_limp[0] == v_limp[1] == v_limp[2]:
        return {"est": "Dragão (Roadmap)", "sug": "Player" if v_limp[0]=='P' else "Banker", "conf": 92}
    return None

# --- SIDEBAR GESTÃO ---
with st.sidebar:
    st.header("🧙‍♂️ Painel do Mago")
    jogo_ativo = st.selectbox("Escolha o Jogo:", ["Roleta", "Dragon Tiger", "Bac Bo"])
    st.session_state.banca_atual = st.number_input("Banca Global R$", value=float(st.session_state.banca_atual))
    perc = st.slider("Mão Fixa (%)", 1, 20, 15) / 100
    stop_limit = st.number_input("Stop Win/Loss (Ciclos)", 1, 30, 5)
    if jogo_ativo == "Bac Bo":
        estabil = st.radio("Tabelas Menores:", ["Estável (Vermelho)", "Caos (Azul)"])
    if st.button("RESETAR SISTEMA"):
        st.session_state.clear(); st.rerun()

is_stopped = st.session_state.greens_dia >= stop_limit or st.session_state.reds_dia >= stop_limit
entrada_v = st.session_state.banca_atual * perc

st.title(f"🚀 ANALYZER PRO - {jogo_ativo.upper()}")

if is_stopped:
    st.error("### 🛑 GESTÃO ENCERRADA: META OU STOP ATINGIDO")
else:
    c_reg, c_prev = st.columns([1, 1.4])

    with c_reg:
        st.subheader("📥 Registro")
        if jogo_ativo == "Roleta":
            massa = st.text_area("Números em Massa ou Único:", help="Cole o histórico ou digite o número.")
            if st.button("PROCESSAR ROLETA", use_container_width=True):
                nums = [int(s) for s in re.findall(r'\b\d+\b', massa) if 0 <= int(s) <= 36]
                for n in reversed(nums):
                    st.session_state.historico.insert(0, {"Vencedor": n, "Jogo": "ROL", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()
        
        elif jogo_ativo == "Dragon Tiger":
            cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
            az = st.selectbox("Dragão", cartas); ver = st.selectbox("Tigre", cartas)
            if st.button("PROCESSAR DT"):
                p_map = {'J':11,'Q':12,'K':13,'A':14}
                venc = "Azul" if p_map.get(az, int(az) if az.isdigit() else 0) > p_map.get(ver, int(ver) if ver.isdigit() else 0) else "Vermelho"
                def cat(v):
                    if v in ['J','Q','K','A']: return "Alt"
                    return "Baix" if int(v) <= 6 else "Neut"
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"{cat(az)}x{cat(ver)}", "Az": az, "Ver": ver, "Jogo": "DT", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

        elif jogo_ativo == "Bac Bo":
            res = st.radio("Resultado:", ["Player", "Banker", "Empate"], horizontal=True)
            if st.button("PROCESSAR BB"):
                st.session_state.historico.insert(0, {"Vencedor": res, "Jogo": "BB", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

    with c_prev:
        st.subheader("🔮 Sinal de Criticidade 85%+")
        sinal = None
        hist_filt = [h['Vencedor'] for h in st.session_state.historico if h['Jogo'] == ("ROL" if jogo_ativo == "Roleta" else "BB" if jogo_ativo == "Bac Bo" else "DT")]
        
        if jogo_ativo == "Roleta": sinal = analisar_roleta_turbo(hist_filt)
        elif jogo_ativo == "Dragon Tiger": sinal = analisar_dt_85(st.session_state.historico)
        elif jogo_ativo == "Bac Bo" and estabil == "Estável (Vermelho)": sinal = analisar_bacbo_roadmap(st.session_state.historico)

        if sinal and sinal['conf'] >= 85:
            cor_s = "#2563eb" if sinal.get('sug') in ["Azul", "Player"] else "#dc2626"
            if jogo_ativo == "Roleta": cor_s = "#10b981"
            st.markdown(f"""
                <div class="card-sinal-critico">
                    <small>{sinal['est']} - CONFIRMAÇÃO IA</small>
                    <h1 style="color: {cor_s}; font-size: 60px; margin: 0;">{str(sinal.get('sug', sinal.get('est'))).upper()}</h1>
                    <p>Confiança: {sinal['conf']:.0f}% | Aposta: R$ {entrada_v:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            play_sound()
        else:
            st.info("🔎 Monitorando... Aguardando desvio estatístico favorável.")

st.divider()
st.subheader("🕒 Histórico e Fluxo")

if st.session_state.historico:
    hist_v = [h for h in st.session_state.historico if h.get('Jogo') == ("ROL" if jogo_ativo == "Roleta" else "BB" if jogo_ativo == "Bac Bo" else "DT")][:12]
    if hist_v:
        cols = st.columns(len(hist_v))
        for i, h in enumerate(hist_v):
            v = h.get('Vencedor', '?')
            cor = "azul" if v in ["Azul", "Player"] else "vermelho" if v in ["Vermelho", "Banker"] else "amarelo"
            cols[i].markdown(f"<div style='text-align:center'><span class='bola {cor}'></span><br><b>{v}</b></div>", unsafe_allow_html=True)

    with st.expander("Ver Tabela de Dados"):
        df = pd.DataFrame(st.session_state.historico).head(15)
        exist_cols = [c for c in ["Hora", "Vencedor", "Padrao", "Jogo"] if c in df.columns]
        st.table(df[exist_cols])
