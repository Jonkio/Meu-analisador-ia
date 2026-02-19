import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração e Estética
st.set_page_config(page_title="IA ANALYZER - ESTRATÉGIA CORES", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .card-oportunidade { 
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
        padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #3b82f6;
    }
    .bola { height: 15px; width: 15px; border-radius: 50%; display: inline-block; margin: 0 2px; }
    .azul { background-color: #3b82f6; }
    .vermelho { background-color: #ef4444; }
    .amarelo { background-color: #facc15; } /* EMPATE */
</style>
""", unsafe_allow_html=True)

# 2. Inicialização
if 'historico' not in st.session_state: st.session_state.historico = []
if 'banca_atual' not in st.session_state: st.session_state.banca_atual = 1000.0
if 'logs_banca' not in st.session_state: st.session_state.logs_banca = [1000.0]

def categorizar(valor):
    valor = str(valor).upper().strip()
    if valor in ['J', 'Q', 'K', 'A']: return "Letra"
    try:
        v = int(valor)
        if 1 <= v <= 6: return "Baixo"
        if 7 <= v <= 8: return "Neutro"
        if 9 <= v <= 10: return "Alto"
    except: pass
    return "Outro"

def determinar_vencedor(v_az, v_ver):
    pesos = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    get_val = lambda x: pesos.get(str(x).upper(), int(x) if str(x).isdigit() else 0)
    n_az, n_ver = get_val(v_az), get_val(v_ver)
    if n_az > n_ver: return "Azul"
    if n_ver > n_az: return "Vermelho"
    return "Empate"

# --- LÓGICA DOS PADRÕES DE CORES (DAS IMAGENS) ---
def analisar_padroes_cores(historico):
    if len(historico) < 6: return None
    
    # Pega as cores das últimas rodadas (do mais recente para o mais antigo)
    cores = [h['Vencedor'] for h in historico[:6]]
    
    # Exemplos de padrões das imagens enviadas:
    # Monitorando 3 Azuis + 1 Vermelho -> Sugere Vermelho (Padrão de repetição/quebra)
    if cores[:4] == ["Vermelho", "Azul", "Azul", "Azul"]: return "Vermelho"
    
    # Monitorando 4 Vermelhos + 1 Azul -> Sugere Azul
    if cores[:5] == ["Azul", "Vermelho", "Vermelho", "Vermelho", "Vermelho"]: return "Azul"
    
    # Monitorando Sequência de 5 iguais
    if cores[:5] == ["Azul"] * 5: return "Vermelho"
    if cores[:5] == ["Vermelho"] * 5: return "Azul"
    
    # Monitorando Amarelo (Empate) - Conforme sua solicitação
    if cores[0] == "Empate": return "Repetir última cor"

    return None

# --- PROCESSAMENTO ---
def processar_vitoria_automatica(novo_vencedor):
    if len(st.session_state.historico) < 1: return
    ult = st.session_state.historico[0]
    if "previsao_ia" in ult:
        valor_aposta = st.session_state.banca_atual * 0.15
        if novo_vencedor == ult["previsao_ia"]:
            st.session_state.banca_atual += valor_aposta
            st.toast("✅ GREEN AUTOMÁTICO!", icon="💰")
        elif novo_vencedor != "Empate":
            st.session_state.banca_atual -= valor_aposta
            st.toast("❌ LOSS DETECTADO", icon="📉")
        st.session_state.logs_banca.append(st.session_state.banca_atual)

# --- INTERFACE ---
with st.sidebar:
    st.header("💼 Gestão e Evolução")
    st.session_state.banca_atual = st.number_input("Saldo Atual (R$)", value=float(st.session_state.banca_atual), format="%.2f")
    st.metric("Entrada Sugerida (15%)", f"R$ {st.session_state.banca_atual * 0.15:.2f}")
    st.divider()
    st.line_chart(st.session_state.logs_banca)

st.title("🛡️ IA ANALYZER - MULTI-PADRÕES")

c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("📥 Registro")
    cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
    az = st.selectbox("Azul", cartas, key="az")
    ver = st.selectbox("Vermelho", cartas, key="ver")
    
    if st.button("REGISTRAR RODADA", use_container_width=True):
        venc = determinar_vencedor(az, ver)
        processar_vitoria_automatica(venc)
        
        padrao_num = f"{categorizar(az)}x{categorizar(ver)}"
        nova_rodada = {"Azul": az, "Vermelho": ver, "Vencedor": venc, "Padrao": padrao_num, "Hora": datetime.now().strftime("%H:%M")}
        
        # Previsão Híbrida (Cores + Números)
        prev_cor = analisar_padroes_cores([nova_rodada] + st.session_state.historico)
        if prev_cor:
            nova_rodada["previsao_ia"] = prev_cor
        else:
            # Fallback para padrão numérico
            matches = [h for h in st.session_state.historico if h["Padrao"] == padrao_num]
            if matches:
                nova_rodada["previsao_ia"] = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)

        st.session_state.historico.insert(0, nova_rodada)
        st.rerun()

with c2:
    st.subheader("🔮 Próxima Entrada")
    if st.session_state.historico:
        ult = st.session_state.historico[0]
        if "previsao_ia" in ult:
            st.markdown(f"""
                <div class="card-oportunidade">
                    <h3>ESTRATÉGIA COMBINADA DETECTADA</h3>
                    <h1 style='color: #10b981; font-size: 50px;'>{ult['previsao_ia'].upper()}</h1>
                    <p>Valor da Entrada: <b>R$ {st.session_state.banca_atual * 0.15:.2f}</b></p>
                </div>
            """, unsafe_allow_html=True)

st.divider()
st.subheader("📜 Histórico Visual (Cores e Padrões)")
for h in st.session_state.historico[:10]:
    cor_classe = "azul" if h['Vencedor'] == "Azul" else "vermelho" if h['Vencedor'] == "Vermelho" else "amarelo"
    st.markdown(f"""
        <div style='background:#1e293b; padding:10px; border-radius:10px; margin-bottom:5px;'>
            <span class="bola {cor_classe}"></span> <b>{h['Vencedor']}</b> | 
            Cartas: {h['Azul']} vs {h['Vermelho']} | 
            Padrão: {h['Padrao']} | {h['Hora']}
        </div>
    """, unsafe_allow_html=True)
