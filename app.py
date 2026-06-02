import streamlit as st

st.set_page_config(page_title="ÁPICE IA - MESTRE PREDICTOR", layout="wide")

st.markdown("""
<style>
    .main { background-color: #020617; color: white; }
    .stButton>button { height: 75px; border-radius: 15px; font-weight: bold; font-size: 20px; }
    
    /* Cores de Seleção Clássicas */
    .btn-home { background-color: #dc2626 !important; color: white !important; }
    .btn-away { background-color: #2563eb !important; color: white !important; }
    
    /* Histórico Horizontal Dinâmico */
    .history-ball { 
        display: inline-block; width: 38px; height: 38px; line-height: 38px; 
        border-radius: 50%; text-align: center; font-weight: bold; margin: 4px; 
        font-size: 15px; border: 2px solid rgba(255,255,255,0.1);
    }
    .ball-H { background-color: #dc2626; color: white; box-shadow: 0 0 10px #ef4444; }
    .ball-A { background-color: #2563eb; color: white; box-shadow: 0 0 10px #3b82f6; }
    .ball-D { background-color: #16a34a; color: white; }
    
    /* Alertas de Elite */
    .alert-master { background: linear-gradient(145px, #064e3b, #022c22); border: 2px solid #22c55e; padding: 25px; border-radius: 15px; text-align: center; }
    .alert-warning-master { background: linear-gradient(145px, #78350f, #451a03); border: 2px solid #f59e0b; padding: 25px; border-radius: 15px; text-align: center; }
    .danger-box { background: #4c0519; border: 2px solid #f43f5e; padding: 15px; border-radius: 12px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Inicialização de Variáveis de Estado Inteligentes
if 'selected_venc' not in st.session_state: st.session_state.selected_venc = None
if 'h_football' not in st.session_state: st.session_state.h_football = []

def confirmar_rodada():
    if st.session_state.selected_venc:
        st.session_state.h_football.insert(0, st.session_state.selected_venc)
        st.session_state.selected_venc = None
    else:
        st.error("Selecione o vencedor antes de apertar OK!")

# --- O MOTOR MESTRE DE PREDIÇÃO ---
def motor_mestre_analise():
    h = st.session_state.h_football
    # Filtra empates para não quebrar a análise de micro-tendências de cores
    fluxo = [x for x in h if x != "D"]
    
    if len(fluxo) < 3:
        return {"tipo": "AGUARDANDO", "msg": "Alimentando matriz de dados...", "sug": None, "conf": 0}
        
    s = "".join(fluxo[:6]) # Captura as últimas 6 rodadas puras
    
    # ⚠️ ANTICORRUPÇÃO / ALERTA DE MANIPULAÇÃO (Mesa em Super-Tendência Unilateral)
    if len(fluxo) >= 6 and (fluxo[:6] == ["H"]*6 or fluxo[:6] == ["A"]*6):
        return {"tipo": "PERIGO", "msg": "Mesa em fluxo de retenção unilateral severo. ALTA CHANCE DE MANIPULAÇÃO.", "sug": "ABORTAR", "conf": 0}

    # 1. PADRÃO TERMINATOR (Entrada Antecipada na 2ª e 3ª casa)
    if s.startswith("HH"): 
        return {"tipo": "SINAL", "msg": "Padrão Terminator: Força de reversão imediata calculada.", "sug": "🔵 FORA (AWAY)", "conf": 84}
    if s.startswith("AA"):
        return {"tipo": "SINAL", "msg": "Padrão Terminator: Força de reversão imediata calculada.", "sug": "🔴 CASA (HOME)", "conf": 84}

    # 2. PADRÃO GÊMEOS (Entrada em Duplas - AA -> H... a IA busca o segundo H)
    if s.startswith("HAA") or s.startswith("AHH"):
        proxima = "🔴 CASA (HOME)" if s.startswith("HAA") else "🔵 FORA (AWAY)"
        return {"tipo": "SINAL", "msg": "Padrão Gêmeos: Algoritmo tende a fechar a segunda perna do par.", "sug": proxima, "conf": 89}

    # 3. PADRÃO INTERMITÊNCIA EXTENSA (Xadrez de Bloco)
    if s.startswith("HHAAHH") or s.startswith("AAHHAA"):
        proxima = "🔵 FORA (AWAY)" if s.startswith("HHAAHH") else "🔴 CASA (HOME)"
        return {"tipo": "SINAL", "msg": "Xadrez de Blocos: Quebra cíclica detectada no espelhamento.", "sug": proxima, "conf : 92"}

    # 4. PADRÃO XADREZ TRADICIONAL COMPACTO
    if s.startswith("HA") or s.startswith("AH"):
        proxima = "🔴 CASA (HOME)" if s[0] == "A" else "🔵 FORA (AWAY)"
        return {"tipo": "SINAL", "msg": "Xadrez Padrão: Fluidez de mesa identificada.", "sug": proxima, "conf": 78}

    return {"tipo": "MISTO", "msg": "Mesa oscilando em mercado neutro. Aguardando assimetria estatística.", "sug": None, "conf": 0}

# --- INTERFACE ---
st.title("🎯 PORTAL ÁPICE IA - MESTRE PREDICTOR V6")

c_input, c_analise = st.columns([1.1, 1])

with c_input:
    st.subheader("📥 Input de Alta Precisão")
    
    # Grid de botões com feedback visual instantâneo
    c1, c2, c3 = st.columns(3)
    if c1.button("🔴 CASA", key="btn_h", use_container_width=True, type="primary" if st.session_state.selected_venc == "H" else "secondary"):
        st.session_state.selected_venc = "H"; st.rerun()
    if c2.button("🟢 EMPATE", key="btn_d", use_container_width=True, type="primary" if st.session_state.selected_venc == "D" else "secondary"):
        st.session_state.selected_venc = "D"; st.rerun()
    if c3.button("🔵 FORA", key="btn_a", use_container_width=True, type="primary" if st.session_state.selected_venc == "A" else "secondary"):
        st.session_state.selected_venc = "A"; st.rerun()
        
    st.divider()
    if st.button("🚀 CONFIRMAR E ANALISAR (OK)", use_container_width=True):
        confirmar_rodada()
        st.rerun()

with c_analise:
    st.subheader("🛰️ Monitoramento de Algoritmo")
    
    res = motor_mestre_analise()
    
    if res["tipo"] == "PERIGO":
        st.markdown(f"""
            <div class="danger-box">
                <h3 style="color:#fda4af; margin:0;">⚠️ MERCADO DO CASSINO EM ALERTA MÁXIMO</h3>
                <p style="margin:5px 0 0 0; color:#f43f5e; font-weight:bold;">{res['msg']}</p>
                <span style="font-size:12px; color:#fecdd3;">Não opere nesta sequência! Aguarde a mesa redefinir.</span>
            </div>
        """, unsafe_allow_html=True)
    
    elif res["tipo"] == "SINAL" and res["sug"]:
        st.markdown(f"""
            <div class="alert-master">
                <small style="color:#a7f3d0; text-transform: uppercase; font-weight:bold; letter-spacing:1px;">{res['msg']}</small>
                <h1 style="color:white; font-size:38px; margin:10px 0;">🎯 ENTRADA: {res['sug']}</h1>
                <div style="background:rgba(255,255,255,0.1); display:inline-block; padding:3px 15px; border-radius:20px; font-weight:bold;">
                    Confiança Mecânica: {res['conf']}%
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="alert-warning-master">
                <h3 style="margin:0; color:#fef08a;">🔍 Analisando Flutuação</h3>
                <p style="margin:5px 0 0 0; font-size:14px; color:#fde047;">{res['msg']}</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    # Dashboard Estatístico Rápido
    if st.session_state.h_football:
        total = len(st.session_state.h_football)
        casas = st.session_state.h_football.count("H")
        foras = st.session_state.h_football.count("A")
        
        st.write(f"📊 Volatilidade da Mesa: **{total} rodadas coletadas**")
        st.caption(f"Proporção Física Atual: 🔴 Casa {int((casas/total)*100)}% | 🔵 Fora {int((foras/total)*100)}%")
        
        # Histórico Estilo Fita de Cassino Real
        html_history = "<div style='overflow-x: auto; white-space: nowrap; padding: 12px; background:#0f172a; border-radius:12px; border: 1px solid #1e293b;'>"
        for item in st.session_state.h_football[:20]:
            html_history += f'<span class="history-ball ball-{item}">{item}</span>'
        html_history += "</div>"
        st.markdown(html_history, unsafe_allow_html=True)

st.divider()
if st.button("🗑️ ENVIAR NOVAS CARTAS (RESET BARALHO)"):
    st.session_state.h_football = []
    st.session_state.selected_venc = None
    st.rerun()
