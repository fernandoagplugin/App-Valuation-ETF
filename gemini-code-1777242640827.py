import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações da Página
st.set_page_config(page_title="ETF Analytics Pro", layout="wide", initial_sidebar_state="expanded")

# 2. Configuração dos Ativos (Bandeiras separadas para layout mais limpo)
etfs_config = {
    'IVV': {'nome': 'S&P 500 ETF', 'bandeira': '🇺🇸', 'cor': '#00b894'}, # Verde moderno
    'VEA': {'nome': 'Developed Markets', 'bandeira': '🇺🇸', 'cor': '#0984e3'}, # Azul
    'SOXX': {'nome': 'Semiconductors', 'bandeira': '🇺🇸', 'cor': '#6c5ce7'}, # Roxo
    'IAU': {'nome': 'Gold Trust', 'bandeira': '🇺🇸', 'cor': '#fdcb6e'}, # Dourado
    'SIVR': {'nome': 'Silver Trust', 'bandeira': '🇺🇸', 'cor': '#b2bec3'}, # Prata
    'DIVO11.SA': {'nome': 'Dividendos Brasil', 'bandeira': '🇧🇷', 'cor': '#e17055'} # Laranja
}

# 3. Sidebar
with st.sidebar:
    st.markdown("## 📊 Painel de Controle")
    margem_seguranca = st.slider("Margem de Segurança (%)", 0, 20, 5) / 100
    periodo_grafico = st.selectbox("Período do Gráfico", ["6mo", "1y", "2y", "5y"], index=1)
    st.markdown("---")
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 4. Busca de Dados
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

# 5. Interface Principal
st.markdown("<h1 style='color: white; font-family: sans-serif; margin-bottom: 0;'>ETF Analytics Pro 💎</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8b949e; font-family: sans-serif; margin-bottom: 30px;'>Monitoramento avançado de margem de segurança e fair value.</p>", unsafe_allow_html=True)

if dados:
    cols = st.columns(6)
    for i, (ticker, cfg) in enumerate(etfs_config.items()):
        if ticker in dados:
            with cols[i]:
                d = dados[ticker]
                p_teto = d['media'] * (1 - margem_seguranca)
                
                # O cálculo exato da margem
                margem_p = ((p_teto - d['atual']) / p_teto) * 100
                
                # Controle Rígido das Cores da Margem (Verde para Positivo, Vermelho para Negativo)
                if margem_p >= 0:
                    bg_margem = "rgba(0, 184, 148, 0.15)" # Fundo verde transparente
                    cor_margem = "#00b894" # Texto verde
                else:
                    bg_margem = "rgba(214, 48, 49, 0.15)" # Fundo vermelho transparente
                    cor_margem = "#ff7675" # Texto vermelho claro
                
                moeda = "R$" if ".SA" in ticker else "US$"
                ticker_limpo = ticker.replace('.SA', '')
                
                # O Design do Card usando HTML/CSS Inline (100% à prova de quebra do Streamlit)
                card_html = f"""
                <div style="
                    background-color: #161b22; 
                    border: 1px solid #30363d; 
                    border-top: 4px solid {cfg['cor']}; 
                    border-radius: 12px; 
                    padding: 18px; 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                        <h3 style="margin: 0; color: #ffffff; font-size: 1.3rem;">{ticker_limpo}</h3>
                        <span style="font-size: 1.2rem;">{cfg['bandeira']}</span>
                    </div>
                    <p style="margin: 0 0 15px 0; color: #8b949e; font-size: 0.8rem;">{cfg['nome']}</p>
                    
                    <div style="margin-bottom: 12px;">
                        <p style="margin: 0; color: #8b949e; font-size: 0.75rem; text-transform: uppercase;">Preço Atual</p>
                        <p style="margin: 0; color: #ffffff; font-size: 1.25rem; font-weight: bold;">{moeda} {d['atual']:.2f}</p>
                    </div>
                    
                    <div style="margin-bottom: 18px;">
                        <p style="margin: 0; color: #8b949e; font-size: 0.75rem; text-transform: uppercase;">Preço Teto</p>
                        <p style="margin: 0; color: #c9d1d9; font-size: 1.05rem; font-weight: 500;">{moeda} {p_teto:.2f}</p>
                    </div>
                    
                    <div style="
                        background-color: {bg_margem}; 
                        color: {cor_margem}; 
                        border: 1px solid {cor_margem}40;
                        padding: 8px; 
                        border-radius: 6px; 
                        text-align: center; 
                        font-weight: bold; 
                        font-size: 0.9rem;
                    ">
                        Margem: {margem_p:.1f}%
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: #30363d;'><br>", unsafe_allow_html=True)
    
    # 6. Gráfico com visual Premium (Dark Mode nativo do Plotly)
    st.markdown("<h3 style='color: white; font-family: sans-serif;'>📈 Análise de Tendência e Fair Value</h3>", unsafe_allow_html=True)
    
    selecionado = st.selectbox("Selecione o ativo para análise aprofundada:", list(dados.keys()), format_func=lambda x: f"{x.replace('.SA', '')} - {etfs_config[x]['nome']}")
    df_plot = dados[selecionado]['hist'].tail(252) # Mostra o último ano (252 dias úteis)
    
    fig = go.Figure()
    
    # Linha do Preço Atual (com área preenchida suave)
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['Close'], 
        name='Preço de Mercado', 
        line=dict(color=etfs_config[selecionado]['cor'], width=2.5),
        fill='tozeroy', 
        fillcolor=f"rgba(255,255,255,0.02)"
    ))
    
    # Linha do Preço Justo (Média)
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['Close'].rolling(50).mean(), 
        name='Média 50d (Fair Value)', 
        line=dict(color='#8b949e', dash='dash', width=1.5)
    ))
    
    # Configuração do Layout do Gráfico
    fig.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0), 
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, linecolor='#30363d'),
        yaxis=dict(showgrid=True, gridcolor='#30363d', linecolor='#30363d')
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Carregando dados do Yahoo Finance...")
