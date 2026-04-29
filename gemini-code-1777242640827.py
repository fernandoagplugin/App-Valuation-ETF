import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações Iniciais
st.set_page_config(page_title="ETF Analytics Pro", layout="wide")

# 2. CSS Global Mínimo (Apenas para cores de fundo e fontes)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; color: #8b949e; }
    </style>
    """, unsafe_allow_html=True)

# 3. Configuração dos Ativos
# Adicionamos a bandeira diretamente no nome para evitar erros de renderização
etfs_config = {
    'IVV': {'nome': '🇺🇸 S&P 500 ETF', 'cor': '#00b894'},
    'VEA': {'nome': '🇺🇸 Dev. Markets', 'cor': '#1f6feb'},
    'SOXX': {'nome': '🇺🇸 Semiconductors', 'cor': '#8957e5'},
    'IAU': {'nome': '🇺🇸 Gold Trust', 'cor': '#d29922'},
    'SIVR': {'nome': '🇺🇸 Silver Trust', 'cor': '#b2bec3'},
    'DIVO11.SA': {'nome': '🇧🇷 Dividendos Br', 'cor': '#e17055'}
}

# 4. Sidebar
with st.sidebar:
    st.title("📊 Controle")
    st.info("💡 Dica: Se o layout quebrar, desative a 'Tradução Automática' do seu navegador para esta página.")
    margem_seg = st.slider("Margem de Segurança (%)", 0, 20, 5) / 100
    if st.button("🔄 Atualizar Base de Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. Coleta de Dados (Yahoo Finance)
@st.cache_data(ttl=3600)
def fetch_data(tickers):
    store = {}
    for t in tickers:
        try:
            ticker_obj = yf.Ticker(t)
            hist = ticker_obj.history(period="1y")
            if not hist.empty:
                store[t] = {
                    'atual': hist['Close'].iloc[-1],
                    'media': hist['Close'].rolling(window=50).mean().iloc[-1],
                    'df': hist
                }
        except Exception: continue
    return store

dados_mercado = fetch_data(list(etfs_config.keys()))

# 6. Dashboard Principal
st.title("ETF Analytics Pro 💎")
st.caption("Monitoramento de Preço Teto baseado em Média Móvel (50 dias)")

if dados_mercado:
    # Criamos as colunas para os cards
    cols = st.columns(len(etfs_config))
    
    for i, (ticker, config) in enumerate(etfs_config.items()):
        if ticker in dados_mercado:
            with cols[i]:
                # O SEGREDO: st.container(border=True) cria o card sem usar HTML instável
                with st.container(border=True):
                    d = dados_mercado[ticker]
                    p_teto = d['media'] * (1 - margem_seg)
                    margem_valor = ((p_teto - d['atual']) / p_teto) * 100
                    moeda = "R$" if ".SA" in ticker else "US$"
                    
                    # Título do Card
                    st.subheader(f"{ticker.replace('.SA', '')}")
                    st.caption(config['nome'])
                    
                    # Métricas Principais
                    st.metric("Preço Atual", f"{moeda} {d['atual']:.2f}")
                    st.metric("Preço Teto", f"{moeda} {p_teto:.2f}")
                    
                    # Lógica de Cor da Margem: 
                    # Se Atual < Teto -> Margem Positiva (Verde)
                    # Se Atual > Teto -> Margem Negativa (Vermelho)
                    delta_color = "normal" if d['atual'] <= p_teto else "inverse"
                    
                    st.metric(
                        label="Margem Real", 
                        value=f"{margem_valor:.1f}%",
                        delta=f"{'Oportunidade' if margem_valor > 0 else 'Sobrepreço'}",
                        delta_color=delta_color
                    )

    # 7. Gráfico Técnico
    st.markdown("---")
    st.subheader("📈 Tendência Histórica")
    
    selecionado = st.selectbox(
        "Selecione o ativo para análise detalhada:", 
        options=list(dados_mercado.keys()),
        format_func=lambda x: f"{etfs_config[x]['nome']} ({x.replace('.SA', '')})"
    )
    
    df_plot = dados_mercado[selecionado]['df']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['Close'], 
        name='Preço', line=dict(color=etfs_config[selecionado]['cor'], width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['Close'].rolling(50).mean(), 
        name='Média 50d', line=dict(color='#8b949e', dash='dot')
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Erro ao conectar com a API do Yahoo Finance. Verifique sua conexão.")
