import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações da Página
st.set_page_config(page_title="ETF Analytics Pro", layout="wide")

# 2. CSS Mínimo - Apenas para evitar que os números fiquem cortados ("...")
st.markdown("""
    <style>
    /* Reduz o tamanho da fonte das métricas para caber em 6 colunas perfeitamente */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    /* Reduz o espaçamento entre as métricas dentro do card */
    [data-testid="stMetric"] {
        margin-bottom: -15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Configuração dos Ativos
etfs_config = {
    'IVV': {'nome': '🇺🇸 S&P 500 ETF'},
    'VEA': {'nome': '🇺🇸 Dev. Markets'},
    'SOXX': {'nome': '🇺🇸 Semiconductors'},
    'IAU': {'nome': '🇺🇸 Gold Trust'},
    'SIVR': {'nome': '🇺🇸 Silver Trust'},
    'DIVO11.SA': {'nome': '🇧🇷 Dividendos Br'}
}

# 4. Sidebar
st.sidebar.title("📊 Painel de Controle")
margem_seguranca = st.sidebar.slider("Margem de Segurança (%)", 0, 20, 5) / 100

if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# 5. Busca de Dados
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

# 6. Interface Principal
st.title("ETF Analytics Pro 💎")

if dados:
    cols = st.columns(6)
    for i, (ticker, cfg) in enumerate(etfs_config.items()):
        if ticker in dados:
            with cols[i]:
                # Card Nativo do Streamlit (Sem quebras de HTML)
                with st.container(border=True):
                    d = dados[ticker]
                    p_teto = d['media'] * (1 - margem_seguranca)
                    margem_p = ((p_teto - d['atual']) / p_teto) * 100
                    moeda = "R$" if ".SA" in ticker else "$"
                    
                    # Cabeçalho do Card
                    st.markdown(f"**{ticker.replace('.SA', '')}**")
                    st.caption(cfg['nome'])
                    
                    # Métricas
                    st.metric(label="Preço Atual", value=f"{moeda} {d['atual']:.2f}")
                    st.metric(label="Preço Teto", value=f"{moeda} {p_teto:.2f}")
                    
                    # Cor da margem automática
                    st.metric(
                        label="Margem Seg.", 
                        value=f"{margem_p:.1f}%", 
                        delta=f"{margem_p:.1f}%",
                        delta_color="normal" if d['atual'] <= p_teto else "inverse"
                    )

    st.markdown("---")
    
    # 7. Gráfico
    st.subheader("📈 Tendência")
    selecionado = st.selectbox("Selecione o ativo:", list(dados.keys()), format_func=lambda x: x.replace(".SA", ""))
    df_plot = dados[selecionado]['hist'].tail(252)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], name='Preço', line=dict(color='#1f6feb', width=2)))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'].rolling(50).mean(), name='Média 50d', line=dict(color='#8b949e', dash='dot')))
    
    fig.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0), 
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Carregando dados do Yahoo Finance...")
