import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração e Estética
st.set_page_config(page_title="IA ANALYZER - RISK CONTROL PRO", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0b0e14; color: #ffffff; }
    .card-alerta { 
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); 
        padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #6366f1;
    }
    .card-stop {
        background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%);
        padding: 30px; border-radius: 20px; text-align: center; border: 3px solid #f87171;
        margin: 20px 0;
    }
    .bola { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .azul { background-color: #3b82f6; }
    .vermelho { background-color: #ef4444; }
    .amarelo { background-color: #facc15; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória
if 'historico' not in st.session_state: st.session_state.historico = []
if 'banca_atual' not in st.session_state: st.session_state.banca_atual = 1000.0
if 'logs_banca' not in st.session_state: st.session_state.logs_banca = [1000.0]
if 'aguardando_gale' not in st.session_state: st.session_state.aguardando_gale = False
if 'greens_dia' not in st.session_state: st.session_state.greens_dia = 0
if 'reds_dia' not in st.session_state: st.session_state.reds_dia = 0
if 'stats_horario' not in st.session_state: 
    st.session_state.stats_horario = {"Madrugada": 0, "Manhã": 0, "Tarde": 0, "Noite": 0}

# --- Lógica de Horário ---
def obter_turno():
    hora = datetime.now().hour
    if 0 <= hora < 6: return "Madrugada"
    if 6 <= hora < 12: return "Manhã"
    if 12 <= hora < 18: return "Tarde"
    return "Noite"

# --- Lógica do Stop ---
STOP_LIMIT = 5
is_stopped = st.session_state.greens_dia >= STOP_LIMIT or st.session_state.reds_dia >= STOP_LIMIT

# --- Funções Base ---
def determinar_vencedor(v_az, v_ver):
    pesos = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    n_az = pesos.get(v_az, int(v_az) if v_az.isdigit() else 0)
    n_ver = pesos.get(v_ver, int(v_ver) if v_ver.isdigit() else 0)
    if n_az > n_ver: return "Azul"
    if n_ver > n_az: return "Vermelho"
    return "Empate"

def categorizar(v):
    if v in ['J', 'Q', 'K', 'A']: return "L"
    try:
        v = int(v)
        return "B" if 1 <= v <= 6 else "N" if 7 <= v <= 8 else "A"
    except: return "N"

# --- Interface Sidebar ---
with st.sidebar:
    st.header("⚙️ Gestão & Performance")
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual), step=10.0)
    
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Greens", f"{st.session_state.greens_dia}/{STOP_LIMIT}")
    col_s2.metric("Reds (G1=2x)", f"{st.session_state.reds_dia}/{STOP_LIMIT}")
    
    st.divider()
    st.subheader("📊 Assertividade por Turno")
    df_turnos = pd.DataFrame(list(st.session_state.stats_horario.items()), columns=['Turno', 'Greens'])
    st.bar_chart(df_turnos.set_index('Turno'))
    
    st.divider()
    if st.button("LIMPAR TUDO / NOVO CICLO"):
        st.session_state.clear()
        st.rerun()

# --- Painel Principal ---
st.title("🛡️ IA ANALYZER - RISK CONTROL PRO")

if is_stopped:
    # Correção do SyntaxError
    tipo_stop = "META DE GREENS BATIDA! 🎉" if st.session_state.greens_dia >= STOP_LIMIT else "LIMITE DE REDS ATINGIDO! 🛡️"
    st.markdown(f"""
        <div class="card-stop">
            <h1>🚫 OPERAÇÕES BLOQUEADAS</h1>
            <h2>{tipo_stop}</h2>
            <p>Limite diário atingido. Preserve sua banca.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    c1, c2 = st.columns([1, 1.5])

    with c1:
        st.subheader("📥 Registro")
        cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
        az = st.selectbox("Azul", cartas, key="sel_az")
        ver = st.selectbox("Vermelho", cartas, key="sel_ver")
        
        entrada_base = st.session_state.banca_atual * 0.15
        
        if st.button("PROCESSAR RESULTADO", use_container_width=True):
            venc = determinar_vencedor(az, ver)
            turno_atual = obter_turno()
            
            if st.session_state.historico and "previsao" in st.session_state.historico[0]:
                prev = st.session_state.historico[0]["previsao"]
                
                if venc == prev:
                    st.session_state.banca_atual += entrada_base * (2.15 if st.session_state.aguardando_gale else 1)
                    st.session_state.greens_dia += 1
                    st.session_state.stats_horario[turno_atual] += 1
                    st.session_state.aguardando_gale = False
                elif venc != "Empate":
                    if not st.session_state.aguardando_gale:
                        st.session_state.aguardando_gale = True
                    else:
                        st.session_state.banca_atual -= entrada_base * 3
                        st.session_state.reds_dia += 2 # Loss no Gale 1 contabiliza como 2 perdas
                        st.session_state.aguardando_gale = False
                st.session_state.logs_banca.append(st.session_state.banca_atual)

            padrao_num = f"{categorizar(az)}x{categorizar(ver)}"
            nova_rodada = {
                "Hora": datetime.now().strftime("%H:%M"), 
                "Vencedor": venc, 
                "Padrao": padrao_num, 
                "Turno": turno_atual
            }
            
            # Busca de Padrão
            matches = [h for h in st.session_state.historico if h['Padrao'] == padrao_num]
            if matches:
                nova_rodada["previsao"] = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)

            st.session_state.historico.insert(0, nova_rodada)
            st.rerun()

    with c2:
        st.subheader("🔮 Próxima Entrada")
        if st.session_state.historico:
            ult = st.session_state.historico[0]
            if "previsao" in ult:
                tipo = "⚠️ GALE 1" if st.session_state.aguardando_gale else "🎯 ENTRADA"
                st.markdown(f"""
                    <div class="card-alerta">
                        <small>{tipo}</small>
                        <h1 style='font-size: 65px;'>{ult['previsao'].upper()}</h1>
                        <p>Valor Sugerido: <b>R$ {entrada_base * (2 if st.session_state.aguardando_gale else 1):.2f}</b></p>
                    </div>
                """, unsafe_allow_html=True)

st.divider()

# Histórico e Relatórios - Correção do KeyError
if st.session_state.historico:
    st.write("### 🕒 Fluxo de Tendência")
    bolinhas = ""
    for h in st.session_state.historico[:18]:
        # Suporte ao padrão amarelo como empate
        c = "azul" if h['Vencedor'] == "Azul" else "vermelho" if h['Vencedor'] == "Vermelho" else "amarelo"
        bolinhas += f'<span class="bola {c}"></span>'
    st.markdown(bolinhas, unsafe_allow_html=True)
    
    with st.expander("Ver Detalhes"):
        df_hist = pd.DataFrame(st.session_state.historico).head(15)
        # Verifica se colunas existem antes de filtrar para evitar erro
        colunas_desejadas = ["Hora", "Vencedor", "Padrao"]
        colunas_existentes = [col for col in colunas_desejadas if col in df_hist.columns]
        st.table(df_hist[colunas_existentes])
