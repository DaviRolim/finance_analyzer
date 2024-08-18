import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input, State
from financial_analyzer.data_analysis import analyze_report, save_dashboard_config, load_dashboard_config

def create_dashboard(df: pd.DataFrame):
    """
    Create and run an interactive dashboard using Dash and Plotly.
    """
    app = Dash(__name__)

    # Check if 'date' column exists
    if 'date' not in df.columns:
        print("Warning: 'date' column not found in the DataFrame")
        df['date'] = pd.to_datetime('today')  # Use today's date as a fallback
    else:
        df['date'] = pd.to_datetime(df['date'])

    # Get all available months
    all_months = df['date'].dt.strftime('%Y-%m').unique().tolist()

    # Load the dashboard configuration, if available
    config = load_dashboard_config()
    selected_months = config.get('selected_months', all_months)
    chart_type = config.get('chart_type', 'bar')

    app.layout = html.Div([
        dcc.Store(id='store', data=df.to_dict('records')),
        html.H1('Financial Report Dashboard'),
        
        html.Div([
            html.Label('Select Months:'),
            dcc.Dropdown(
                id='month-selector',
                options=[{'label': month, 'value': month} for month in all_months],
                value=selected_months,
                multi=True
            ),
            html.Label('Select Chart Type:'),
            dcc.Dropdown(
                id='chart-type-selector',
                options=[{'label': chart_type.capitalize(), 'value': chart_type} for chart_type in ['bar', 'line', 'pie']],
                value=chart_type
            ),
            html.Button('Save Configuration', id='save-button', n_clicks=0),
        ]),
        
        html.Div([
            html.H3(id='total-amount'),
        ]),
        
        dcc.Graph(id='monthly-category-chart'),

        html.H2('Top 5 Most Expensive Items by Month'),
        html.Div(id='top-5-items-charts')
    ])

    @callback(
        [Output('total-amount', 'children'),
         Output('monthly-category-chart', 'figure'),
         Output('top-5-items-charts', 'children')],
        [Input('month-selector', 'value'),
         Input('chart-type-selector', 'value')],
        [State('store', 'data')]
    )
    def update_dashboard(selected_months, chart_type, stored_data):
        df = pd.DataFrame(stored_data)
        print(f"Selected months: {selected_months}")
        print(f"Chart type: {chart_type}")

        if not selected_months:
            # If no months are selected, use all available months
            selected_months = all_months

        analysis_results = analyze_report(df, selected_months)
        
        print(f"Analysis results: {analysis_results}")

        total_amount = f"Total Amount: ${analysis_results['total_amount']:,.2f}"
        
        monthly_category_data = pd.DataFrame(analysis_results['monthly_category_totals'])
        
        print(f"Monthly category data:\n{monthly_category_data}")

        if not monthly_category_data.empty and set(['date', 'amount', 'category']).issubset(monthly_category_data.columns):
            if chart_type == 'bar':
                monthly_fig = px.bar(monthly_category_data, x='date', y='amount', color='category',
                                     title='Total Amount by Month and Category')
            elif chart_type == 'line':
                monthly_fig = px.line(monthly_category_data, x='date', y='amount', color='category',
                                      title='Total Amount by Month and Category')
            elif chart_type == 'pie':
                monthly_fig = px.pie(monthly_category_data, values='amount', names='category',
                                     title='Total Amount by Category')
            monthly_fig.update_xaxes(title='Month')
            monthly_fig.update_yaxes(title='Total Amount')
        else:
            monthly_fig = px.bar(title='No data available for Monthly Category Chart')
            monthly_fig.update_layout(
                xaxis={'visible': False},
                yaxis={'visible': False},
                annotations=[{
                    'text': 'No data available for Monthly Category Chart',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20}
                }]
            )
        
        top_5_items_by_month = analysis_results['top_5_items_by_month']
        
        top_5_charts = []
        for month, items in top_5_items_by_month.items():
            if items:
                df = pd.DataFrame(items)
                fig = px.bar(df, x='title', y='amount', title=f'Top 5 Most Expensive Items - {month}')
                fig.update_xaxes(title='Item')
                fig.update_yaxes(title='Amount')
                top_5_charts.append(dcc.Graph(figure=fig))
            else:
                fig = px.bar(title=f'No data available for {month}')
                fig.update_layout(
                    xaxis={'visible': False},
                    yaxis={'visible': False},
                    annotations=[{
                        'text': f'No data available for {month}',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 20}
                    }]
                )
                top_5_charts.append(dcc.Graph(figure=fig))
        
        return total_amount, monthly_fig, top_5_charts

    @callback(
        Output('save-button', 'n_clicks'),
        Input('save-button', 'n_clicks'),
        State('month-selector', 'value'),
        State('chart-type-selector', 'value')
    )
    def save_config(n_clicks, selected_months, chart_type):
        if n_clicks > 0:
            config = {
                'selected_months': selected_months,
                'chart_type': chart_type
            }
            save_dashboard_config(config)
            return 0
        return n_clicks

    app.run_server(debug=True)
