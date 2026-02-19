import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração de Layout e Estética de Alto Contraste
st.set_page_config(page_title="IA ANALYZER - SISTEMA MAGO PRO", layout="wide")

# Função de Som para Alertas
def play_sound():
    # Link de áudio externo para garantir funcionamento no navegador
    sound_file = "https://www.soundjay.com/buttons/button-3.mp3"
    st.markdown(f'<audio autoplay><source src="{sound_file}" type="audio/mp3"></audio>', unsafe_allow_html=True)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; color: #1e293b; }
    .card-sinal-critico { 
        background-color: #ffffff; padding: 25px; border-radius: 15px; text-align: center; 
        border: 4px solid #3b82f6; box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2); margin-bottom: 20px;
    }
    .carta-hist { 
        display: inline-block; background: #fff; color: #000; padding: 5px 12px; 
        border-radius: 6px; border: 2px solid #333; font-weight: bold; margin: 3px; 
        box-shadow: 2px 2px 0px #000;
    }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .azul { background-color: #2563eb; } .vermelho { background-color: #dc2626; } .amarelo { background-color: #fbbf24; }
    .vela-box { display: inline-block; padding: 10px; border-radius: 8px; font-weight: bold; margin: 4px; color: white; min-width: 65px; text-align: center; }
    .vela-baixa { background-color: #3b82f6; } .vela-media { background-color: #8b5cf6; } .vela-rosa { background-color: #ec4899; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização Segura de Memória
for key in ['historico', 'banca_atual', 'greens_dia', 'reds_dia', 'aguardando_gale', 'stats_horario']:
    if key not in st.session_state:
        if 'banca' in key: st.session_state[key] = 1000.0
        elif 'stats' in key: st.session_state[key] = {"Madrugada": 0, "Manhã": 0, "Tarde": 0, "Noite": 0}
        else: st.session_state[key] = [] if 'historico' in key else 0

# --- Lógicas de Apoio e Inteligência ---
def obter_turno():
    h = datetime.now().hour
    return "Madrugada" if 0<=h<6 else "Manhã" if 6<=h<12 else "Tarde" if 12<=h<18 else "Noite"

def calcular_confianca(jogo, padrao_atual):
    # Filtra o histórico pelo jogo ativo
    hist_jogo = [h for h in st.session_state.historico if h['Jogo'] == jogo]
    if len(hist_jogo) < 3: return 0, None
    
    # Busca repetições do padrão registrado
    matches = [h for h in hist_jogo[1:] if h.get("Padrao") == padrao_atual]
    if not matches: return 0, None
    
    # Identifica o vencedor mais frequente para esse padrão
    venc_f = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
    confianca = ([m["Vencedor"] for m in matches].count(venc_f) / len(matches)) * 100
    return confianca, venc_f

# --- Sidebar ---
with st.sidebar:
    st.header("🧙‍♂️ Gestão Estratégica")
    jogo_ativo = st.selectbox("Escolha o Jogo:", ["Dragon Tiger", "Aviator", "Bac Bo", "Roleta"])
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual))
    perc_entrada = st.slider("Mão (%)", 1, 30, 15) / 100
    stop_limit = st.number_input("Stop Win/Loss (Ciclos)", 1, 30, 5)
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Greens", st.session_state.greens_dia)
    c2.metric("Reds", st.session_state.reds_dia)
    
    if st.button("RESETAR SISTEMA"):
        st.session_state.clear(); st.rerun()

# Lógica de Stop e Valor de Entrada
is_stopped = st.session_state.greens_dia >= stop_limit or st.session_state.reds_dia >= stop_limit
entrada_v = st.session_state.banca_atual * perc_entrada

st.title(f"🚀 ANALYZER PRO - {jogo_ativo.upper()}")

if is_stopped:
    tipo_stop = "META ATINGIDA! 🎉" if st.session_state.greens_dia >= stop_limit else "STOP LOSS ATINGIDO! 🛡️"
    st.error(f"### 🛑 OPERAÇÕES BLOQUEADAS: {tipo_stop}")
else:
    c_reg, c_prev = st.columns([1, 1.3])

    with c_reg:
        st.subheader("📥 Registro de Dados")
        
        if jogo_ativo == "Dragon Tiger":
            cartas_op = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
            az = st.selectbox("Dragão", cartas_op, key="dt_az")
            ver = st.selectbox("Tigre", cartas_op, key="dt_ver")
            if st.button("PROCESSAR JOGO", use_container_width=True):
                p_map = {'J':11,'Q':12,'K':13,'A':14}
                n_az = p_map.get(az, int(az) if az.isdigit() else 0)
                n_ver = p_map.get(ver, int(ver) if ver.isdigit() else 0)
                venc = "Azul" if n_az > n_ver else "Vermelho" if n_ver > n_az else "Empate"
                
                # Validação de Ganhos
                if st.session_state.historico and "previsao" in st.session_state.historico[0]:
                    if venc == st.session_state.historico[0]["previsao"]:
                        st.session_state.greens_dia += 1; st.session_state.banca_atual += entrada_v
                        st.session_state.aguardando_gale = False
                    elif venc != "Empate":
                        if not st.session_state.aguardando_gale: st.session_state.aguardando_gale = True
                        else:
                            st.session_state.reds_dia += 2; st.session_state.banca_atual -= entrada_v * 3
                            st.session_state.aguardando_gale = False

                st.session_state.historico.insert(0, {
                    "Vencedor": venc, "Padrao": f"{az}x{ver}", "Az": az, "Ver": ver, 
                    "Jogo": "DT", "Hora": datetime.now().strftime("%H:%M")
                })
                st.rerun()

        elif jogo_ativo == "Aviator":
            v_v = st.number_input("Vela Atual:", 1.0, 1000.0, 1.5, key="av_v")
            if st.button("REGISTRAR VELA", use_container_width=True):
                st.session_state.historico.insert(0, {"Valor": v_v, "Jogo": "AV", "Vencedor": "Win" if v_v >= 1.5 else "Loss", "Padrao": "Scalp", "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

        elif jogo_ativo == "Bac Bo":
            s1 = st.number_input("Azul (Soma)", 2, 12, 7); s2 = st.number_input("Vermelho (Soma)", 2, 12, 7)
            if st.button("REGISTRAR DADOS", use_container_width=True):
                venc = "Azul" if s1 > s2 else "Vermelho" if s2 > s1 else "Empate"
                st.session_state.historico.insert(0, {"Vencedor": venc, "Padrao": f"S{s1}x{s2}", "Jogo": "BB", "Az": s1, "Ver": s2, "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

    with c_prev:
        st.subheader("🔮 Próxima Entrada")
        if st.session_state.historico:
            ult = st.session_state.historico[0]
            conf, sug = calcular_confianca(ult['Jogo'], ult.get('Padrao'))
            
            # FILTRO DE CRITICIDADE 85%
            if conf >= 85 and sug:
                tipo = "⚠️ GALE 1" if st.session_state.aguardando_gale else "🎯 ENTRADA DIRETA"
                cor_txt = "#2563eb" if sug == "Azul" else "#dc2626"
                st.markdown(f"""
                    <div class="card-sinal-critico">
                        <small>{tipo} - CRITICIDADE {conf:.0f}%</small>
                        <h1 style="color: {cor_txt}; font-size: 70px; margin: 0;">{str(sug).upper()}</h1>
                        <p style="font-size: 20px;">Apostar: R$ {entrada_v * (2 if st.session_state.aguardando_gale else 1):.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
                play_sound()
                # Armazena a previsão para validação na próxima rodada
                st.session_state.historico[0]["previsao"] = sug
            else:
                st.info("Aguardando confirmação de criticidade > 85% com base no volume de dados...")

st.divider()

# --- HISTÓRICO VISUAL COM CARTAS ---
st.subheader("🕒 Fluxo de Tendência Recente")

if st.session_state.historico:
    # Filtra histórico pelo jogo ativo para visualização correta
    hist_f = [h for h in st.session_state.historico if h['Jogo'] == ("AV" if jogo_ativo == "Aviator" else "DT" if jogo_ativo == "Dragon Tiger" else "BB" if jogo_ativo == "Bac Bo" else "ROL")][:10]
    
    for h in hist_f:
        if jogo_ativo in ["Dragon Tiger", "Bac Bo"]:
            cor_b = "azul" if h['Vencedor'] == "Azul" else "vermelho" if h['Vencedor'] == "Vermelho" else "amarelo"
            st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <span class="bola {cor_b}"></span>
                    <span class="carta-hist">{h.get('Az', '')}</span> 
                    <b>VS</b> 
                    <span class="carta-hist">{h.get('Ver', '')}</span> 
                    <small style="margin-left: 20px; color: #64748b;">{h.get('Hora', '')} | Vencedor: {h.get('Vencedor', '')}</small>
                </div>
            """, unsafe_allow_html=True)
        elif jogo_ativo == "Aviator":
            v = h.get('Valor', 0)
            cl = "vela-rosa" if v >= 10 else "vela-media" if v >= 2 else "vela-baixa"
            st.markdown(f"<div class='vela-box {cl}'>{v}x</div>", unsafe_allow_html=True)

# Tabela detalhada protegida contra KeyError (Imagem 4 resolvida)
if st.session_state.historico:
    with st.expander("Ver Tabela Técnica"):
        df = pd.DataFrame(st.session_state.historico).head(10)
        # Garantia de que as colunas existem antes de filtrar
        colunas_final = [c for c in ["Hora", "Vencedor", "Padrao", "Jogo"] if c in df.columns]
        st.table(df[colunas_final])
