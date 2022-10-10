import dash
# import dash_core_components as dcc
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# creating a dummy sales dataframe
# product_sales = {'vendors':['VANS','VANS','VANS','VANS','NIKE','NIKE','NIKE','ADIDAS','ADIDAS','CONVERSE','CONVERSE','CONVERSE'],
#                  'products': ['Tshirts','Sneakers','Caps','Clothing','Sports Outfit','Sneakers','Caps','Accessories','Bags','Sneakers','Accessories','Tshirts'],
#                  'units sold': [2,15,3,8,37,13,7,4,12,7,8,2]
#                  }
# product_sales_df = pd.DataFrame(product_sales)
product_sales_df = pd.read_csv('mms.csv', encoding= 'unicode_escape')

# all vendors sales pie chart
def sales_pie():
    df = product_sales_df.groupby('regional').sum().reset_index()
    fig = px.pie(df, names='regional',
                 values='actual', hole=0.4)
    fig.update_layout(template='presentation', title='Sales actual per region')
    return fig

# creating app layout
app.layout = dbc.Container([
    dbc.Card([
            dbc.Button('<', id='back-button', outline=True, size="sm",
                        className='mt-2 ml-2 col-1', style={'display': 'none'}),
            dbc.Row(
                dcc.Graph(
                        id='graph',
                        figure=sales_pie()
                    ), justify='center'
            )
    ], className='mt-3')
])

#Callback
@app.callback(
    Output('graph', 'figure'),
    Output('back-button', 'style'), #to hide/unhide the back button
    Input('graph', 'clickData'),    #for getting the vendor name from graph
    # Input('graph', 'n_clicks'),    #for getting the vendor name from graph
    Input('back-button', 'n_clicks')
)
def drilldown(click_data,n_clicks):

    # using callback context to check which input was fired
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == 'graph':

        # get vendor name from clickData
        if click_data is not None:
            regional = click_data['points'][0]['label']

            if regional in product_sales_df.regional.unique():
                # creating df for clicked vendor
                regional_sales_df = product_sales_df[product_sales_df['regional'] == regional]

                # generating product sales bar graph
                # fig = px.bar(regional_sales_df, x='cabang',
                #              y='actual', color='cabang')
                fig = px.bar(regional_sales_df, x="cabang", y="actual",
                            color='supervisor', barmode='group',
                            height=400)
                fig.update_layout(title='<b>{} sales by cabang<b>'.format(regional),
                                  showlegend=False, template='presentation')
                return fig, {'display':'block'}     #returning the fig and unhiding the back button
            if regional in product_sales_df.cabang.unique():
                # creating df for clicked vendor
                cabang_sales_df = product_sales_df[product_sales_df['cabang'] == regional]
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=cabang_sales_df['supervisor'],
                    y=cabang_sales_df['actual'],
                    name='Actual Sales',
                    marker_color='indianred'
                ))
                fig.add_trace(go.Bar(
                    x=cabang_sales_df['supervisor'],
                    y=cabang_sales_df['target'],
                    name='Target Sales',
                    marker_color='lightsalmon'
                ))
                
                fig.update_layout(title='<b>{} sales by supervisor<b>'.format(regional),
                                  showlegend=True, template='presentation')
                return fig, {'display':'block'}     #returning the fig and unhiding the back button  
            else:
                return sales_pie(), {'display': 'none'}     #hiding the back button
        
        
    else:
        return sales_pie(), {'display':'none'}

if __name__ == '__main__':
    app.run_server(debug=True)