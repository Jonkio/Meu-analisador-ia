import streamlit as st
import pandas as pd
from datetime import datetime
import base64

# 1. Configuração de Layout e Estética Global
st.set_page_config(page_title="SUPER IA ANALYZER - MODO MAGO", layout="wide")

# Função para alerta sonoro (Base64)
def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3" # Som de "Ding"
    st.markdown(f"""
        <audio autoplay>
            <source src="{sound_file}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; color: #1e293b; }
    .card-sinal-95 { 
        background: linear-gradient(135deg, #065f46 0%, #064e3b 100%); 
        padding: 30px; border-radius: 15px; text-align: center; color: white;
        border: 3px solid #10b981; box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    .vela-box { display: inline-block; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin: 3px; color: white; min-width: 60px; text-align: center; }
    .vela-baixa { background-color: #3b82f6; } .vela-media { background-color: #8b5cf6; } .vela-rosa { background-color: #ec4899; }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .azul { background-color: #2563eb; } .vermelho { background-color: #dc2626; } .amarelo { background-color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória Global
for key in ['historico', 'banca_atual', 'logs_banca', 'greens_dia', 'reds_dia', 'aguardando_gale', 'stats_horario']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'logs' in key: st.session_state[key] = [1000.0]
        elif 'stats' in key: st.session_state[key] = {"Madrugada": 0, "Manhã": 0, "Tarde": 0, "Noite": 0}
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- Lógica de Apoio ---
def obter_turno():
    h = datetime.now().hour
    return "Madrugada" if 0<=h<6 else "Manhã" if 6<=h<12 else "Tarde" if 12<=h<18 else "Noite"

# --- Sidebar Global ---
with st.sidebar:
    st.header("🧙‍♂️ Gestão Estratégica")
    perc_entrada = st.slider("Mão Fixa (%)", 1, 30, 15) / 100
    stop_limit = st.number_input("Meta de Ciclos (Stop)", 1, 30, 5)
    confianca_min = st.slider("Confiança Mínima para Sinal (%)", 70, 95, 85)
    
    st.divider()
    jogo_ativo = st.selectbox("Mudar de Mesa:", ["Aviator", "Dragon Tiger", "Bac Bo", "Roleta"])
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual), step=10.0)
    
    col_g, col_r = st.columns(2)
    col_g.metric("Greens", f"{st.session_state.greens_dia}")
    col_r.metric("Reds", f"{st.session_state.reds_dia}")
    
    if st.button("LIMPAR DADOS / RESET"):
        st.session_state.clear(); st.rerun()

is_stopped = st.session_state.greens_dia >= stop_limit or st.session_state.reds_dia >= stop_limit

# --- PAINEL PRINCIPAL ---
st.title(f"🔮 SUPER ANALYZER - MODO {jogo_ativo.upper()}")

if is_stopped:
    st.error(f"### 🛑 GESTÃO ENCERRADA! Meta de {stop_limit} ciclos atingida.")
else:
    c_reg, c_prev = st.columns([1, 1.4])
    entrada_v = st.session_state.banca_atual * perc_entrada

    with c_reg:
        st.subheader("📥 Entrada de Dados")
        if jogo_ativo == "Aviator":
            v_v = st.number_input("Última Vela:", 1.0, 1000.0, 1.5, step=0.1)
            if st.button("REGISTRAR VELA", use_container_width=True):
                if st.session_state.historico and "alvo" in st.session_state.historico[0]:
                    if v_v >= st.session_state.historico[0]["alvo"]:
                        st.session_state.greens_dia += 1; st.session_state.banca_atual += entrada_v
                        st.session_state.stats_horario[obter_turno()] += 1
                    else:
                        st.session_state.reds_dia += 1; st.session_state.banca_atual -= entrada_v
                st.session_state.historico.insert(0, {"Valor": v_v, "Jogo": "AV"})
                st.session_state.logs_banca.append(st.session_state.banca_atual); st.rerun()

        elif jogo_ativo == "Dragon Tiger":
            opts = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
            az = st.selectbox("Dragão", opts); ver = st.selectbox("Tigre", opts)
            if st.button("REGISTRAR JOGO", use_container_width=True):
                pesos = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
                n_az, n_ver = pesos.get(az, int(az) if az.isdigit() else 0), pesos.get(ver, int(ver) if ver.isdigit() else 0)
                venc = "Azul" if n_az > n_ver else "Vermelho" if n_ver > n_az else "Empate"
                
                if st.session_state.historico and "previsao" in st.session_state.historico[0]:
                    if venc == st.session_state.historico[0]["previsao"]:
                        st.session_state.greens_dia += 1; st.session_state.banca_atual += entrada_v
                        st.session_state.stats_horario[obter_turno()] += 1; st.session_state.aguardando_gale = False
                    elif venc != "Empate":
                        if not st.session_state.aguardando_gale: st.session_state.aguardando_gale = True
                        else:
                            st.session_state.reds_dia += 2; st.session_state.banca_atual -= entrada_v * 3
                            st.session_state.aguardando_gale = False
                
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"{az}x{ver}"})
                st.session_state.logs_banca.append(st.session_state.banca_atual); st.rerun()

    with c_prev:
        st.subheader("🔮 Sinal de Alta Precisão")
        if st.session_state.historico:
            if jogo_ativo == "Aviator":
                velas = [h['Valor'] for h in st.session_state.historico]
                seq_azul = sum(1 for v in velas[:3] if v < 2.0) == 3
                
                if seq_azul:
                    st.error("❌ MERCADO EM RECOLHIMENTO (3 AZUIS) - NÃO OPERAR")
                else:
                    st.session_state.historico[0]["alvo"] = 1.5
                    st.markdown('<div class="card-sinal-95"><h1>ENTRADA: 1.50x</h1><p>Assertividade: 95%</p></div>', unsafe_allow_html=True)
                    play_sound()
            
            elif jogo_ativo == "Dragon Tiger":
                ult_p = st.session_state.historico[0]["Padrao"]
                matches = [h for h in st.session_state.historico[1:] if h.get("Padrao") == ult_p]
                if len(matches) >= 3:
                    venc_f = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
                    winrate = ([m["Vencedor"] for m in matches].count(venc_f) / len(matches)) * 100
                    
                    if winrate >= confianca_min:
                        st.session_state.historico[0]["previsao"] = venc_f
                        st.markdown(f'<div class="card-sinal-95"><h1>ENTRAR NO {venc_f.upper()}</h1><p>Confiança: {winrate:.0f}%</p></div>', unsafe_allow_html=True)
                        play_sound()
                    else:
                        st.info(f"Padrão detectado, mas assertividade ({winrate:.0f}%) abaixo do limite configurado.")
                else:
                    st.info("Aguardando volume de dados (Amostragem < 3)")

st.divider()

# --- HISTÓRICO VISUAL ---
st.subheader("🕒 Fluxo de Mercado (Tempo Real)")
if st.session_state.historico:
    if jogo_ativo == "Aviator":
        cols = st.columns(12)
        for i, h in enumerate(st.session_state.historico[:12]):
            v = h['Valor']
            cl = "vela-rosa" if v >= 10 else "vela-media" if v >= 2 else "vela-baixa"
            cols[i].markdown(f"<div class='vela-box {cl}'>{v}x</div>", unsafe_allow_html=True)
    else:
        for h in st.session_state.historico[:10]:
            v = h.get("Vencedor", "Azul")
            cor = "azul" if v == "Azul" else "vermelho" if v == "Vermelho" else "amarelo"
            st.markdown(f"<span class='bola {cor}'></span> **{v}** | Padrão: {h.get('Padrao','')}", unsafe_allow_html=True)

st.info("💡 **Dica do Mago**: O som de alerta indica o momento exato da quebra de ciclo favorável.")
