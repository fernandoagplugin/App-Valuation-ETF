import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações da Página e Estilo Moderno
st.set_page_config(page_title="ETF Analytics Pro", layout="wide")

st.markdown("""
    <style>
    /* Fundo principal */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Customização dos Cards */
    .card {
        padding: 20px;
        border-radius: 12px;
        background-color: #1e222d;
        border: 1px solid #2d3139;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: translateY(-5px);
        border-color: #4a4f5a;
    }
    
    /* Textos dentro do Card */
    .ticker-title { color: #ffffff; font-size: 1.4em; font-weight: 700; margin-bottom: 2px; }
    .asset-name { color: #848d9a; font-size: 0.85em; margin-bottom: 15px; }
    .price-label { color: #848d9a; font-size: 0.9em; }
    .price-value { color: #ffffff; font-size: 1.2em; font-weight: 600; }
    .margin-box {
        margin-top: 10px;
        padding: 5px 10px;
        border-radius: 6px;
        text-align: center;
        font-weight: 700;
    }
    
    /* Sidebar e Header */
    [data-testid="stSidebar"] { background-color: #161b22; }
    h1 { color: #ffffff; font-weight: 800; letter-spacing: -1px; }
    h3 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Definição dos ETFs
etfs_config = {
    'IVV': {'nome': '🇺🇸 S&P 500 ETF', 'cor': '#10b981'},
    'VEA': {'nome': '🇺🇸 Developed Markets', 'cor': '#3b82f6'},
    'SOXX': {'nome': '🇺🇸 Semiconductors', 'cor': '#8b5cf6'},
    'IAU': {'nome': '🇺🇸 Gold Trust', 'cor': '#f59e0b'},
    'SIVR': {'nome': '🇺🇸 Silver Trust', 'cor': '#94a3b8'},
    'DIVO11.SA': {'nome': '🇧🇷 Dividendos Brasil', 'cor': '#f97316'}
}

# 3. Sidebar
st.sidebar.title("⚙️ Painel de Controle")
margem_seguranca = st.sidebar.slider("Margem de Segurança (%)", 0, 20, 5) / 100
periodo_grafico = st.sidebar.selectbox("Período do Gráfico", ["6mo", "1y", "2y", "5y"], index=1)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# 4. Busca de Dados
@st.cache_data(ttl=3600)
def buscar_dados_etf(tickers):
    data_dict = {}
    for t in tickers:
        try:
            ticker_obj = yf.Ticker(t)
            hist = ticker_obj.history(period="2y") 
            if hist.empty: continue
            
            preco_atual = hist['Close'].iloc[-1]
            preco_justo = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            data_dict[t] = {
                'preco_atual': preco_atual,
                'preco_justo': preco_justo,
                'historico': hist
            }
        except:
            continue
    return data_dict

dados_etf = buscar_dados_etf(list(etfs_config.keys()))

# 5. Interface Principal
st.title("ETF Analytics Pro 💎")
st.markdown("<p style='color:#848d9a;'>Monitoramento em tempo real de ativos globais e estratégia de preço-teto.</p>", unsafe_allow_html=True)

if dados_etf:
    cols = st.columns(6)
    
    for i, (ticker, config) in enumerate(etfs_config.items()):
        if ticker in dados_etf:
            with cols[i]:
                d = dados_etf[ticker]
                p_teto = d['preco_justo'] * (1 - margem_seguranca)
                margem_real = ((p_teto - d['preco_atual']) / p_teto) * 100
                
                # Definição de Cores Dinâmicas
                cor_status = "#10b981" if d['preco_atual'] <= p_teto else "#ef4444"
                bg_status = "rgba(16, 185, 129, 0.1)" if d['preco_atual'] <= p_teto else "rgba(239, 68, 68, 0.1)"
                moeda = "R$" if ".SA" in ticker else "$"
                
                st.markdown(f"""
                    <div class="card" style="border-top: 4px solid {config['cor']};">
                        <div class="ticker-title">{ticker.replace('.SA', '')}</div>
                        <div class="asset-name">{config['nome']}</div>
                        <span class="price-label">Preço Atual</span><br>
                        <span class="price-value">{moeda}{d['preco_atual']:.2f}</span><br>
                        <div style="margin-top:10px;">
                            <span class="price-label">Preço Teto</span><br>
                            <span style="color:#ffffff; font-weight:600;">{moeda}{p_teto:.2f}</span>
                        </div>
                        <div class="margin-box" style="color:{cor_status}; background-color:{bg_status};">
                            Margem: {margem_real:.1f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 6. Gráfico Detalhado
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📈 Análise de Tendência e Médias")
        
        selecionado = st.selectbox(
            "Filtrar ativo para análise profunda:", 
            options=list(dados_etf.keys()), 
            format_func=lambda x: f"{x.replace('.SA', '')} - {etfs_config[x]['nome']}"
        )
        
        df_plot = dados_etf[selecionado]['historico'].tail(252) # Foco no último ano
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot['Close'], 
            name='Preço de Mercado', 
            line=dict(color=etfs_config[selecionado]['cor'], width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot['Close'].rolling(window=50).mean(), 
            name='Média 50d (Fair Value)', 
            line=dict(color='#ffffff', width=1, dash='dot'),
            opacity=0.5
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#848d9a"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#2d3139'),
            height=450,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.error("Conexão interrompida. Por favor, atualize o painel.")
