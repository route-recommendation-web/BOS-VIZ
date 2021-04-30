import dash_html_components as html
import styles as st
import dash_core_components as dcc
import utils
from textwrap import dedent as d

styles = st.styles
layout = html.Div([
    # ########################Title
    html.Div([html.H1("Boston Graph")],
             className="row",
             style={'textAlign': "center"}),
    # ############################################################################################define the row
    html.Div(
        className="row",
        children=[
            # #############################################left side two input components
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
                            html.Div(
                                className='twelve columns',
                                children=[
                                    dcc.Markdown(d("""
                                    **Play Game**
                            
                                    Click PLAY button to move NPC\n
                                    Click Restart to start over
                                    """)),
                                    html.Button('play', id='play-val', n_clicks=0, style=styles['button']),
                                    html.Button('Restart The Game', id='reset', n_clicks=0, style=styles['button']),
                                ],
                                style={'height': '280px'}),
                            html.Div(
                                className='twelve columns',
                                children=[
                                    dcc.Markdown(d("""
                                    **Game settings**
                            
                                    Move your mouse on the slider to change npc step length
                                    """)),
                                    dcc.Slider(
                                        id='step-slider', min=1, max=5, value=1,
                                        marks={str(i): str(i) for i in range(1, 6)},
                                        step=1),
                                    html.Button('Switch Algorithm', id='switch-algorithm', n_clicks=0,
                                                style=styles['button']),
                                    html.Button('edit block', id='add-block', n_clicks=0, style=styles['add-block-disable']),
                                    # html.Pre(id='show-dest', style=styles['pre']),
                                    html.Pre(id='show-algorithm', style=styles['pre'])
                                ],
                                style={'height': '400px'}),
                            # html.Div(dcc.Input(id='input-on-play', type='text')),
                            # html.Div(id='container-button-basic',
                            # children='Enter a value and press play')
                        ]
                    )
                ]
            ),

            # ###########################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.ConfirmDialog(
        id='confirm',
        message='Game over, restart?',
    ),dcc.Graph(id="my-graph",
                                    figure=utils.next_tic(0, 1))],
            ),

            # ########################################right side two output component
            html.Div(
                className="two columns",
                children=[
                    # html.Div(
                    #     className='twelve columns',
                    #     children=[
                    #         dcc.Markdown(d("""
                    #         **Hover Data**
                    #
                    #         Mouse over values in the graph.
                    #         """)),
                    #         html.Pre(id='hover-data', style=styles['pre'])
                    #     ],
                    #     style={'height': '380px'}),

                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                             **Click Data**

                             Click anywhere on the graph.
                             """)),
                            html.Pre(id='click-data', style=styles['pre']),
                            html.Button('set as destination', id='set-dest', n_clicks=0, style=styles['button']),
                            html.Pre(id='show-dest', style=styles['pre'])
                        ],
                        style={'height': '400px'}
                    )
                ]
            )
        ]
    )
])
