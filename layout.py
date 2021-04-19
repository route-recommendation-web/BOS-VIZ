import dash_html_components as html
import styles as st
import dash_core_components as dcc
import utils
from textwrap import dedent as d
styles = st.styles
layout = html.Div([
    #########################Title
    html.Div([html.H1("Boston Graph")],
             className="row",
             style={'textAlign': "center"}),
    #############################################################################################define the row
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[

                    # html.Div(
                    #     className="twelve columns",
                    #     children=[
                    #         dcc.Markdown(d("""
                    #         **Account To Search**
                    #
                    #         Input the account to visualize.
                    #         """)),
                    #         dcc.Input(id="input1", type="text", placeholder="Account"),
                    #         html.Div(id="output")
                    #     ],
                    #     style={'height': '300px'}
                    # ),
                    html.Div(
                        className="before start",
                        children=[
                            html.Button('play', id='play-val', n_clicks=0, style=styles['button']),
                            html.Button('Restart The Game', id='reset', n_clicks=0, style=styles['button']),
                            html.Pre(id='show-dest', style=styles['pre']),
                            html.Pre(id='edges-blocked', style=styles['pre']),
                            # html.Div(dcc.Input(id='input-on-play', type='text')),
                            # html.Div(id='container-button-basic',
                            # children='Enter a value and press play')
                        ]
                    )
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=utils.next_tic(0, 1))],
            ),

            #########################################right side two output component
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Hover Data**

                            Mouse over values in the graph.
                            """)),
                            html.Pre(id='hover-data', style=styles['pre'])
                        ],
                        style={'height': '400px'}),

                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                             **Click Data**

                             Click anywhere on the graph.
                             """)),
                            html.Pre(id='click-data', style=styles['pre']),
                            html.Button('set as destination', id='set-dest', n_clicks=0, style=styles['button']),
                            html.Button('edit block', id='add-block', n_clicks=0, style=styles['add-block-disable'])
                        ],
                        style={'height': '400px'}
                    )
                ]
            )
        ]
    )
])