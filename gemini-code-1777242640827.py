import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações da Página
st.set_page_config(page_title="ETF Analytics Pro", layout="wide")

# 2. Configuração dos Ativos com Bandeiras e Cores
etfs_config = {
    'IVV': {'nome': 'S&P 500 ETF', 'flag': '🇺🇸', 'cor': '#00b894'},
    'VEA': {'nome': 'Dev. Markets', 'flag': '🇺🇸', 'cor': '#0984e3'},
    'SOXX': {'nome': 'Semiconductors', 'flag': '🇺🇸', 'cor': '#6c5ce7'},
    'IAU': {'nome': 'Gold Trust', 'flag': '🇺🇸', 'cor': '#fdcb6e'},
    'SIVR': {'nome': 'Silver Trust', 'flag': '🇺🇸', 'cor': '#b2bec3'},
    'DIVO11.SA': {'nome': 'Dividendos Br', 'flag': '🇧🇷', 'cor': '#e17055'}
}

# 3. Sidebar (Painel de Controle)
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    margem_seg = st.slider("Margem de Segurança (%)", 0, 20, 5) / 100
    st.markdown("---")
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 4. Coleta de Dados Blindada
@st.cache_data(ttl=3600)
def carregar_dados(tickers):
    data = {}
    for t in tickers:
        try:
            asset = yf.Ticker(t)
            h = asset.history(period="1y")
            if not h.empty:
                data[t] = {
                    'p_atual': h['Close'].iloc[-1],
                    'p_medio': h['Close'].rolling(window=50).mean().iloc[-1],
                    'historico': h
                }
        except: continue
    return data

dados = carregar_dados(list(etfs_config.keys()))

# 5. Interface Principal
st.markdown("<h1 class='notranslate'>ETF Analytics Pro 💎</h1>", unsafe_allow_html=True)
st.markdown("---")

if dados:
    # Grid de 6 colunas
    cols = st.columns(6)
    
    for i, (ticker, cfg) in enumerate(etfs_config.items()):
        if ticker in dados:
            with cols[i]:
                d = dados[ticker]
                p_teto = d['p_medio'] * (1 - margem_seg)
                margem_real = ((p_teto - d['p_atual']) / p_teto) * 100
                moeda = "R$" if ".SA" in ticker else "$"
                
                # Lógica de cores para a margem
                cor_status = "#00b894" if margem_real >= 0 else "#ff7675"
                bg_status = "rgba(0, 184, 148, 0.1)" if margem_real >= 0 else "rgba(255, 118, 117, 0.1)"
                
                # Card HTML Blindado contra Tradução
                st.markdown(f"""
                <div class="notranslate" style="
                    background-color: #161b22; 
                    border: 1px solid #30363d; 
                    border-top: 4px solid {cfg['cor']}; 
                    border-radius: 12px; 
                    padding: 15px;
                    min-height: 240px;
                ">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: white; font-weight: 800; font-size: 1.2rem;">{ticker.replace('.SA','')}</span>
                        <span>{cfg['flag']}</span>
                    </div>
                    <div style="color: #8b949e; font-size: 0.75rem; margin-bottom: 15px;">{cfg['nome']}</div>
                    
                    <div style="margin-bottom: 8px;">
                        <span style="color: #8b949e; font-size: 0.7rem; display: block;">PREÇO ATUAL</span>
                        <span style="color: white; font-size: 1.1rem; font-weight: bold;">{moeda} {d['p_atual']:.2f}</span>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <span style="color: #8b949e; font-size: 0.7rem; display: block;">PREÇO TETO</span>
                        <span style="color: #c9d1d9; font-size: 0.95rem;">{moeda} {p_teto:.2f}</span>
                    </div>
                    
                    <div style="
                        background-color: {bg_status}; 
                        color: {cor_status}; 
                        border: 1px solid {cor_status}; 
                        padding: 6px; 
                        border-radius: 6px; 
                        text-align: center; 
                        font-weight: bold; 
                        font-size: 0.85rem;
                    ">
                        Margem: {margem_real:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 6. Gráfico de Análise
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Análise de Tendência e Médias")
    selecionado = st.selectbox("Escolha um ativo para ver detalhes:", list(dados.keys()), 
                               format_func=lambda x: f"{etfs_config[x]['flag']} {x.replace('.SA', '')}")
    
    df_plot = dados[selecionado]['historico'].tail(120) # Últimos 6 meses
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], name='Preço', line=dict(color=etfs_config[selecionado]['cor'], width=2)))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'].rolling(50).mean(), name='Média 50d', line=dict(color='white', dash='dot')))
    
    fig.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aguardando conexão com Yahoo Finance...")
