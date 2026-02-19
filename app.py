import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração e Estética de Alto Contraste
st.set_page_config(page_title="IA ANALYZER - VISIBILIDADE PRO", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; color: #212529; }
    /* Card de Alerta com Fonte Clara para fácil leitura */
    .card-alerta { 
        background-color: #ffffff; 
        padding: 30px; 
        border-radius: 15px; 
        text-align: center; 
        border: 2px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .texto-azul { color: #0d6efd; font-weight: bold; }
    .texto-vermelho { color: #dc3545; font-weight: bold; }
    .texto-amarelo { color: #ffc107; font-weight: bold; }
    
    /* Estilo das Cartas no Fluxo */
    .carta-box {
        display: inline-block;
        background: white;
        color: #333;
        padding: 5px 12px;
        border-radius: 6px;
        border: 2px solid #333;
        font-weight: bold;
        margin-right: 10px;
        box-shadow: 2px 2px 0px #000;
    }
    .bola { height: 15px; width: 15px; border-radius: 50%; display: inline-block; margin-right: 5px; vertical-align: middle; }
    .azul { background-color: #0d6efd; }
    .vermelho { background-color: #dc3545; }
    .amarelo { background-color: #ffc107; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória
if 'historico' not in st.session_state: st.session_state.historico = []
if 'banca_atual' not in st.session_state: st.session_state.banca_atual = 1000.0
if 'logs_banca' not in st.session_state: st.session_state.logs_banca = [1000.0]
if 'aguardando_gale' not in st.session_state: st.session_state.aguardando_gale = False
if 'greens_dia' not in st.session_state: st.session_state.greens_dia = 0
if 'reds_dia' not in st.session_state: st.session_state.reds_dia = 0

# --- Funções Lógicas ---
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
        v_int = int(v)
        return "B" if 1 <= v_int <= 6 else "N" if 7 <= v_int <= 8 else "A"
    except: return "N"

# --- Lógica do Stop ---
STOP_LIMIT = 5
is_stopped = st.session_state.greens_dia >= STOP_LIMIT or st.session_state.reds_dia >= STOP_LIMIT

# --- Sidebar ---
with st.sidebar:
    st.header("💼 Gestão Financeira")
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual), step=10.0)
    
    c1, c2 = st.columns(2)
    c1.metric("Greens", f"{st.session_state.greens_dia}/{STOP_LIMIT}")
    c2.metric("Reds", f"{st.session_state.reds_dia}/{STOP_LIMIT}")
    
    st.divider()
    if st.button("LIMPAR TUDO / RESET"):
        st.session_state.clear()
        st.rerun()

# --- Painel Principal ---
st.title("🎯 IA ANALYZER - ALTA VISIBILIDADE")

if is_stopped:
    tipo_stop = "META ATINGIDA! 🎉" if st.session_state.greens_dia >= STOP_LIMIT else "LIMITE DE PERDA! 🛡️"
    st.warning(f"### {tipo_stop} \nSistema bloqueado para segurança da sua banca.")
else:
    col_reg, col_prev = st.columns([1, 1.5])

    with col_reg:
        st.subheader("📥 Registro de Dados")
        cartas_op = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
        az_val = st.selectbox("Lado Azul", cartas_op, key="az")
        ver_val = st.selectbox("Lado Vermelho", cartas_op, key="ver")
        
        entrada_val = st.session_state.banca_atual * 0.15
        
        if st.button("PROCESSAR RESULTADO", use_container_width=True):
            venc = determinar_vencedor(az_val, ver_val)
            
            # Validação Automática
            if st.session_state.historico and "previsao" in st.session_state.historico[0]:
                prev = st.session_state.historico[0]["previsao"]
                if venc == prev:
                    st.session_state.banca_atual += entrada_val * (2.15 if st.session_state.aguardando_gale else 1)
                    st.session_state.greens_dia += 1
                    st.session_state.aguardando_gale = False
                elif venc != "Empate":
                    if not st.session_state.aguardando_gale:
                        st.session_state.aguardando_gale = True
                    else:
                        st.session_state.banca_atual -= entrada_val * 3
                        st.session_state.reds_dia += 2 # Loss no Gale 1 conta como 2
                        st.session_state.aguardando_gale = False
                st.session_state.logs_banca.append(st.session_state.banca_atual)

            padrao_n = f"{categorizar(az_val)}x{categorizar(ver_val)}"
            st.session_state.historico.insert(0, {
                "Hora": datetime.now().strftime("%H:%M"),
                "Vencedor": venc,
                "Padrao": padrao_n,
                "Azul": az_val,
                "Vermelho": ver_val
            })
            
            # Gerar Previsão para a Próxima
            matches = [h for h in st.session_state.historico[1:] if h['Padrao'] == padrao_n]
            if matches:
                st.session_state.historico[0]["previsao"] = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
            
            st.rerun()

    with col_prev:
        st.subheader("🔮 Próxima Entrada")
        if st.session_state.historico:
            ult_h = st.session_state.historico[0]
            if "previsao" in ult_h:
                cor_txt = "texto-azul" if ult_h['previsao'] == "Azul" else "texto-vermelho"
                tipo_entrada = "⚠️ GALE 1" if st.session_state.aguardando_gale else "🎯 ENTRADA DIRETA"
                st.markdown(f"""
                    <div class="card-alerta">
                        <p style="color: #666; font-size: 18px;">{tipo_entrada}</p>
                        <h1 class="{cor_txt}" style="font-size: 80px; margin: 10px 0;">{ult_h['previsao'].upper()}</h1>
                        <p style="color: #333; font-size: 20px;">Valor: <b>R$ {entrada_val * (2 if st.session_state.aguardando_gale else 1):.2f}</b></p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Aguardando repetição de padrão histórico...")

st.divider()

# --- FLUXO DE TENDÊNCIA COM CARTAS VISUAIS ---
st.subheader("🕒 Fluxo de Tendência Recente")
if st.session_state.historico:
    for h in st.session_state.historico[:10]:
        cor_bola = "azul" if h['Vencedor'] == "Azul" else "vermelho" if h['Vencedor'] == "Vermelho" else "amarelo"
        st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <span class="bola {cor_bola}"></span>
                <span class="carta-box">{h['Azul']}</span> 
                <span style="font-weight: bold;">VS</span> 
                <span class="carta-box">{h['Vermelho']}</span> 
                <span style="margin-left: 20px; font-size: 14px; color: #666;">Padrão: {h['Padrao']} | {h['Hora']}</span>
            </div>
        """, unsafe_allow_html=True)
else:
    st.write("Registre dados para visualizar o fluxo.")

# Tabela Detalhada com proteção para KeyError
if len(st.session_state.historico) > 0:
    with st.expander("Ver Tabela de Dados Completa"):
        df_p = pd.DataFrame(st.session_state.historico)
        cols_val = [c for c in ["Hora", "Vencedor", "Padrao"] if c in df_p.columns]
        st.table(df_p[cols_val].head(10))
