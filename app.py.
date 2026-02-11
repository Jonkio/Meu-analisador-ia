import streamlit as st
import pandas as pd

# Configuração visual da página
st.set_page_config(page_title="IA Analisadora de Padrões", layout="wide")

# Estilização para as cores ficarem vivas
st.markdown("""
<style>
.azul { color: #3498db; font-weight: bold; }
.vermelho { color: #e74c3c; font-weight: bold; }
.neutro { color: #95a5a6; font-weight: bold; }
.letra { color: #f1c40f; font-weight: bold; }
</style>
""", unsafe_allow_stdio=True)

# Inicialização da memória do sistema
if 'historico' not in st.session_state:
st.session_state.historico = []
if 'acertos' not in st.session_state:
st.session_state.acertos = 0
if 'erros' not in st.session_state:
st.session_state.erros = 0

def categorizar(valor):
if valor in ['J', 'Q', 'K']: return "Letra"
v = int(valor)
if 1 <= v <= 6: return "Baixo"
if 7 <= v <= 8: return "Neutro"
if 9 <= v <= 10: return "Alto"

def determinar_vencedor(v_az, v_ver):
# Converte letras para valores numéricos para comparar quem é maior
pesos = {'J': 11, 'Q': 12, 'K': 13}
n_az = pesos.get(v_az, int(v_az) if v_az.isdigit() else 0)
n_ver = pesos.get(v_ver, int(v_ver) if v_ver.isdigit() else 0)

if n_az > n_ver: return "Azul"
if n_ver > n_az: return "Vermelho"
return "Empate"

# --- INTERFACE ---
st.title("🧠 IA de Análise Numérica e Sequencial")

col1, col2 = st.columns(2)

with col1:
st.subheader("🔵 Entrada Azul")
opcoes = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K']
val_az = st.selectbox("Selecione o valor Azul", opcoes, key="sel_az")

with col2:
st.subheader("🔴 Entrada Vermelho")
val_ver = st.selectbox("Selecione o valor Vermelho", opcoes, key="sel_ver")

if st.button("REGISTRAR RESULTADO E ANALISAR", use_container_width=True):
cat_az = categorizar(val_az)
cat_ver = categorizar(val_ver)
vencedor = determinar_vencedor(val_az, val_ver)

nova_rodada = {
"Comparativo": f"{val_az} ({cat_az}) x {val_ver} ({cat_ver})",
"Vencedor": vencedor,
"Padrao_Codificado": f"{cat_az}-{cat_ver}"
}

# Adiciona ao início da lista para aparecer primeiro
st.session_state.historico.insert(0, nova_rodada)

# --- LÓGICA DE APRENDIZADO (PALPITE) ---
st.divider()
if len(st.session_state.historico) >= 2:
# Pega o padrão que acabou de sair
ultimo_padrao = st.session_state.historico[0]["Padrao_Codificado"]

# Procura no histórico anterior se esse padrão já aconteceu
sugestao = None
for i in range(1, len(st.session_state.historico) - 1):
if st.session_state.historico[i+1]["Padrao_Codificado"] == ultimo_padrao:
sugestao = st.session_state.historico[i]["Vencedor"]
break

st.subheader("🔮 Palpite para a Próxima Rodada")
if sugestao:
st.warning(f"Baseado no histórico, quando sai '{ultimo_padrao}', a tendência seguinte é: **{sugestao}**")

c1, c2 = st.columns(2)
if c1.button("✅ O palpite ACERTOU"):
st.session_state.acertos += 1
st.rerun()
if c2.button("❌ O palpite ERROU"):
st.session_state.erros += 1
st.rerun()
else:
st.info("Aguardando repetição de padrão para gerar palpite...")

# --- DASHBOARD LATERAL ---
st.sidebar.title("📈 Performance da IA")
st.sidebar.metric("Acertos", st.session_state.acertos)
st.sidebar.metric("Erros", st.session_state.erros)

if st.sidebar.button("Limpar Histórico"):
st.session_state.historico = []
st.session_state.acertos = 0
st.session_state.erros = 0
st.rerun()

# --- TABELA DE DADOS ---
st.subheader("📋 Histórico de Entradas")
if st.session_state.historico:
df = pd.DataFrame(st.session_state.historico)
st.table(df[["Comparativo", "Vencedor"]])
