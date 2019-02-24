import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import base64
from dash.dependencies import Input, Output,State
import numpy as np
import matplotlib.pyplot as plt
from plotly import tools
import pickle
import plotly
import plotly.plotly as py
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Main image to be displayed in the App:

main_img = base64.b64encode(open('./img/city.jpg', 'rb').read())

app = dash.Dash(__name__)
server=app.server

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

 ##  data:

values_common=['salary','management','culture','balance','team']

precomputed_companies_list = ['AT&T Inc','Wal-Mart Stores','Nordstrom','Suncor Energy Inc','Wells Fargo & Company',
                              'SAP Ag', 'Capital One Financial Corp', 'Fedex Corp','Citigroup Inc', 'Target Corp',
                              'JP Morgan Chase & CO', 'Thomson Reuters Corp', 'Coca-Cola Company', 'Yelp Inc',
                              'Motorola Solutions', 'Spotify Technology S.A.', 'Morgan Stanley', 'Booz Allen Hamilton Holding Corp',
                              'Bank of Montreal','Pfizer Inc', 'Shopify Inc', 'Best Buy CO', 'Goldman Sachs Group',
                              'Accenture Plc','HSBC Holdings Plc', 'Bank of America Corp', 'Walt Disney Company',
                              'Exxon Mobil Corp', 'CGI Group','Manulife Financial Corp','Visa Inc', 'Boeing Company',
                              'AON Plc', 'Equifax Inc', 'Metlife Inc', 'Deutsche Bank Ag', 'Toronto Dominion Bank',
                              'Kellogg Company', 'CBS Corp', 'Blackberry Ltd', 'General Electric Company',
                              'Procter & Gamble Company', '3M Company', 'Unilever NV', 'American Express Company',
                              'Credit Suisse Group', 'Square', 'Twitter Inc', 'Sun Life Financial Inc', 
                              'Royal Bank of Canada', 'Bank of Nova Scotia', 'Avon Products','Sony Corp', 'Loews Corp',
                              'Mastercard Inc', 'National Bank Holdings Corp', 'Rogers Communication', 
                              'Canadian Imperial Bank of Commerce', 'Fitbit Inc']


precomputed_percentage= pd.read_pickle('./pre_percentage.pickle')
precomputed_score= pd.read_pickle('./pre_scores.pickle')


#### Web App layout:


app.layout = html.Div([
#title:
    html.Div(html.H1('UValue', style = {'textAlign': 'center', 'padding': '2px', 'height': '20px', 'margin-top': '10px', 'fontSize':80,'color': '#1E9DA0'})),
# subtitle:    
    html.Div(html.H3('Helping you find your best place to work', style = {'textAlign': 'center', 'height': '10px','color':'#1B698E', 'fontSize':25, 'margin-top': '10px'})),
# image:    
    html.Div(html.Img(id='head-image', src='data:image/jpeg;base64,{}'.format(main_img.decode('ascii')),
                      style = {'width':'100%', 'height': '300px', 'padding':'0','margin':'0','margin-top': '10px','box-sizing':'border-box'})),

# first input:    
    html.Div(title='select inputs', id='selections',children=[
    html.P('Choose the name of the company:',style = {'fontSize':18}),
# dropdown:
    dcc.Dropdown(
        id='my-dropdown',
        options=[{'label': i, 'value': i} for i in precomputed_companies_list],
        placeholder='Select a Company'
    ),
# second input:    
    html.P('Select what you value, comma separated, one word per value:', style = {'fontSize':18}),
    dcc.Input(
        id='input1',type='text',
        placeholder='(e.g. balance, pay)'
    ),
    html.Button(id='submit-button', n_clicks=0,children='Submit'),
    html.Button(id='reset-button', n_clicks=0,children='reset'),
    html.Div(id='temporal-output')
    ]),
    html.Br(),
    html.Div(id='output-container-button',
             children='Enter a value and press submit'),
    html.Br(),
    html.Br(),
    html.Br(),
# results:
    html.Div(html.H3("RESULTS:", style = {'textAlign': 'center', 'height': '10px', 'fontSize':40,'color':'#1B698E'})),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div(html.H3("Your company's score for each of your selected values:", style = { 'height': '10px', 'fontSize':22})),
    dcc.Graph(
       id='user_graph',
    ),
    html.Div(html.H3('The arrow below points at where in the distribution your company lies for each value:', style = {'height': '10px', 'fontSize':22})),
    dcc.Graph(
       id='user_graph2',
    ),
    html.Div(html.H3('Here is how your company scores in popular categories:', style = { 'height': '10px', 'fontSize':22})),
    dcc.Graph(
        id='user_graph3'
    )


])


## Buttons:
#reset:
@app.callback(
    dash.dependencies.Output('input1', 'value'),
    [dash.dependencies.Input('reset-button', 'n_clicks')]
)
def reset(click):
    if (click !=0):
        return ('')


# message:
@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('input1', 'value')])
def update_output(n_clicks, value):
    if (n_clicks != 0):
        try:
            return html.Div(html.H3("The input values were '{}', if there is no output, or\
            the output doesn't change, I couldn't find one of them in my memory, try with different words!".format(
            value
            ),style = {'textAlign': 'center', 'height': '10px', 'fontSize':26}))
        except KeyError:
            return html.Div(html.H3("The input values were '{}', if there is no output222, or\
            the output doesn't change, I couldn't find one of them in my memory, try with different words!".format(
            value
            ),style = {'textAlign': 'center', 'height': '10px', 'fontSize':26}))




## Boxplot:


@app.callback(
    dash.dependencies.Output(component_id='user_graph2', component_property='figure'),
    [dash.dependencies.Input('submit-button','n_clicks'),
    dash.dependencies.Input('reset-button', 'n_clicks')],
    [State('my-dropdown','value'),
    State('input1','value'),
 ])
def update_output(subclick, resetclick, company_name, values_list):
    try:
        arr=(values_list.replace(' ','')).split(',')
        y_pro=[]
        x_pro=[]
        for value in arr:
            for company in precomputed_companies_list:
                y_pro.append(precomputed_percentage[value,company,'pros'])
                x_pro.append(value)
        y_con=[]
        x_con=[]
        for value in arr:
            for company in precomputed_companies_list:
                y_con.append(precomputed_percentage[value,company,'cons'])
                x_con.append(value)
        trace1=go.Box(
        y=y_pro,
        x=x_pro,
        name = 'positive',
        marker = dict(
        color = 'rgb(26, 118, 255)',

            )
        )
        trace2=go.Box(
        y=y_con,
        x=x_con,
        name = 'negative',
        marker = dict(
        color = 'rgb(55, 83, 109)'
            )
        )
        data = [trace1,trace2]

        annot=[]
        n=0
        for value in arr:
            dict1=dict(
                x=n-.175,
                y=precomputed_percentage[value, company_name,'pros'],
                showarrow=True,
                ax=40,
                ay=0,
                arrowhead=1,
                arrowcolor = "black",
                arrowsize = 1,
                arrowwidth = 3,
                xanchor = "left",
                yanchor = "bottom"
            )
            annot.append(dict1)
            dict2=dict(
                x=n+.175,
                y=precomputed_percentage[value, company_name,'cons'],
                showarrow=True,
                ax=40,
                ay=0,
                arrowhead=1,
                arrowcolor = "black",
                arrowsize = 1,
                arrowwidth = 3,
                xanchor = "left",
                yanchor = "bottom"
            )
            annot.append(dict2)
            n=n+1
            print(n)
        layout = go.Layout(
            yaxis=dict(
            title='SCORE',
            titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'),
            zeroline=False
            ),
            boxmode='group',
            annotations=annot
            
        )
        fig = go.Figure(data=data, layout=layout)
            
        return fig
    except AttributeError:
        pass




## Bar charts for input values:


@app.callback(
    dash.dependencies.Output(component_id='user_graph', component_property='figure'),
    [dash.dependencies.Input('submit-button','n_clicks'),
    dash.dependencies.Input('reset-button', 'n_clicks')],
    [State('my-dropdown','value'),
    State('input1','value'),
 ])
def update_output(subclick, resetclick, company_name, values_list):
    try:
        arr=(values_list.replace(' ','')).split(',')
        traces = []
        for value in arr:
            height_pro=precomputed_percentage[value,company_name,'pros']
            height_con=precomputed_percentage[value,company_name,'cons']
            labels=['positive', 'negative']
            values=[height_pro, height_con]
            colors=['rgb(26, 118, 255)', 'rgb(55, 83, 109)', '#82D6D8']
            trace = go.Bar(x = labels,
                           y = values,
                           name=value,
                           )
            traces.append(trace)
            
           
        layout = go.Layout(
            title='Scores for your selected values',
            xaxis=dict(
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            yaxis=dict(
                title='SCORE',
                titlefont=dict(
                    size=16,
                    color='rgb(107, 107, 107)'
                ),
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            legend=dict(
                x=1.0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1
        )
        fig = go.Figure(data = traces, layout = layout)
            
        return fig
    except AttributeError:
        pass


## Bar chart for common values:

@app.callback(
    dash.dependencies.Output(component_id='user_graph3', component_property='figure'),
    [dash.dependencies.Input('submit-button','n_clicks'),
    dash.dependencies.Input('reset-button', 'n_clicks')],
    [State('my-dropdown','value'),
    State('input1','value'),
 ])
def update_output(subclick, resetclick, company_name, values_list):
    try:

        arr=(values_list.replace(' ','')).split(',')
        height_p, height_c=precomputed_score[company_name]
        N = len(height_p)
        final_height_pro = height_p
        final_height_con = height_c
        trace1 = go.Bar(
            x=values_common,
            y=final_height_pro,
            name='Positive',
            marker=dict(
                color='rgb(26, 118, 255)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
                ),
            opacity=0.8
        )

        trace2 = go.Bar(
            x=values_common,
            y=final_height_con,
            name='Negative',
            marker=dict(
                color='rgb(55, 83, 109)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
                ),
            opacity=0.8
        )

        traces = [trace1,trace2]

        layout = go.Layout(
            title='Scores for popular values',
            xaxis=dict(
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            yaxis=dict(
                title='SCORE',
                titlefont=dict(
                    size=16,
                    color='rgb(107, 107, 107)'
                ),
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            legend=dict(
                x=1.0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1
        )
        fig = go.Figure(data = traces, layout=layout)
        return fig
    except AttributeError:
        pass



if __name__ == '__main__':
    app.run_server(debug=True)

