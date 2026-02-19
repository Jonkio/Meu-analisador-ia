import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração de Layout
st.set_page_config(page_title="IA ANALYZER - MODO GALE PRO", layout="wide")

# Estilos CSS Otimizados
st.markdown("""
<style>
    .main { background-color: #0b0e14; color: #ffffff; }
    .card-alerta { 
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); 
        padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #6366f1;
    }
    .card-gale { 
        background: linear-gradient(135deg, #422006 0%, #78350f 100%); 
        padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #f59e0b;
        margin-top: 10px;
    }
    .metric-box { background-color: #161b22; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# Inicialização de Memória
if 'historico' not in st.session_state: st.session_state.historico = []
if 'banca_atual' not in st.session_state: st.session_state.banca_atual = 1000.0
if 'assertividade_recente' not in st.session_state: st.session_state.assertividade_recente = []
if 'aguardando_gale' not in st.session_state: st.session_state.aguardando_gale = False

# --- Funções Auxiliares ---
def determinar_vencedor(v_az, v_ver):
    pesos = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    n_az = pesos.get(v_az, int(v_az) if v_az.isdigit() else 0)
    n_ver = pesos.get(v_ver, int(v_ver) if v_ver.isdigit() else 0)
    return "Azul" if n_az > n_ver else "Vermelho" if n_ver > n_az else "Empate"

def categorizar(v):
    if v in ['J', 'Q', 'K', 'A']: return "L"
    v = int(v)
    return "B" if 1 <= v <= 6 else "N" if 7 <= v <= 8 else "A"

# --- ALGORITMO COM MONITOR DE GALE ---
def analisar_gale(padrao_alvo, sugestao, historico):
    if len(historico) < 15: return 0
    
    sucessos_gale = 0
    total_ocorrencias = 0
    
    for i in range(1, len(historico) - 2):
        # Se achamos o padrão no passado
        if historico[i+1]['Padrao'] == padrao_alvo:
            total_ocorrencias += 1
            # Se a primeira falhou (i), verificamos a próxima (i-1)
            if historico[i]['Vencedor'] != sugestao and historico[i]['Vencedor'] != "Empate":
                if historico[i-1]['Vencedor'] == sugestao:
                    sucessos_gale += 1
                    
    return (sucessos_gale / total_ocorrencias * 100) if total_ocorrencias > 0 else 0

# --- Interface ---
with st.sidebar:
    st.header("📊 Gestão Pro")
    recente = st.session_state.assertividade_recente[-5:]
    win_count = recente.count("W")
    status = "Favorável" if win_count >= 3 else "Instável"
    st.markdown(f"Ciclo: **{status}**")
    
    st.divider()
    st.session_state.banca_atual = st.number_input("Saldo (R$)", value=float(st.session_state.banca_atual))
    entrada = st.session_state.banca_atual * 0.15
    st.write(f"Entrada Atual: **R$ {entrada:.2f}**")
    if st.session_state.aguardando_gale:
        st.warning(f"Próximo Gale: **R$ {entrada * 2:.2f}**")

st.title("🛡️ IA ANALYZER - GALE RECOVERY")

c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("📥 Registro")
    cartas = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K', 'A']
    az = st.selectbox("Azul", cartas)
    ver = st.selectbox("Vermelho", cartas)
    
    if st.button("PROCESSAR JOGO", use_container_width=True):
        venc = determinar_vencedor(az, ver)
        
        # Lógica Automática de Win/Loss/Gale
        if st.session_state.historico and "previsao" in st.session_state.historico[0]:
            prev = st.session_state.historico[0]["previsao"]
            
            if venc == prev:
                st.session_state.assertividade_recente.append("W")
                mult = 2.15 if st.session_state.aguardando_gale else 1.15 # Recupera o anterior
                st.session_state.banca_atual *= mult 
                st.session_state.aguardando_gale = False
                st.success("GREEN!")
            elif venc == "Empate":
                st.info("EMPATE - Rodada Anulada")
            else:
                if not st.session_state.aguardando_gale:
                    st.session_state.aguardando_gale = True
                    st.warning("LOSS - Preparar Gale")
                else:
                    st.session_state.assertividade_recente.append("L")
                    st.session_state.banca_atual -= (entrada * 3) # Perda total do ciclo
                    st.session_state.aguardando_gale = False
                    st.error("LOSS TOTAL")
        
        padrao = f"{categorizar(az)}x{categorizar(ver)}"
        nova_rodada = {"Vencedor": venc, "Padrao": padrao, "Hora": datetime.now().strftime("%H:%M")}
        
        # Inteligência de Previsão
        matches = [h for h in st.session_state.historico if h['Padrao'] == padrao]
        if matches and len(matches) >= 3:
            sugestao = max(set([o['Vencedor'] for o in matches]), key=[o['Vencedor'] for o in matches].count)
            winrate = ([o['Vencedor'] for o in matches].count(sugestao) / len(matches)) * 100
            
            if winrate >= 75:
                nova_rodada["previsao"] = sugestao
                nova_rodada["conf"] = winrate
                nova_rodada["gale_rate"] = analisar_gale(padrao, sugestao, st.session_state.historico)

        st.session_state.historico.insert(0, nova_rodada)
        st.rerun()

with c2:
    if st.session_state.historico:
        ult = st.session_state.historico[0]
        
        if st.session_state.aguardando_gale:
            st.markdown(f"""
                <div class="card-gale">
                    <h2 style='margin:0;'>⚠️ RECUPERAÇÃO (GALE 1)</h2>
                    <h1 style='font-size: 50px; margin: 10px 0;'>{ult['previsao'].upper()}</h1>
                    <p>Taxa Histórica de Recuperação: <b>{ult.get('gale_rate', 0):.1f}%</b></p>
                    <p>Aposte: R$ {entrada * 2:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        elif "previsao" in ult:
            st.markdown(f"""
                <div class="card-alerta">
                    <h2 style='margin:0; color: #818cf8;'>ENTRADA SUGERIDA</h2>
                    <h1 style='font-size: 60px; margin: 10px 0;'>{ult['previsao'].upper()}</h1>
                    <p>Confiança Direta: <b>{ult['conf']:.1f}%</b></p>
                    <p>Amostragem: {len([h for h in st.session_state.historico if h['Padrao'] == ult['Padrao']])} jogos</p>
                </div>
            """, unsafe_allow_html=True)

st.divider()
st.write("### 🕒 Histórico de Rodadas")
st.table(pd.DataFrame(st.session_state.historico[:5])[["Hora", "Vencedor", "Padrao"]])
