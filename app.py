import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IA Analisadora Pro", layout="wide")

# Estilos CSS para o Alerta Piscante
st.markdown("""
<style>
@keyframes blinker {
    50% { opacity: 0; }
}
.flash-button {
    background-color: #ff4b4b;
    color: white;
    padding: 15px;
    text-align: center;
    font-weight: bold;
    border-radius: 10px;
    animation: blinker 1s linear infinite;
    font-size: 20px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Inicialização da memória
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'acertos' not in st.session_state:
    st.session_state.acertos = 0
if 'erros' not in st.session_state:
    st.session_state.erros = 0

def categorizar(valor):
    if valor in ['J', 'Q', 'K', 'A']: 
        return "Letra"
    v = int(valor)
    if 1 <= v <= 6: return "Baixo"
    if 7 <= v <= 8: return "Neutro"
    if 9 <= v <= 10: return "Alto"
    return "Outro"

def determinar_vencedor(v_az, v_ver):
    pesos = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    n_az = pesos.get(v_az, int(v_az) if v_az.isdigit() else 0)
    n_ver = pesos.get(v_ver, int(v_ver) if v_ver.isdigit() else 0)

    if n_az > n_ver: return "Azul"
    if n_ver > n_az: return "Vermelho"
    return "Empate"

st.title("🚀 IA Pro: Filtro 80% & Notificação")

# --- ÁREA DE ENTRADA ---
col1, col2 = st.columns(2)
opcoes = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']

with col1:
    val_az = st.selectbox("Lado Azul", opcoes)
with col2:
    val_ver = st.selectbox("Lado Vermelho", opcoes)

if st.button("REGISTRAR RODADA", use_container_width=True):
    cat_az = categorizar(val_az)
    cat_ver = categorizar(val_ver)
    venc = determinar_vencedor(val_az, val_ver)

    nova_rodada = {
        "Azul": f"{val_az} ({cat_az})",
        "Vermelho": f"{val_ver} ({cat_ver})",
        "Resultado": venc,
        "Padrao": f"{cat_az}x{cat_ver}"
    }
    st.session_state.historico.insert(0, nova_rodada)
    st.rerun()

st.divider()

# --- LÓGICA DE INTELIGÊNCIA ---
if len(st.session_state.historico) >= 5:
    ult_p = st.session_state.historico[0]["Padrao"]
    ocorrencias = []

    for i in range(1, len(st.session_state.historico) - 1):
        if st.session_state.historico[i+1]["Padrao"] == ult_p:
            ocorrencias.append(st.session_state.historico[i]["Resultado"])

    if ocorrencias:
        total = len(ocorrencias)
        contagem = {v: ocorrencias.count(v) for v in set(ocorrencias)}
        vencedor_frequente = max(contagem, key=contagem.get)
        porcentagem = (contagem[vencedor_frequente] / total) * 100

        if porcentagem >= 80 and vencedor_frequente != "Empate":
            st.markdown(f'<div class="flash-button">🔥 OPORTUNIDADE: ENTRAR NO {vencedor_frequente.upper()} 🔥</div>', unsafe_allow_html=True)
            st.balloons()

            st.write(f"### Confiança Estatística: {porcentagem:.1f}%")
            st.write(f"Baseado em {total} repetições deste padrão.")

            c1, c2 = st.columns(2)
            if c1.button("✅ ACERTEI"):
                st.session_state.acertos += 1
                st.rerun()
            if c2.button("❌ ERREI"):
                st.session_state.erros += 1
                st.rerun()
        else:
            st.info(f"Análise: Padrão '{ult_p}' favorece {vencedor_frequente} ({porcentagem:.1f}%). Aguardando > 80%.")
    else:
        st.info("Padrão novo detectado. Coletando dados...")
else:
    st.info("Aguardando base de dados (mínimo 5 rodadas)...")

# --- DASHBOARD LATERAL (SEM PLOTLY) ---
st.sidebar.title("📊 Performance")
total_paps = st.session_state.acertos + st.session_state.erros

if total_paps > 0:
    winrate = (st.session_state.acertos / total_paps) * 100
    st.sidebar.metric("Taxa de Assertividade", f"{winrate:.1f}%")
    
    # Gráfico de Barras Nativo
    chart_data = pd.DataFrame({
        "Quantidade": [st.session_state.acertos, st.session_state.erros]
    }, index=["Acertos", "Erros"])
    st.sidebar.bar_chart(chart_data)

if st.sidebar.button("Limpar Histórico"):
    st.session_state.historico = []
    st.session_state.acertos = 0
    st.session_state.erros = 0
    st.rerun()

# --- TABELA ---
if st.session_state.historico:
    st.subheader("📜 Histórico Recente")
    st.table(pd.DataFrame(st.session_state.historico).head(10))
