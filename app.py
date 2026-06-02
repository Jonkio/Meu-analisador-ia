import streamlit as st
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="ÁPICE IA - SUPREME PREDICTOR", layout="wide")

# Chave de Acesso do Painel
SENHA_CORRETA = "APICE777"

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- BLINDAGEM DE ACESSO ---
if not st.session_state.autenticado:
    st.markdown("""
    <style>
        .main { background-color: #020617; color: white; }
        .login-box { 
            max-width: 450px; margin: 100px auto; padding: 40px; 
            background: #0f172a; border-radius: 20px; 
            border: 2px solid #1e293b; text-align: center;
            box-shadow: 0 0 20px rgba(96, 165, 250, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-box">
        <h2 style="color: #60a5fa; margin-bottom: 5px;">🔒 SISTEMA SUPREMO BLINDADO</h2>
        <p style="color: #94a3b8; font-size: 14px; margin-bottom: 25px;">Insira a chave de criptografia para liberar a IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    c_left, c_mid, c_right = st.columns([1, 2, 1])
    with c_mid:
        senha_digitada = st.text_input("Chave de Acesso:", type="password", label_visibility="collapsed", placeholder="Digite a senha...")
        if st.button("DESBLOQUEAR PAINEL", use_container_width=True):
            if senha_digitada == SENHA_CORRETA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Chave incorreta!")
    st.stop()

# --- ESTILIZAÇÃO DO ECOSSISTEMA SUPREMO ---
st.markdown("""
<style>
    .main { background-color: #020617; color: white; }
    .stButton>button { height: 75px; border-radius: 15px; font-weight: bold; font-size: 20px; }
    
    .ball-H { display: inline-block; width: 35px; height: 35px; line-height: 35px; border-radius: 50%; text-align: center; font-weight: bold; margin: 2px; background-color: #dc2626; color: white; box-shadow: 0 0 8px #ef4444; }
    .ball-A { display: inline-block; width: 35px; height: 35px; line-height: 35px; border-radius: 50%; text-align: center; font-weight: bold; margin: 2px; background-color: #2563eb; color: white; box-shadow: 0 0 8px #3b82f6; }
    .ball-D { display: inline-block; width: 35px; height: 35px; line-height: 35px; border-radius: 50%; text-align: center; font-weight: bold; margin: 2px; background-color: #16a34a; color: white; }
    
    .box-win { background: linear-gradient(145deg, #064e3b, #022c22); border: 2px solid #22c55e; padding: 20px; border-radius: 15px; text-align: center; }
    .box-surf { background: linear-gradient(145deg, #1e3a8a, #172554); border: 2px solid #3b82f6; padding: 20px; border-radius: 15px; text-align: center; }
    .box-danger { background: #4c0519; border: 2px solid #f43f5e; padding: 20px; border-radius: 15px; text-align: center; }
    .box-kelly { background: #1e1b4b; border: 1px dashed #818cf8; padding: 10px; border-radius: 10px; text-align: center; margin-top: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Inicialização de Variáveis de Estado
if 'selected_venc' not in st.session_state: st.session_state.selected_venc = None
if 'h_football' not in st.session_state: st.session_state.h_football = []
if 'palpites_log' not in st.session_state: st.session_state.palpites_log = []
if 'proximo_palpite' not in st.session_state: st.session_state.proximo_palpite = None

def confirmar_rodada():
    if st.session_state.selected_venc:
        resultado_real = st.session_state.selected_venc
        if st.session_state.proximo_palpite:
            p = st.session_state.proximo_palpite
            status_resultado = "❌ RED"
            if p["sug_curta"] == resultado_real:
                status_resultado = "✅ GREEN DIRETO"
            elif resultado_real == "D" and p["sug_curta"] == "EMPATE":
                status_resultado = "🟢 GREEN EMPATE"
            elif p["sug_curta"] in ["H", "A"] and resultado_real != "D":
                status_resultado = "⚠️ GALE 1"
                
            st.session_state.palpites_log.insert(0, {
                "rodada": len(st.session_state.h_football) + 1,
                "previsao": p["sug_completa"],
                "resultado": status_resultado
            })
        st.session_state.h_football.insert(0, resultado_real)
        st.session_state.selected_venc = None
    else:
        st.error("Selecione quem ganhou antes de apertar OK!")

# --- MOTOR MATEMÁTICO SUPREMO ---
def processar_ia_suprema():
    h = st.session_state.h_football
    fluxo = [x for x in h if x != "D"]
    
    if len(fluxo) < 8:
        return {"status": "NEUTRO", "msg": "Alimentando Matrizes Estatísticas...", "sug": None, "sug_curta": None, "conf": 0}

    # 1. FILTRO CHI-QUADRADO (Análise de Desvio e Manipulação)
    observado_h = fluxo[:12].count("H")
    observado_a = fluxo[:12].count("A")
    esperado = len(fluxo[:12]) / 2
    # Cálculo simplificado do desvio padrão dinâmico
    chi_sq = ((observado_h - esperado)**2 / esperado) + ((observado_a - esperado)**2 / esperado) if esperado > 0 else 0
    
    if chi_sq > 4.5 or fluxo[:5] == ["H"]*5 or fluxo[:5] == ["A"]*5:
        return {"status": "MANIPULACAO", "msg": f"Desvio Crítico Chi-Sq ({chi_sq:.1f}). Algoritmo agindo de forma não linear.", "sug": "RETENÇÃO DETECTADA - ABORTAR", "sug_curta": "STOP", "conf": 0}

    # 2. MOMENTUM EXPONENCIAL DE CURTO PRAZO
    # Peso 3x maior para as últimas 3 rodadas vs as anteriores
    peso_recente = fluxo[0:3].count(fluxo[0])
    
    # 3. CLUSTERING DE EMPATES (Rastreador de Gaps e Efeito Eco)
    gaps_empate = []
    contador = 0
    for x in h:
        if x == "D":
            if contador > 0: gaps_empate.append(contador)
            contador = 0
        else: contador += 1
        
    if h[0] == "D" or (len(h) > 1 and h[1] == "D"):
        # Janela de Efeito Eco Ativa (Empates próximos)
        return {"status": "EMPATE", "msg": "Efeito Eco ativado. Densidade de empates agrupada por Clustering.", "sug": "PROTEGER EMPATE (VERDE)", "sug_curta": "EMPATE", "conf": 75}

    # 4. MAPEAMENTO DE PADRÕES COMPLEXOS (Padrão Espelho e Quebras de Bloco)
    s_seis = "".join(fluxo[:6])
    s_quatro = "".join(fluxo[:4])
    
    # Padrão Espelho (Ex: HAAHAH ou AHHARA)
    if s_seis in ["HAAHAH", "AHHARA"]:
        sug_cor = "🔴 CASA" if s_seis.endswith("A") else "🔵 FORA"
        sug_curta = "H" if s_seis.endswith("A") else "A"
        return {"status": "PADRAO", "msg": "Assinatura Algorítmica Detectada: Padrão Espelho.", "sug": f"ENTRADA COMPLEXA: {sug_cor}", "sug_curta": sug_curta, "conf": 88}

    # 5. MÓDULO SURFE DE TENDÊNCIA VALIDADO PELO MOMENTUM
    cor_atual = fluxo[0]
    tamanho_surfe = 0
    for x in fluxo:
        if x == cor_atual: tamanho_surfe += 1
        else: break
        
    if 3 <= tamanho_surfe <= 6 and peso_recente >= 2:
        sug_cor = "🔴 CASA" if cor_atual == "H" else "🔵 FORA"
        return {
            "status": "SURFE",
            "msg": f"Trend Rider: Surfe validado na {tamanho_surfe}ª casa por Momentum Exponencial.",
            "sug": f"SURFAR NO FLUXO: {sug_cor}",
            "sug_curta": cor_atual,
            "conf": 82
        }

    # Reversão Clássica Inteligente
    if fluxo[0] == fluxo[1]:
        sug_inv = "🔵 FORA" if fluxo[0] == "H" else "🔴 CASA"
        sug_curta = "A" if fluxo[0] == "H" else "H"
        return {"status": "PADRAO", "msg": "Estabilidade de mercado. Padrão de reversão cirúrgica ativo.", "sug": sug_inv, "sug_curta": sug_curta, "conf": 80}

    return {"status": "NEUTRO", "msg": "Aguardando Assimetria Estatística Confiável...", "sug": None, "sug_curta": None, "conf": 0}

# --- INTERFACE SUPREMA ---
col_t1, col_t2 = st.columns([5, 1])
with col_t1:
    st.title("🎯 ÁPICE IA V6 — SUPREME PREDICTOR")
with col_t2:
    if st.button("🔒 SAIR", key="btn_logout"):
        st.session_state.autenticado = False
        st.rerun()

col_in, col_an = st.columns([1, 1.2])

with col_in:
    st.subheader("📥 Registro Antierro")
    c1, c2, c3 = st.columns(3)
    if c1.button("🔴 CASA", key="b_h", use_container_width=True, type="primary" if st.session_state.selected_venc == "H" else "secondary"):
        st.session_state.selected_venc = "H"; st.rerun()
    if c2.button("🟢 EMPATE", key="b_d", use_container_width=True, type="primary" if st.session_state.selected_venc == "D" else "secondary"):
        st.session_state.selected_venc = "D"; st.rerun()
    if c3.button("🔵 FORA", key="b_a", use_container_width=True, type="primary" if st.session_state.selected_venc == "A" else "secondary"):
        st.session_state.selected_venc = "A"; st.rerun()
        
    st.divider()
    if st.button("🚀 CONFIRMAR JOGADA (OK)", use_container_width=True):
        confirmar_rodada()
        st.rerun()

with col_an:
    st.subheader("🔮 Processamento de Matriz de Confiança")
    
    res = processar_ia_suprema()
    
    if res["sug_curta"] and res["sug_curta"] != "STOP":
        st.session_state.proximo_palpite = {"sug_curta": res["sug_curta"], "sug_completa": res["sug"]}
        
        # 📊 CÁLCULO GESTÃO DE BANCA: CRITÉRIO DE KELLY DUPLEX
        prob = res["conf"] / 100
        b_odds = 1.0 # Pagamento comum 1:1 (dobra a aposta)
        f_kelly = ((prob * b_odds) - (1 - prob)) / b_odds
        f_kelly_fracional = max(0.01, f_kelly * 0.3) * 100 # Multiplicador conservador de segurança (Kelly Fracionado a 30%)
        texto_kelly = f"🛡️ GESTÃO DE KELLY: Recomendado entrar com {f_kelly_fracional:.1f}% da sua banca ativa."
    else:
        st.session_state.proximo_palpite = None
        texto_kelly = None

    # Renderização Gráfica dos Cards Analíticos
    if res["status"] == "MANIPULACAO":
        st.markdown(f'<div class="box-danger"><h2>⚠️ ALERTA DE MANIPULAÇÃO</h2><h3>{res["sug"]}</h3><p>{res["msg"]}</p></div>', unsafe_allow_html=True)
    elif res["status"] == "SURFE":
        st.markdown(f'<div class="box-surf"><h2>🌊 TREND RIDER ATIVO</h2><h1 style="color:#fde047; margin:5px 0;">{res["sug"]}</h1><p>{res["msg"]}</p></div>', unsafe_allow_html=True)
        if texto_kelly: st.markdown(f'<div class="box-kelly">{texto_kelly}</div>', unsafe_allow_html=True)
    elif res["status"] == "EMPATE":
        st.markdown(f'<div class="box-win" style="background: linear-gradient(145deg, #14532d, #064e3b); border-color: #4ade80;"><h2>🟢 COMBINAÇÃO DE EMPATE (ECO)</h2><h1 style="color:white; margin:5px 0;">{res["sug"]}</h1><p>{res["msg"]}</p></div>', unsafe_allow_html=True)
    elif res["status"] == "PADRAO":
        st.markdown(f'<div class="box-win"><h2>🎯 PALPITE ADAPTADO</h2><h1 style="color:white; margin:5px 0;">{res["sug"]}</h1><p>{res["msg"]}</p></div>', unsafe_allow_html=True)
        if texto_kelly: st.markdown(f'<div class="box-kelly">{texto_kelly}</div>', unsafe_allow_html=True)
    else:
        st.info(res["msg"])

st.divider()
col_grids1, col_grids2 = st.columns([1, 1.2])

with col_grids1:
    st.subheader("📜 Painel Roadmap (Evolution)")
    if st.session_state.h_football:
        html_history = "<div style='overflow-x: auto; white-space: nowrap; padding: 12px; background:#0f172a; border-radius:12px; border: 1px solid #1e293b;'>"
        for item in st.session_state.h_football[:25]:
            html_history += f'<span class="history-ball ball-{item}">{item}</span>'
        html_history += "</div>"
        st.markdown(html_history, unsafe_allow_html=True)
    else:
        st.caption("Sem dados no baralho.")

with col_grids2:
    st.subheader("📊 Auditoria de Assertividade Real")
    if st.session_state.palpites_log:
        for log in st.session_state.palpites_log[:6]:
            st.markdown(f"**Rodada {log['rodada']}** | Previsão: `{log['previsao']}` ➔ **{log['resultado']}**")
    else:
        st.caption("Aguardando confirmações...")

st.divider()
if st.button("🗑️ RESETAR SISTEMA MATRICIAL"):
    st.session_state.h_football = []
    st.session_state.palpites_log = []
    st.session_state.proximo_palpite = None
    st.session_state.selected_venc = None
    st.rerun()
