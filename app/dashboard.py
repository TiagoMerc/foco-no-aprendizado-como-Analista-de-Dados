# Criando um dashboard interativo com Dash para visualização dos dados de arrecadação federal do Brasil
#  utilizando o framework Dash e Plotly.

# Fazendo importação das bibliotecas necessárias

import dash
from dash import dcc, html

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os


# Caminhos dos arquivos de dados 
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
natureza_path = os.path.join(data_dir, 'arrecadacao-natureza.csv')
cnae_path = os.path.join(data_dir, 'arrecadacao-cnae.csv')
ir_ipi_path = os.path.join(data_dir, 'arrecadacao-ir-ipi.csv')

# Carregando dados
natureza_df = pd.read_csv(natureza_path, encoding='latin1', sep=';')
cnae_df = pd.read_csv(cnae_path, encoding='latin1', sep=';')
ir_ipi_df = pd.read_csv(ir_ipi_path, encoding='latin1', sep=';')

# Converter colunas numéricas para float
for col in ['Arrecadação Líquida', 'Compensação', 'Restituição', 'Retificação']:
    if col in ir_ipi_df.columns:
        ir_ipi_df[col] = (
            ir_ipi_df[col]
            .astype(str)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
        ir_ipi_df[col] = pd.to_numeric(ir_ipi_df[col], errors='coerce')

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Br(),
    html.H1('Dashboard Interativo da Arrecadação Federal', style={"textAlign": "center", "color": "#2c3e50"}),
    html.P("Este painel apresenta uma análise detalhada da arrecadação federal brasileira, destacando tendências, variações e o impacto de eventos sobre os tributos. Explore as abas para descobrir insights e storytelling dos dados.", style={"textAlign": "center", "fontSize": "18px"}),
    html.Br(),
    html.Div([
        html.Div([
            html.H4(f"R$ {ir_ipi_df['Arrecadação Líquida'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style={"color": "#fff", "backgroundColor": "#2980b9", "padding": "10px", "borderRadius": "8px"}),
            html.P("Arrecadação Líquida Total", style={"textAlign": "center"})
        ], style={"width": "24%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
        html.Div([
            html.H4(int(ir_ipi_df.groupby('Ano')['Arrecadação Líquida'].sum().idxmax()), style={"color": "#fff", "backgroundColor": "#16a085", "padding": "10px", "borderRadius": "8px"}),
            html.P("Ano mais arrecadado", style={"textAlign": "center"})
        ], style={"width": "24%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
        html.Div([
            html.H4(ir_ipi_df.groupby('Tributo')['Arrecadação Líquida'].sum().idxmax(), style={"color": "#fff", "backgroundColor": "#27ae60", "padding": "10px", "borderRadius": "8px"}),
            html.P("Tributo destaque", style={"textAlign": "center"})
        ], style={"width": "24%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
        html.Div([
            html.H4(f"{ir_ipi_df.groupby('Ano')['Arrecadação Líquida'].sum().pct_change().max()*100:.2f}%", style={"color": "#fff", "backgroundColor": "#f39c12", "padding": "10px", "borderRadius": "8px"}),
            html.P("Variação máxima anual (%)", style={"textAlign": "center"})
        ], style={"width": "24%", "display": "inline-block", "verticalAlign": "top", "margin": "1%"}),
    ], style={"width": "100%", "textAlign": "center"}),
    html.Br(),
    dcc.Tabs([
        dcc.Tab(label='Natureza Jurídica', children=[
            html.Br(),
            html.P("Acompanhe a arrecadação por diferentes naturezas jurídicas e identifique os segmentos que mais contribuem para a receita federal.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='natureza-graph',
                figure=px.bar(natureza_df, x=natureza_df.columns[0], y=natureza_df.columns[-1],
                              title='Arrecadação por Natureza Jurídica', color=natureza_df.columns[0], template="plotly_white")
            )
        ]),
        dcc.Tab(label='CNAE', children=[
            html.Br(),
            html.P("Visualize a arrecadação por setores econômicos (CNAE) e descubra quais atividades impulsionam a receita.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='cnae-graph',
                figure=px.bar(cnae_df, x=cnae_df.columns[0], y=cnae_df.columns[-1],
                              title='Arrecadação por CNAE', color=cnae_df.columns[0], template="plotly_white")
            )
        ]),
        dcc.Tab(label='IR e IPI', children=[
            html.Br(),
            html.P("Explore a arrecadação detalhada de IR e IPI ao longo do tempo e identifique padrões e sazonalidades.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='ir-ipi-graph',
                figure=px.line(ir_ipi_df, x=ir_ipi_df.columns[0], y=ir_ipi_df.columns[-1],
                               title='Arrecadação de IR e IPI detalhada', color=ir_ipi_df['Tributo'], template="plotly_white")
            )
        ]),
        dcc.Tab(label='Análise Descritiva IR x IPI', children=[
            html.Br(),
            html.P("Veja a evolução comparativa entre IR e IPI, destacando mudanças e eventos que impactaram a arrecadação.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='comparacao-ir-ipi',
                figure=px.line(
                    ir_ipi_df.groupby(['Ano', 'Tributo'])['Arrecadação Líquida'].sum().reset_index(),
                    x='Ano', y='Arrecadação Líquida', color='Tributo', 
                    title='Arrecadação Líquida Total por Ano e Tributo', template="plotly_white"
                )
            )
        ]),
        dcc.Tab(label='Variação Anual', children=[
            html.Br(),
            html.P("Acompanhe a variação anual da arrecadação líquida e identifique anos de maior crescimento ou queda.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='variacao-anual',
                figure=px.bar(
                    ir_ipi_df.groupby('Ano')['Arrecadação Líquida'].sum().pct_change().reset_index().fillna(0),
                    x='Ano', y='Arrecadação Líquida',
                    title='Variação Percentual Anual da Arrecadação Líquida (%)',
                    labels={'Arrecadação Líquida': 'Variação (%)'}, template="plotly_white"
                )
            )
        ]),
        dcc.Tab(label='Impacto de Eventos', children=[
            html.Br(),
            html.P("Analise o impacto percentual de compensações, restituições e retificações sobre a arrecadação líquida em cada ano.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='impacto-eventos',
                figure=go.Figure(
                    data=[
                        go.Bar(
                            name=evento,
                            x=ir_ipi_df['Ano'].unique(),
                            y=[
                                ir_ipi_df[(ir_ipi_df['Ano'] == ano)][evento].sum() / ir_ipi_df[(ir_ipi_df['Ano'] == ano)]['Arrecadação Líquida'].sum() * 100
                                if ir_ipi_df[(ir_ipi_df['Ano'] == ano)]['Arrecadação Líquida'].sum() != 0 else 0
                                for ano in ir_ipi_df['Ano'].unique()
                            ],
                        ) for evento in ['Compensação', 'Restituição', 'Retificação']
                    ],
                    layout=go.Layout(
                        barmode='group',
                        title='Impacto (%) de Eventos sobre a Arrecadação Líquida por Ano',
                        xaxis_title='Ano',
                        yaxis_title='Impacto (%)',
                        template='plotly_white'
                    )
                )
            )
        ]),
        dcc.Tab(label='Projeção Futura', children=[
            html.Br(),
            html.P("Veja a projeção da arrecadação líquida para os próximos anos, baseada na média móvel dos últimos anos.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='projecao-futura',
                figure=(
                    lambda: (
                        lambda ts, forecast_df: go.Figure(
                            [go.Scatter(x=ts.index, y=ts[tributo], mode='lines+markers', name=f'{tributo} (histórico)') for tributo in ts.columns] +
                            [go.Scatter(x=forecast_df.index, y=forecast_df[tributo], mode='lines+markers', name=f'{tributo} (previsão)', line=dict(dash='dash')) for tributo in forecast_df.columns],
                            layout=go.Layout(title='Tendência Futura da Arrecadação Líquida por Tributo', xaxis_title='Ano', yaxis_title='Arrecadação Líquida', template='plotly_white')
                        )
                    )(
                        (lambda dados_grafico: dados_grafico.pivot(index='Ano', columns='Tributo', values='Arrecadação Líquida').sort_index())(
                            ir_ipi_df.groupby(['Ano', 'Tributo'])['Arrecadação Líquida'].sum().reset_index()
                        ),
                        (lambda ts: (
                            lambda ts, horizon=3: pd.DataFrame({
                                tributo: np.full(horizon, ts[tributo].rolling(3, min_periods=1).mean().iloc[-1])
                                for tributo in ts.columns
                            }, index=np.arange(ts.index.max() + 1, ts.index.max() + 1 + horizon))
                        )(ts)
                        )(
                            (lambda dados_grafico: dados_grafico.pivot(index='Ano', columns='Tributo', values='Arrecadação Líquida').sort_index())(
                                ir_ipi_df.groupby(['Ano', 'Tributo'])['Arrecadação Líquida'].sum().reset_index()
                            )
                        )
                    )
                )()
            )
        ]),
        dcc.Tab(label='Crescimento por Tributo', children=[
            html.Br(),
            html.P("Compare o crescimento médio anual dos diferentes tributos e identifique os que mais evoluíram.", style={"fontSize": "16px"}),
            dcc.Graph(
                id='crescimento-tributo',
                figure=(lambda ts: px.bar(
                    ts.pct_change().mean() * 100,
                    title='Crescimento Médio Anual por Tributo (%)',
                    labels={'value': 'Crescimento (%)', 'index': 'Tributo'}, template="plotly_white"
                ))(
                    (lambda dados_grafico: dados_grafico.pivot(index='Ano', columns='Tributo', values='Arrecadação Líquida').sort_index())(
                        ir_ipi_df.groupby(['Ano', 'Tributo'])['Arrecadação Líquida'].sum().reset_index()
                    )
                )
            )
        ]),
    ])
])

if __name__ == '__main__': # Executando o servidor da aplicação
    app.run(debug=True) # Rodando o servidor em modo debug