from click import style
import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.express as px


df = pd.read_excel("vendas_veiculos.xlsx")

df['data_venda'] = pd.to_datetime(df['data_venda'], dayfirst=True)

# Extração de ano, mês e semana para filtros e análises
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month
df['semana'] = df['data_venda'].dt.isocalendar().week

# Crição do app web
app = Dash(__name__)


style_cards = {
    'backgroundColor': '#f9f9f9',
    'padding': '20px',
    'marginBottom': '20px',
    'borderRadius': '5px',
    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
}

style_dropdown = {
    'width': '100%',
    'padding': '15px',
    'fontSize': '20px',
    'borderRadius': '10px',
    'border': '1px solid #ccc'
}


app.layout = html.Div([

    html.Br(),

    # TÍTULO DASHBOARD
    html.H1("Dashboard de Vendas de Veículos", 
        style={
        'textAlign': 'center',
        'marginBottom': '60px',
        'fontFamily': 'Segoe UI, Arial, sans-serif',
        'color': '#2c2c2c',
        'fontWeight': '700',
        'fontSize': '42px',
        'letterSpacing': '1px',
        'textTransform': 'uppercase'
    }
),


    # FILTROS
    html.Div([
        
        html.Label("Selecione o Ano"),
        dcc.Dropdown(
        id='filtro_ano',
        options=[{'label': ano, 'value': ano} for ano in sorted(df['ano'].unique())],
        value=sorted(df['ano'].unique())[-1],
        style=style_dropdown
        ),

        html.Br(),
        html.Label("Selecione o Mês"),
        dcc.Dropdown(
            id='filtro_mes',
            options=[{'label': mes, 'value': mes} for mes in sorted(df['mes'].unique())] +
                    [{'label': 'Todas', 'value': 'todas'}],
            value='todas',
            style=style_dropdown
        ),

        html.Br(),
        html.Label("Selecione a Marca"),
        dcc.Dropdown(
            id='filtro_marca',
            options=[{'label': m, 'value': m} for m in df['marca'].unique()] +
                    [{'label': 'Todas', 'value': 'todas'}],
            value='todas',
            style=style_dropdown
        )

    ], style={'width': '25%', 'float': 'left', 'padding': '20px'}),


    # CONTEÚDOS
    html.Div([

        # Cards
        html.Div(id='cards_resumo',
                 style={'marginBottom': '40px'}),

        # Gráfico
        dcc.Graph(id='grafico_semana'),

        # Tabela
        dash_table.DataTable(
            id='tabela_vendas',
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

    ], style={'width': '70%', 'float': 'right', 'padding': '20px'})

])


# Callback para atualizar os componentes com base nos filtros

@app.callback(

    # O que será atualizado:
    [
        Output('cards_resumo', 'children'),   # Painel com números
        Output('grafico_semana', 'figure'),   # Gráfico
        Output('tabela_vendas', 'data'),      # Dados da tabela
        Output('tabela_vendas', 'columns')    # Colunas da tabela
    ],

    [
        Input('filtro_ano', 'value'),
        Input('filtro_mes', 'value'),
        Input('filtro_marca', 'value')
    ]
)
def atualizar_dashboard(ano, mes, marca):
    """
    Esta função roda TODA VEZ que o usuário muda um filtro.
    E atualiza o card, o gráfico e a tabela automaticamente.
    """

    # Filtro do DataFrame

    df_filtro = df[(df['ano'] == ano) & (df['mes'] == mes)]

    if ano != 'todas':
        df_filtro = df_filtro[df_filtro['ano'] == ano]

    if mes != 'todas':
        df_filtro = df_filtro[df_filtro['mes'] == mes]

    if marca != 'todas':
        df_filtro = df_filtro[df_filtro['marca'] == marca]


    # Métricas gerais
    total_vendas = len(df_filtro)  # Total de vendas no mês
    valor_total = df_filtro['valorvenda'].sum()  # Valor total vendido

    # Quantidade de vendas da marca selecionada
    if marca == 'todas':
        vendas_marca = "Selecione uma marca"
    else:
        vendas_marca = len(df_filtro)


    # Cards

    cards = html.Div([
html.Div([
        html.H3("Total de vendas no mês"),
        html.H2(total_vendas)
    ], style={
        'backgroundColor': '#007bff',
        'color': 'white',
        'fontSize': '20px',
        'padding': '20px',
        'border': '1px solid #ccc',
        'borderRadius': '10px',
        'marginRight': '20px',
        'textAlign': 'center',
        'width': '30%'
    }),

    html.Div([
        html.H3("Valor total vendido"),
        html.H2(f"R$ {valor_total:,.2f}")
    ], style={
        'backgroundColor': '#28a745',
        'color': 'white',
        'fontSize': '20px',
        'padding': '20px',
        'border': '1px solid #ccc',
        'borderRadius': '10px',
        'marginRight': '20px',
        'textAlign': 'center',
        'width': '30%'
    }),

    html.Div([
        html.H3("Vendas da marca selecionada"),
        html.H2(vendas_marca)
    ], style={
        'backgroundColor': '#ff8800',
        'color': 'white',
        'fontSize': '20px',
        'padding': '20px',
        'border': '1px solid #ccc',
        'borderRadius': '10px',
        'marginRight': '20px',
        'textAlign': 'center',
        'width': '30%'
    }),

], style={
    'display': 'flex',
    'flexDirection': 'row',
    'justifyContent': 'space-between'
})


    # Gráfico por semana

    if len(df_filtro) > 0:
        vendas_semana = df_filtro.groupby('semana').sum(numeric_only=True).reset_index()
        fig = px.bar(vendas_semana, x='semana', y='valorvenda',
                     title="Vendas por Semana")
    else:
        fig = px.bar(title="Sem dados para exibir neste período")


    # Tabela de dados filtrados

    dados = df_filtro.to_dict('records')
    colunas = [{"name": c, "id": c} for c in df_filtro.columns]


    # O retorno deve seguir a ORDEM dos Outputs do callback
    return cards, fig, dados, colunas


# Rodar o servidor

def new_func(__name__, app):
    if __name__ == "__main__":
        app.run(debug=True)

new_func(__name__, app)