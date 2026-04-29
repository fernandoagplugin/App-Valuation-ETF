import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Configurações da Página - Layout Largo e Título Profissional
st.set_page_config(page_title="ETF Analytics Pro", layout="wide")

# Estilos Visuais - Design Limpo e Profissional
st.markdown("""
    <style>
    /* Estilo Moderno para os Títulos */
    .stApp h1 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 0px;
    }
    
    .stApp h3 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #f0f2f6;
        font-weight: 600;
        margin-top: 25px;
    }
    
    /* Estilo para os Cards de Ativos */
    div.element-container div[data-testid="stMarkdownContainer"] div {
        border: 1px solid #323640; /* Borda mais suave */
        border-radius: 12px;
        background-color: #1a1e28;
        padding: 18px 18px 10px 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    
    div.element-container div[data-testid="stMarkdownContainer"] div:hover {
        transform: translateY(-5px);
        border-color: #4c525f;
    }
    
    .ticker-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.5em;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 2px;
    }
    
    .asset-desc {
        color: #8b96a4;
        font-size: 0.8em;
        font-weight: 400;
        margin-bottom: 12px;
    }
    
    .ticker-separator {
        border-top: 2px solid;
        width: 40px;
        margin-bottom: 15px;
    }
    
    /* Customização do Componente Nativo st.metric para consistência */
    div[data-testid="stMetricValue"] {
        color: #ffffff;
    }
    
    div[data-testid="stMetricDelta"] > div {
        font-weight: 700;
    }

    </style>
    """, unsafe_allow_html=True)

# 2. Definição dos ETFs - Cores mais Profissionais e Bandeiras
etfs_config = {
    'IVV': {'nome': '🇺🇸 S&P 500 ETF', 'cor': '#34d399'},     # Verde moderno
    'VEA': {'nome': '🇺🇸 Developed Markets', 'cor': '#60a5fa'}, # Azul suave
    'SOXX': {'nome': '🇺🇸 Semiconductors', 'cor': '#a78bfa'}, # Roxo
    'IAU': {'nome': '🇺🇸 Gold Trust', 'cor': '#fbbf24'},       # Amarelo moderno
    'SIVR': {'nome': '🇺🇸 Silver Trust', 'cor': '#94a3b8'},     # Cinza suave
    'DIVO11.SA': {'nome': '🇧🇷 Dividendos Brasil', 'cor': '#f97316'} # Laranja
}

# 3. Sidebar (Mantendo todas as funcionalidades antigas)
with st.sidebar:
    st.image("https://raw.githubusercontent.com/tadeumesquita/assets/main/finance_logo.png", width=120) # Logo (opcional, adicione a url)
    st.header("📊 Painel de Controle")
    margem_seguranca = st.slider("Margem de Segurança (%)", 0, 20, 5, step=1) / 100
    periodo_grafico = st.selectbox("Período do Gráfico", ["6mo", "1y", "2y", "5y"], index=1)
    
    st.markdown("---")
    st.subheader("⚠️ Configurações")
    if st.button("🔄 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 4. Busca de Dados
@st.cache_data(ttl=3600)
def buscar_dados_etf(tickers, period):
    data_dict = {}
    
    # Busca um pouco mais de histórico para garantir o cálculo da média
    hist_period = "2y" 
    
    for t in tickers:
        try:
            ticker_obj = yf.Ticker(t)
            hist = ticker_obj.history(period=hist_period)
            if hist.empty: continue
            
            preco_atual = hist['Close'].iloc[-1]
            preco_justo = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            # Filtra o histórico para o gráfico baseado no período do slider
            if period == '6mo':
                hist_plot = hist.tail(126)
            elif period == '1y':
                hist_plot = hist.tail(252)
            else:
                hist_plot = hist
            
            data_dict[t] = {
                'preco_atual': preco_atual,
                'preco_justo': preco_justo,
                'historico': hist_plot
            }
        except Exception as e:
            st.error(f"Erro ao buscar {t}: {e}")
            continue
    return data_dict

dados_etf = buscar_dados_etf(list(etfs_config.keys()), periodo_grafico)

# 5. Interface Principal
st.title("ETF Analytics Pro 💎")
st.markdown("<p style='color:#a3b1c6;'>Monitoramento em tempo real de ativos globais e estratégia de preço-teto.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if dados_etf:
    # Ajuste dinâmico de colunas baseado na quantidade de ativos
    cols = st.columns(len(etfs_config))
    
    for i, (ticker, config) in enumerate(etfs_config.items()):
        if ticker in dados_etf:
            with cols[i]:
                d = dados_etf[ticker]
                p_teto = d['preco_justo'] * (1 - margem_seguranca)
                
                # Cálculo da Margem Real e Lógica de Moeda
                margem_real_num = p_teto - d['preco_atual']
                moeda = "R$" if ".SA" in ticker else "$"
                ticker_display = ticker.replace(".SA", "")
                
                # Monta o HTML do Card (Design Limpo)
                card_html = f"""
                    <div style="border-top: 4px solid {config['cor']};">
                        <div class="ticker-header">{ticker_display}</div>
                        <div class="asset-desc">{config['nome']}</div>
                        <div class="ticker-separator" style="border-color: {config['cor']};"></div>
                    </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Usa o componente NATIVO st.metric (Corrige os bugs de cores)
                col_met1, col_met2 = st.columns(2)
                with col_met1:
                    st.metric(label="Preço Atual", value=f"{moeda}{d['preco_atual']:.2f}")
                with col_met2:
                    st.metric(label="Preço Teto", value=f"{moeda}{p_teto:.2f}")
                
                # Métrica de Margem com cor de alta/baixa consistente
                st.metric(label="Margem Real", value=f"{moeda}{margem_real_num:.2f}", delta=f"{((p_teto - d['preco_atual']) / p_teto) * 100:.1f}%")

    st.markdown("---")
    
    # 6. Gráfico Detalhado - Design Bloomberg-style
    st.subheader("📈 Análise de Tendência e Médias")
    
    # Seletor com formato mais limpo
    selecionado = st.selectbox(
        "Filtrar ativo para análise profunda:", 
        options=list(dados_etf.keys()), 
        format_func=lambda x: f"{x.replace('.SA', '')} - {etfs_config[x]['nome']}"
    )
    
    df_plot = dados_etf[selecionado]['historico']
    
    fig = go.Figure()
    # Linha principal do preço - Cheia e colorida
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['Close'], 
        name='Preço de Mercado', 
        line=dict(color=etfs_config[selecionado]['cor'], width=3.5),
        fill='tozeroy', fillcolor=f'rgba({int(etfs_config[selecionado]["cor"][1:3],16)}, {int(etfs_config[selecionado]["cor"][3:5],16)}, {int(etfs_config[selecionado]["cor"][5:7],16)}, 0.05)' # Fill suave
    ))
    # Média de 50d - Pontilhada e discreta
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot['Close'].rolling(window=50).mean(), 
        name='Média 50d (Preço Justo)', 
        line=dict(color='#ffffff', width=1.2, dash='dot'),
        opacity=0.4
    ))
    
    # Estilização completa do gráfico (Plotly Moderno)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#848d9a", size=12),
        xaxis=dict(showgrid=False, linecolor='#323640'),
        yaxis=dict(showgrid=True, gridcolor='#323640', linecolor='#323640', position=0.01),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Conexão interrompida. Verifique se o Yahoo Finance está acessível ou clique em Atualizar Dados.")
