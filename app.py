import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração de Layout e Estética
st.set_page_config(page_title="SUPER IA ANALYZER - SISTEMA MAGO", layout="wide")

# Função para alerta sonoro
def play_sound():
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

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
for key in ['historico', 'banca_atual', 'logs_banca', 'greens_dia', 'reds_dia', 'aguardando_gale']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'logs' in key: st.session_state[key] = [1000.0]
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- Mapeamento Roleta e Lógicas ---
CILINDRO = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
def categorizar_carta(v):
    if v in ['J', 'Q', 'K', 'A']: return "Alta"
    try: return "Baixa" if int(v) <= 6 else "Neutra" if int(v) <= 9 else "Alta"
    except: return "Neutra"

# --- Sidebar ---
with st.sidebar:
    st.header("🧙‍♂️ Gestão do Mago")
    jogo_ativo = st.selectbox("Selecione o Jogo:", ["Dragon Tiger", "Bac Bo", "Roleta", "Aviator"])
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual))
    perc_entrada = st.slider("Entrada (%)", 1, 30, 15) / 100
    stop_limit = st.number_input("Stop Win/Loss", 1, 30, 5)
    
    st.divider()
    st.metric("Greens", f"{st.session_state.greens_dia}")
    st.metric("Reds", f"{st.session_state.reds_dia}")
    if st.button("RESETAR SISTEMA"):
        st.session_state.clear(); st.rerun()

is_stopped = st.session_state.greens_dia >= stop_limit or st.session_state.reds_dia >= stop_limit
entrada_v = st.session_state.banca_atual * perc_entrada

st.title(f"🔮 IA ANALYZER - MODO {jogo_ativo.upper()}")

if is_stopped:
    st.error("🛑 META ATINGIDA!")
else:
    c_reg, c_prev = st.columns([1, 1.4])

    with c_reg:
        st.subheader("📥 Inserir Dados")
        
        # --- DRAGON TIGER ---
        if jogo_ativo == "Dragon Tiger":
            cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
            az = st.selectbox("Carta Dragão", cartas); ver = st.selectbox("Carta Tigre", cartas)
            if st.button("ANALISAR MÃO"):
                p = {'J':11,'Q':12,'K':13,'A':14}; n_az = p.get(az, int(az) if az.isdigit() else 0); n_ver = p.get(ver, int(ver) if ver.isdigit() else 0)
                venc = "Azul" if n_az > n_ver else "Vermelho" if n_ver > n_az else "Empate"
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"{categorizar_carta(az)}x{categorizar_carta(ver)}", "Jogo": "DT"})
                st.rerun()

        # --- BAC BO ---
        elif jogo_ativo == "Bac Bo":
            s_az = st.number_input("Soma Azul (Dados)", 2, 12, 7); s_ver = st.number_input("Soma Vermelho (Dados)", 2, 12, 7)
            if st.button("ANALISAR DADOS"):
                venc = "Azul" if s_az > s_ver else "Vermelho" if s_ver > s_az else "Empate"
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"Soma{s_az}x{s_ver}", "Jogo": "BB"})
                st.rerun()

        # --- ROLETA ---
        elif jogo_ativo == "Roleta":
            num = st.number_input("Número Sorteado", 0, 36, 0)
            if st.button("ANALISAR ROLETA"):
                idx = CILINDRO.index(num)
                vizinhos = [CILINDRO[(idx + i) % len(CILINDRO)] for i in range(-2, 3)]
                st.session_state.historico.insert(0, {"Numero": num, "vizinhos": vizinhos, "Jogo": "ROL"})
                st.rerun()

        # --- AVIATOR ---
        elif jogo_ativo == "Aviator":
            vela = st.number_input("Última Vela", 1.0, 1000.0, 1.5)
            if st.button("ANALISAR VELA"):
                st.session_state.historico.insert(0, {"Valor": vela, "Jogo": "AV"})
                st.rerun()

    with c_prev:
        st.subheader("🔮 Sinal da IA")
        if st.session_state.historico:
            st.markdown('<div class="card-sinal-95">', unsafe_allow_html=True)
            ult = st.session_state.historico[0]
            
            if jogo_ativo == "Aviator":
                velas = [h['Valor'] for h in st.session_state.historico if h['Jogo'] == "AV"]
                if sum(1 for v in velas[:3] if v < 2.0) == 3:
                    st.error("❌ MERCADO EM RECOLHIMENTO")
                else:
                    st.write("🎯 ENTRADA CONFIRMADA: 1.50x"); play_sound()
            
            elif jogo_ativo == "Roleta":
                st.write(f"🎯 COBRIR NÚMERO {ult['Numero']} E VIZINHOS:"); st.write(ult['vizinhos']); play_sound()
            
            elif jogo_ativo in ["Dragon Tiger", "Bac Bo"]:
                p_atual = ult.get("Padrao")
                matches = [h for h in st.session_state.historico[1:] if h.get("Padrao") == p_atual]
                if matches:
                    venc_f = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
                    st.write(f"🎯 ENTRAR NO {venc_f.upper()}"); play_sound()
                else:
                    st.write("⏳ AGUARDANDO REPETIÇÃO DE PADRÃO")
            
            st.write(f"Aposta: R$ {entrada_v:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🕒 Histórico Recente")
if st.session_state.historico:
    cols = st.columns(10)
    for i, h in enumerate([x for x in st.session_state.historico if x['Jogo'] == ("AV" if jogo_ativo == "Aviator" else "DT" if jogo_ativo == "Dragon Tiger" else "BB" if jogo_ativo == "Bac Bo" else "ROL")][:10]):
        if jogo_ativo == "Aviator":
            v = h['Valor']; cl = "vela-rosa" if v >= 10 else "vela-media" if v >= 2 else "vela-baixa"
            cols[i].markdown(f"<div class='vela-box {cl}'>{v}x</div>", unsafe_allow_html=True)
        else:
            v = h.get("Vencedor", h.get("Numero"))
            cols[i].write(f"**{v}**")
