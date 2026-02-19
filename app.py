import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração e Estética Premium
st.set_page_config(page_title="IA ANALYZER - MODO HÍBRIDO", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .card-oportunidade { 
        background: linear-gradient(135deg, #065f46 0%, #022c22 100%); 
        padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #10b981;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    .stats-box { background-color: #161b22; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 8px; }
    .carta-visual { display: inline-block; background: white; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #3b82f6; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Memória
if 'historico' not in st.session_state: st.session_state.historico = []
if 'banca_atual' not in st.session_state: st.session_state.banca_atual = 1000.0
if 'logs_banca' not in st.session_state: st.session_state.logs_banca = [1000.0]
if 'performance_padroes' not in st.session_state: st.session_state.performance_padroes = {}

# --- Funções de Lógica ---
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
    return "Azul" if n_az > n_ver else "Vermelho" if n_ver > n_az else "Empate"

def processar_vitoria_automatica(novo_vencedor):
    if len(st.session_state.historico) < 1: return
    
    # Verifica a previsão deixada na última rodada registada
    ultima_rodada = st.session_state.historico[0]
    
    if "previsao_ia" in ultima_rodada:
        sugestao = ultima_rodada["previsao_ia"]
        padrao = ultima_rodada["Padrao"]
        
        if padrao not in st.session_state.performance_padroes:
            st.session_state.performance_padroes[padrao] = {"win": 0, "loss": 0}
        
        valor_aposta = st.session_state.banca_atual * 0.01 # Gestão de 1%

        if novo_vencedor == sugestao:
            st.session_state.performance_padroes[padrao]["win"] += 1
            st.session_state.banca_atual += valor_aposta
            st.toast(f"✅ GREEN AUTOMÁTICO! (+R${valor_aposta:.2f})", icon="💰")
        elif novo_vencedor != "Empate":
            st.session_state.performance_padroes[padrao]["loss"] += 1
            st.session_state.banca_atual -= valor_aposta
            st.toast(f"❌ LOSS DETECTADO! (-R${valor_aposta:.2f})", icon="📉")
        
        st.session_state.logs_banca.append(st.session_state.banca_atual)

# --- Layout Superior ---
st.title("🛡️ IA ANALYZER: REGISTO MANUAL INTELIGENTE")

col_input, col_pred = st.columns([1, 1.5])

with col_input:
    st.subheader("📥 Abastecer Resultados")
    opcoes = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
    
    c1, c2 = st.columns(2)
    val_az = c1.selectbox("Lado Azul", opcoes)
    val_ver = c2.selectbox("Lado Vermelho", opcoes)
    
    if st.button("REGISTAR RODADA", use_container_width=True):
        venc_atual = determinar_vencedor(val_az, val_ver)
        
        # 1. Valida automaticamente se a previsão anterior bateu com este novo dado
        processar_vitoria_automatica(venc_atual)
        
        # 2. Cria a nova rodada
        padrao_atual = f"{categorizar(val_az)}x{categorizar(val_ver)}"
        nova_rodada = {
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Azul": val_az, "Vermelho": val_ver,
            "Vencedor": venc_atual,
            "Padrao": padrao_atual
        }
        
        # 3. Gera a previsão para a PRÓXIMA rodada (Backtest em tempo real)
        matches = [h for h in st.session_state.historico if h["Padrao"] == padrao_atual]
        if matches:
            venc_frequente = max(set([m["Vencedor"] for m in matches]), key=[m["Vencedor"] for m in matches].count)
            nova_rodada["previsao_ia"] = venc_frequente
            
        st.session_state.historico.insert(0, nova_rodada)
        st.rerun()

with col_pred:
    st.subheader("🔮 Previsão para a Próxima")
    if st.session_state.historico:
        ult = st.session_state.historico[0]
        if "previsao_ia" in ult:
            st.markdown(f"""
                <div class="card-oportunidade">
                    <p style='margin:0; font-size: 14px; opacity: 0.8;'>Padrão Detetado: {ult['Padrao']}</p>
                    <h1 style='margin: 10px 0; font-size: 45px; color: #10b981;'>{ult['previsao_ia'].upper()}</h1>
                    <p style='margin:0;'>Entre na cor acima agora!</p>
                    <small style='opacity: 0.6;'>A validação do Green será automática ao registar o próximo resultado.</small>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("A aguardar repetição de padrão para gerar palpite...")
    else:
        st.info("Registe a primeira rodada para iniciar a análise.")

st.divider()

# --- Gráficos e Tabelas ---
col_graf, col_perf = st.columns([2, 1])

with col_graf:
    st.subheader("📈 Evolução da Banca (R$)")
    st.line_chart(st.session_state.logs_banca)

with col_perf:
    st.subheader("📊 Eficiência por Padrão")
    if st.session_state.performance_padroes:
        items = []
        for p, s in st.session_state.performance_padroes.items():
            total = s['win'] + s['loss']
            winrate = (s['win'] / total * 100) if total > 0 else 0
            items.append({"Padrão": p, "✅": s['win'], "❌": s['loss'], "%": f"{winrate:.0f}%"})
        st.table(pd.DataFrame(items))

# --- Histórico ---
st.subheader("📜 Log de Atividade")
if st.session_state.historico:
    for h in st.session_state.historico[:5]:
        st.markdown(f"""
        <div class="stats-box">
            {h['Hora']} | Azul: <span class="carta-visual">{h['Azul']}</span> Vermelho: <span class="carta-visual">{h['Vermelho']}</span> | 
            <b>Vencedor: {h['Vencedor']}</b> | Padrão: {h['Padrao']}
        </div>
        """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Painel de Controlo")
    st.metric("Saldo Disponível", f"R$ {st.session_state.banca_atual:.2f}")
    st.divider()
    if st.button("LIMPAR TUDO"):
        st.session_state.clear()
        st.rerun()
