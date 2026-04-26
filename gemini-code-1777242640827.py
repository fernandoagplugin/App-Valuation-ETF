import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Configurações da Página
st.set_page_config(page_title="Dashboard ETFs Internacionais", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .card { padding: 15px; border-radius: 10px; background-color: white; box-shadow: 1px 1px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Definição dos ETFs e Parâmetros
# Nota: Para ETFs, o "Preço Teto" é calculado com base em uma margem de segurança sobre a média recente
etfs_config = {
    'IVV': {'nome': 'S&P 500 ETF', 'cor': '#27ae60', 'tipo': 'Ações US'},
    'VEA': {'nome': 'Developed Markets', 'cor': '#2980b9', 'tipo': 'Internacional'},
    'SOXX': {'nome': 'Semiconductors', 'cor': '#8e44ad', 'tipo': 'Setorial Tech'},
    'IAU': {'nome': 'iShares Gold Trust', 'cor': '#f1c40f', 'tipo': 'Commodity (Ouro)'},
    'SIVR': {'nome': 'Abrdn Silver Trust', 'cor': '#95a5a6', 'tipo': 'Commodity (Prata)'}
}

# 3. Sidebar
st.sidebar.header("📊 Filtros e Configurações")
margem_desejada = st.sidebar.slider("Margem de Segurança (%)", 0, 20, 5) / 100
periodo_grafico = st.sidebar.selectbox("Período do Gráfico", ["1mo", "3mo", "6mo", "1y", "5y"])

if st.sidebar.button("🔄 Atualizar Dados em Tempo Real"):
    st.cache_data.clear()
    st.rerun()

# 4. Função para buscar dados e histórico
@st.cache_data(ttl=600)
def buscar_dados_etf(tickers, period):
    data_dict = {}
    for t in tickers:
        ticker = yf.Ticker(t)
        hist = ticker.history(period=period)
        info = ticker.info
        
        # Preço Justo Simulado: Média móvel dos últimos 50 dias como referência de valor
        preco_justo = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) > 50 else hist['Close'].mean()
        
        data_dict[t] = {
            'preco_atual': hist['Close'].iloc[-1],
            'preco_justo': preco_justo,
            'historico': hist
        }
    return data_dict

dados_etf = buscar_dados_etf(list(etfs_config.keys()), periodo_grafico)

# 5. Dashboard Principal
st.title("🌎 Monitor de ETFs: Preço Justo & Performance")

# Linha de Cards
cols = st.columns(5)
for i, (ticker, config) in enumerate(etfs_config.items()):
    with cols[i]:
        d = dados_etf[ticker]
        p_teto = d['preco_justo'] * (1 - margem_desejada)
        margem_real = ((p_teto - d['preco_atual']) / p_teto) * 100
        cor = "green" if d['preco_atual'] <= p_teto else "red"
        
        st.markdown(f"""
            <div class="card" style="border-left: 5px solid {config['cor']};">
                <h3 style="margin:0;">{ticker}</h3>
                <small>{config['tipo']}</small>
                <p style="margin:10px 0 0 0;">Preço: <b>${d['preco_atual']:.2f}</b></p>
                <p style="margin:0;">Teto: <b>${p_teto:.2f}</b></p>
                <p style="color:{cor}; margin:0;">Margem: <b>{margem_real:.1f}%</b></p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 6. Gráfico Interativo com Plotly
st.subheader("📈 Histórico de Preços e Tendência")
ticker_selecionado = st.selectbox("Selecione o ETF para detalhamento:", list(etfs_config.keys()))

df_plot = dados_etf[ticker_selecionado]['historico']

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], name='Preço de Fechamento', line=dict(color=etfs_config[ticker_selecionado]['cor'], width=2)))
fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'].rolling(window=50).mean(), name='Média 50d (Preço Justo)', line=dict(color='gray', dash='dash')))

fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    margin=dict(l=0, r=0, t=30, b=0),
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_運用=True)

st.caption(f"Dados fornecidos via Yahoo Finance em {datetime.now().strftime('%d/%m/%Y %H:%M')}. O Preço Justo é calculado pela média móvel de 50 dias.")