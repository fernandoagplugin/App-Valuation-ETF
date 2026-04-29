import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configurações da Página
st.set_page_config(page_title="Dashboard ETFs Internacionais", layout="wide")

# Estilos Visuais
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .card { padding: 15px; border-radius: 10px; background-color: white; box-shadow: 1px 1px 5px rgba(0,0,0,0.05); min-height: 160px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Definição dos ETFs (DIVO11 movido para o final e com bandeiras)
etfs_config = {
    'IVV': {'nome': '🇺🇸 S&P 500 ETF', 'cor': '#27ae60'},
    'VEA': {'nome': '🇺🇸 Developed Markets', 'cor': '#2980b9'},
    'SOXX': {'nome': '🇺🇸 Semiconductors', 'cor': '#8e44ad'},
    'IAU': {'nome': '🇺🇸 Gold Trust', 'cor': '#f1c40f'},
    'SIVR': {'nome': '🇺🇸 Silver Trust', 'cor': '#95a5a6'},
    'DIVO11.SA': {'nome': '🇧🇷 Dividendos Brasil', 'cor': '#e67e22'} # Agora no final
}

# 3. Sidebar
st.sidebar.header("📊 Configurações")
margem_seguranca = st.sidebar.slider("Margem de Segurança (%)", 0, 20, 5) / 100
periodo_grafico = st.sidebar.selectbox("Período do Gráfico", ["6mo", "1y", "2y", "5y"], index=1)

if st.sidebar.button("🔄 Forçar Update"):
    st.cache_data.clear()
    st.rerun()

# 4. Busca de Dados
@st.cache_data(ttl=3600)
def buscar_dados_etf(tickers, period):
    data_dict = {}
    for t in tickers:
        try:
            ticker_obj = yf.Ticker(t)
            # Aumentamos um pouco o histórico buscado para garantir que a média móvel tenha dados suficientes
            hist = ticker_obj.history(period="2y") 
            if hist.empty: continue
            
            preco_atual = hist['Close'].iloc[-1]
            # Preço Justo: Média móvel de 50 dias
            preco_justo = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            data_dict[t] = {
                'preco_atual': preco_atual,
                'preco_justo': preco_justo,
                'historico': hist
            }
        except Exception as e:
            print(f"Erro ao buscar {t}: {e}")
            continue
    return data_dict

dados_etf = buscar_dados_etf(list(etfs_config.keys()), periodo_grafico)

# 5. Interface
st.title("🌎 Monitor de Estratégia de ETFs")

if dados_etf:
    # Cria 6 colunas para os 6 ativos
    cols = st.columns(6)
    
    for i, (ticker, config) in enumerate(etfs_config.items()):
        if ticker in dados_etf:
            with cols[i]:
                d = dados_etf[ticker]
                p_teto = d['preco_justo'] * (1 - margem_seguranca)
                margem_real = ((p_teto - d['preco_atual']) / p_teto) * 100
                cor_status = "#28a745" if d['preco_atual'] <= p_teto else "#dc3545"
                
                # Lógica de Moeda baseada na bandeira/ticker
                moeda = "R$" if ".SA" in ticker else "$"
                ticker_display = ticker.replace(".SA", "")
                
                st.markdown(f"""
                    <div class="card" style="border-top: 5px solid {config['cor']};">
                        <b style="font-size:1.1em;">{ticker_display}</b><br>
                        <span style="color:gray; font-size:0.75em;">{config['nome']}</span><hr style="margin: 8px 0;">
                        Preço: <b>{moeda}{d['preco_atual']:.2f}</b><br>
                        Teto: <b>{moeda}{p_teto:.2f}</b><br>
                        <span style="color:{cor_status};">Margem: <b>{margem_real:.1f}%</b></span>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 6. Gráfico Detalhado
    st.subheader("📈 Análise de Tendência")
    # Formatador para remover o .SA do seletor do gráfico
    selecionado = st.selectbox(
        "Selecione o ativo para ver o detalhe:", 
        options=list(dados_etf.keys()), 
        format_func=lambda x: f"{x.replace('.SA', '')} ({etfs_config[x]['nome']})"
    )
    
    df_plot = dados_etf[selecionado]['historico']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], name='Preço', line=dict(color=etfs_config[selecionado]['cor'])))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'].rolling(window=50).mean(), name='Preço Justo (Média 50d)', line=dict(color='black', dash='dot')))
    
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Dados não encontrados. Verifique a conexão ou clique em Forçar Update.")
