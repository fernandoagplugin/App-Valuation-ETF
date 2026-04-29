import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações da Página
st.set_page_config(page_title="ETF Analytics Pro", layout="wide")

# 2. Estilo CSS Blindado (Corrigido o erro de fechamento de tag)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Container do Card */
    .etf-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border-top: 5px solid;
    }
    
    .ticker-id { color: #ffffff; font-size: 1.5rem; font-weight: 800; margin: 0; }
    .ticker-desc { color: #8b949e; font-size: 0.8rem; margin-bottom: 15px; }
    
    .m-label { color: #8b949e; font-size: 0.75rem; margin-top: 10px; text-transform: uppercase; }
    .m-value { color: #ffffff; font-size: 1.2rem; font-weight: 600; margin-bottom: 5px; }
    
    .status-badge {
        padding: 6px;
        border-radius: 6px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Configuração dos Ativos
etfs_config = {
    'IVV': {'nome': '🇺🇸 S&P 500 ETF', 'cor': '#238636'},
    'VEA': {'nome': '🇺🇸 Dev. Markets', 'cor': '#1f6feb'},
    'SOXX': {'nome': '🇺🇸 Semiconductors', 'cor': '#8957e5'},
    'IAU': {'nome': '🇺🇸 Gold Trust', 'cor': '#d29922'},
    'SIVR': {'nome': '🇺🇸 Silver Trust', 'cor': '#484f58'},
    'DIVO11.SA': {'nome': '🇧🇷 Dividendos Br', 'cor': '#db6d28'}
}

# 4. Sidebar
st.sidebar.title("📊 Controle")
margem_seguranca = st.sidebar.slider("Margem de Segurança (%)", 0, 20, 5) / 100
periodo_grafico = st.sidebar.selectbox("Período do Gráfico", ["6mo", "1y", "2y", "5y"], index=1)

if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# 5. Busca de Dados (Yahoo Finance)
@st.cache_data(ttl=3600)
def carregar_dados(tickers):
    data = {}
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            h = stock.history(period="2y")
            if h.empty: continue
            data[t] = {
                'atual': h['Close'].iloc[-1],
                'media': h['Close'].rolling(window=50).mean().iloc[-1],
                'hist': h
            }
        except: continue
    return data

dados = carregar_dados(list(etfs_config.keys()))

# 6. Dashboard
st.title("ETF Analytics Pro 💎")

if dados:
    cols = st.columns(6)
    for i, (ticker, cfg) in enumerate(etfs_config.items()):
        if ticker in dados:
            with cols[i]:
                d = dados[ticker]
                p_teto = d['media'] * (1 - margem_seguranca)
                margem_p = ((p_teto - d['atual']) / p_teto) * 100
                moeda = "R$" if ".SA" in ticker else "$"
                
                # Cores de Status
                s_color = "#238636" if d['atual'] <= p_teto else "#da3633"
                s_bg = "rgba(35, 134, 54, 0.1)" if d['atual'] <= p_teto else "rgba(218, 54, 51, 0.1)"
                
                # Renderização do Card corrigida
                st.markdown(f"""
                    <div class="etf-card" style="border-top-color: {cfg['cor']};">
                        <div class="ticker-id">{ticker.replace('.SA', '')}</div>
                        <div class="ticker-desc">{cfg['nome']}</div>
                        
                        <div class="m-label">Atual</div>
                        <div class="m-value">{moeda} {d['atual']:.2f}</div>
                        
                        <div class="m-label">P. Teto</div>
                        <div class="m-value">{moeda} {p_teto:.2f}</div>
                        
                        <div class="status-badge" style="color: {s_color}; background-color: {s_bg}; border: 1px solid {s_color};">
                            Margem: {margem_p:.1f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 7. Gráfico
    st.subheader("📈 Análise de Tendência")
    selecionado = st.selectbox("Selecione o ativo:", list(dados.keys()), format_func=lambda x: x.replace(".SA", ""))
    df_plot = dados[selecionado]['hist'].tail(252)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], name='Preço', line=dict(color=etfs_config[selecionado]['cor'], width=2)))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'].rolling(50).mean(), name='Média 50d', line=dict(color='#8b949e', dash='dot')))
    
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0), height=400,
        legend=dict(orientation="h", y=1.1, x=1, xanchor="right")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aguardando resposta do Yahoo Finance... Clique em Atualizar se demorar.")
