import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações da Página e Proteção contra Tradutor
st.set_page_config(page_title="ETF Analytics Pro", layout="wide")

# Injeção de CSS para travar o layout e impedir tradução automática do navegador
st.markdown("""
    <html translate="no">
    <style>
    /* Impede tradução automática */
    .notranslate { translate: no !important; }
    
    /* Fundo e Container Principal */
    .stApp { background-color: #0e1117; }
    
    /* Estilização dos Cards Customizados */
    .card-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        min-height: 220px;
        border-top: 4px solid;
    }
    
    .ticker-name {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    
    .asset-desc {
        color: #8b949e;
        font-size: 0.75rem;
        margin-bottom: 15px;
        height: 35px;
        overflow: hidden;
    }
    
    .metric-label {
        color: #8b949e;
        font-size: 0.8rem;
        margin-top: 10px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
    }

    .margin-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-top: 15px;
        width: 100%;
        text-align: center;
    }
    </style>
    </html>
    """, unsafe_allow_html=True)

# 2. Definição dos ETFs
etfs_config = {
    'IVV': {'nome': '🇺🇸 S&P 500 ETF', 'cor': '#238636'},
    'VEA': {'nome': '🇺🇸 Dev. Markets', 'cor': '#1f6feb'},
    'SOXX': {'nome': '🇺🇸 Semiconductors', 'cor': '#8957e5'},
    'IAU': {'nome': '🇺🇸 Gold Trust', 'cor': '#d29922'},
    'SIVR': {'nome': '🇺🇸 Silver Trust', 'cor': '#484f58'},
    'DIVO11.SA': {'nome': '🇧🇷 Dividendos Br', 'cor': '#db6d28'}
}

# 3. Sidebar
st.sidebar.title("📊 Controle")
margem_seguranca = st.sidebar.slider("Margem de Segurança (%)", 0, 20, 5) / 100
periodo_grafico = st.sidebar.selectbox("Período do Gráfico", ["6mo", "1y", "2y", "5y"], index=1)

if st.sidebar.button("🔄 Atualizar"):
    st.cache_data.clear()
    st.rerun()

# 4. Busca de Dados
@st.cache_data(ttl=3600)
def buscar_dados(tickers):
    data_dict = {}
    for t in tickers:
        try:
            obj = yf.Ticker(t)
            hist = obj.history(period="2y")
            if hist.empty: continue
            data_dict[t] = {
                'atual': hist['Close'].iloc[-1],
                'justo': hist['Close'].rolling(window=50).mean().iloc[-1],
                'hist': hist
            }
        except: continue
    return data_dict

dados = buscar_dados(list(etfs_config.keys()))

# 5. Dashboard
st.title("ETF Analytics Pro 💎")

if dados:
    cols = st.columns(6)
    for i, (ticker, config) in enumerate(etfs_config.items()):
        if ticker in dados:
            with cols[i]:
                d = dados[ticker]
                p_teto = d['justo'] * (1 - margem_seguranca)
                margem_pct = ((p_teto - d['atual']) / p_teto) * 100
                moeda = "R$" if ".SA" in ticker else "$"
                
                # Cores de Status
                status_color = "#238636" if d['atual'] <= p_teto else "#da3633"
                status_bg = "rgba(35, 134, 54, 0.15)" if d['atual'] <= p_teto else "rgba(218, 54, 51, 0.15)"
                
                # Card em HTML Puro para evitar bugs do Streamlit Metrics
                st.markdown(f"""
                    <div class="card-container notranslate" style="border-top-color: {config['cor']};">
                        <div class="ticker-name">{ticker.replace('.SA', '')}</div>
                        <div class="asset-desc">{config['nome']}</div>
                        
                        <div class="metric-label">Preço Atual</div>
                        <div class="metric-value">{moeda} {d['atual']:.2f}</div>
                        
                        <div class="metric-label">Preço Teto</div>
                        <div class="metric-value">{moeda} {p_teto:.2f}</div>
                        
                        <div class="margin-badge" style="color: {status_color}; background-color: {status_bg}; border: 1px solid {status_color};">
                            Margem: {margem_pct:.1f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 6. Gráfico
    st.subheader("📈 Tendência")
    selecionado = st.selectbox("Ativo:", list(dados.keys()), format_func=lambda x: x.replace(".SA", ""))
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
