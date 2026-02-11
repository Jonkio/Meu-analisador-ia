import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IA Analisadora", layout="wide")

# Inicialização da memória
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'acertos' not in st.session_state:
    st.session_state.acertos = 0
if 'erros' not in st.session_state:
    st.session_state.erros = 0

def categorizar(valor):
    if valor in ['J', 'Q', 'K']: 
        return "Letra"
    v = int(valor)
    if 1 <= v <= 6: 
        return "Baixo"
    if 7 <= v <= 8: 
        return "Neutro"
    if 9 <= v <= 10: 
        return "Alto"
    return "Desconhecido"

def determinar_vencedor(v_az, v_ver):
    pesos = {'J': 11, 'Q': 12, 'K': 13}
    # Converte para int se for dígito, senão usa o peso da letra ou 0
    n_az = pesos.get(v_az, int(v_az) if v_az.isdigit() else 0)
    n_ver = pesos.get(v_ver, int(v_ver) if v_ver.isdigit() else 0)
    
    if n_az > n_ver: 
        return "Azul"
    if n_ver > n_az: 
        return "Vermelho"
    return "Empate"

st.title("🧠 IA de Análise de Padrões")

# --- Interface de Entrada ---
col1, col2 = st.columns(2)
opcoes = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K']

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
        "Resultado": f"{venc} Venceu",
        "Padrao": f"{cat_az}x{cat_ver}"
    }
    st.session_state.historico.insert(0, nova_rodada)
    st.rerun() # Recarrega para atualizar a tabela e lógica

st.divider()

# --- Lógica de Palpite ---
if len(st.session_state.historico) >= 2:
    ult_p = st.session_state.historico[0]["Padrao"]
    sugestao = None
    
    # Busca no histórico se esse padrão já ocorreu antes
    for i in range(1, len(st.session_state.historico) - 1):
        if st.session_state.historico[i+1]["Padrao"] == ult_p:
            sugestao = st.session_state.historico[i]["Resultado"]
            break

    if sugestao:
        st.subheader(f"🔮 Sugestão baseada no padrão: {sugestao}")
        c1, c2 = st.columns(2)
        if c1.button("✅ Acertei"):
            st.session_state.acertos += 1
            st.rerun()
        if c2.button("❌ Errei"):
            st.session_state.erros += 1
            st.rerun()

# --- Painel Lateral e Exibição ---
st.sidebar.metric("Acertos", st.session_state.acertos)
st.sidebar.metric("Erros", st.session_state.erros)

if st.session_state.historico:
    st.write("### Histórico Recente")
    df = pd.DataFrame(st.session_state.historico)
    st.table(df[["Azul", "Vermelho", "Resultado"]])
