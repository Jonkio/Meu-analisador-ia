import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÃO E ESTILO
# ==========================================
st.set_page_config(page_title="IA ANALYZER - MODO AUTÔNOMO", layout="wide")

def apply_custom_css():
    st.markdown("""
    <style>
        .main { background-color: #0e1117; color: #ffffff; }
        .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
        .card-oportunidade { 
            background: linear-gradient(135deg, #065f46 0%, #064e3b 100%); 
            padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #10b981; 
        }
        .stats-box { 
            background-color: #161b22; padding: 10px; border-radius: 8px; 
            border-left: 4px solid #10b981; margin-bottom: 5px; 
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE NEGÓCIO (CORE)
# ==========================================

def get_card_value(val):
    """Converte o valor da carta para inteiro para comparação."""
    pesos = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    val_str = str(val).upper().strip()
    if val_str in pesos:
        return pesos[val_str]
    return int(val_str) if val_str.isdigit() else 0

def categorizar(valor):
    """Categoriza a carta conforme as faixas de valor."""
    valor_limpo = str(valor).upper().strip()
    if valor_limpo in ['J', 'Q', 'K', 'A']: return "Letra"
    try:
        v = int(valor_limpo)
        if 1 <= v <= 6: return "Baixo"
        if 7 <= v <= 8: return "Neutro"
        if 9 <= v <= 10: return "Alto"
    except ValueError:
        pass
    return "Outro"

def determinar_vencedor(v_az, v_ver):
    n_az = get_card_value(v_az)
    n_ver = get_card_value(v_ver)
    if n_az > n_ver: return "Azul"
    if n_ver > n_az: return "Vermelho"
    return "Empate"

def processar_vitoria_automatica(novo_vencedor):
    """Valida se a previsão anterior foi correta e atualiza a banca."""
    if len(st.session_state.historico) < 1:
        return

    # A previsão a ser validada está na última rodada inserida (índice 0)
    ultima_rodada = st.session_state.historico[0]
    
    if "previsao_ia" in ultima_rodada:
        sugestao = ultima_rodada["previsao_ia"]
        padrao = ultima_rodada["Padrao"]
        
        if padrao not in st.session_state.performance_padroes:
            st.session_state.performance_padroes[padrao] = {"win": 0, "loss": 0}
        
        valor_aposta = st.session_state.banca_atual * 0.01

        if novo_vencedor == sugestao:
            st.session_state.performance_padroes[padrao]["win"] += 1
            st.session_state.banca_atual += valor_aposta
            st.toast(f"✅ Green no padrão {padrao}!", icon="💰")
        elif novo_vencedor != "Empate":
            st.session_state.performance_padroes[padrao]["loss"] += 1
            st.session_state.banca_atual -= valor_aposta
            st.toast(f"❌ Loss no padrão {padrao}", icon="📉")
        
        st.session_state.logs_banca.append(st.session_state.banca_atual)

# ==========================================
# 3. INICIALIZAÇÃO DO ESTADO
# ==========================================
def init_session():
    defaults = {
        'historico': [],
        'banca_atual': 1000.0,
        'logs_banca': [1000.0],
        'performance_padroes': {}
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ==========================================
# 4. INTERFACE DO USUÁRIO (UI)
# ==========================================
def main():
    apply_custom_css()
    init_session()

    st.title("🛡️ IA ANALYZER: AUTO-TRACKING")

    col_in, col_pred = st.columns([1, 1.5])

    with col_in:
        st.subheader("📥 Abastecer Resultados")
        entrada = st.text_area("Cole os dados (Ex: 10 K 5 2)", height=100)
        
        if st.button("ATUALIZAR", use_container_width=True):
            dados = entrada.replace(',', ' ').split()
            
            # Processa em pares (Azul e Vermelho)
            for i in range(0, len(dados) - 1, 2):
                v_az, v_ver = dados[i], dados[i+1]
                venc_atual = determinar_vencedor(v_az, v_ver)
                
                # Valida previsão anterior antes de registrar a nova
                processar_vitoria_automatica(venc_atual)
                
                # Gera padrão e busca previsão
                padrao_nome = f"{categorizar(v_az)}x{categorizar(v_ver)}"
                
                # Busca tendência no histórico
                matches = [h for h in st.session_state.historico if h["Padrao"] == padrao_nome]
                previsao = None
                if matches:
                    vencedores = [m["Vencedor"] for m in matches if m["Vencedor"] != "Empate"]
                    if vencedores:
                        previsao = max(set(vencedores), key=vencedores.count)

                nova_rodada = {
                    "Hora": datetime.now().strftime("%H:%M"),
                    "Azul": v_az, "Vermelho": v_ver,
                    "Vencedor": venc_atual,
                    "Padrao": padrao_nome,
                    "previsao_ia": previsao
                }
                
                st.session_state.historico.insert(0, nova_rodada)
            st.rerun()

    with col_pred:
        if st.session_state.historico:
            ult = st.session_state.historico[0]
            if ult.get("previsao_ia"):
                st.markdown(f"""
                    <div class="card-oportunidade">
                        <h3>PRÓXIMA ENTRADA SUGERIDA</h3>
                        <h1 style='color: #10b981;'>{ult['previsao_ia'].upper()}</h1>
                        <p>Padrão Detectado: <b>{ult['Padrao']}</b></p>
                        <small>Aguardando resultado para validação...</small>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Padrão novo detectado. Aguardando mais dados para gerar previsão.")

    st.divider()

    # Dashboard de Performance
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Evolução da Banca")
        st.line_chart(st.session_state.logs_banca)
        
    with c2:
        st.subheader("📊 Ranking de Padrões")
        if st.session_state.performance_padroes:
            df_perf = pd.DataFrame([
                {"Padrão": p, "Win": s['win'], "Loss": s['loss']} 
                for p, s in st.session_state.performance_padroes.items()
            ])
            st.dataframe(df_perf, hide_index=True, use_container_width=True)

    # Sidebar lateral
    with st.sidebar:
        st.header("Configurações")
        st.metric("Saldo Atual", f"R$ {st.session_state.banca_atual:.2f}")
        if st.button("Limpar Histórico"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
