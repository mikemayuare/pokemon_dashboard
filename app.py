# %%
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
from math import isnan

load_figure_template("superhero")
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
style = "./assets/style.css"

poke_df = pd.read_csv("data/poke_data.csv", converters={"abilities": pd.eval})
bootstrap = dbc.themes.SUPERHERO
stats = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
types = [
    "bug",
    "dark",
    "dragon",
    "electric",
    "fairy",
    "fight",
    "fire",
    "flying",
    "ghost",
    "grass",
    "ground",
    "ice",
    "normal",
    "poison",
    "psychic",
    "rock",
    "steel",
    "water",
]
# %%

plotly_buttons = {
    "displayModeBar": False,
    "displaylogo": False,
}


def melt_df(df):
    """melt_df melts DataFrame intoa  format suitable
    to the plotly.express.line_radar
    """
    melt_columns = [
        "hp",
        "attack",
        "defense",
        "sp_attack",
        "sp_defense",
        "speed",
        "name",
    ]
    melted_df = df[melt_columns].melt(id_vars=["name"], var_name="stat")
    return melted_df


app = Dash(
    __name__,
    external_stylesheets=[bootstrap, dbc_css, style],
    meta_tags=[  # for responsiveness
        dict(
            name="viewport",
            content="width=device-width, initial-scale=1.0",
        ),
    ],
)

app.title = "Pokémon Dashboard"
app._favicon = "favicon.png"

app.layout = dbc.Container(
    [
        ########## HEADER #############
        dbc.Row(
            html.Div(
                html.Img(
                    src="https://fontmeme.com/permalink/230316/79efd7b7b6559fe97f5374105ae9a3d5.png",
                    className="center",
                    style={"maxHeight": "80px"},
                ),
                style={"backgroundColor": "#ee1515"},
                className="mb-3",
            ),
        ),
        ################# FIRST ROW ################
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="unique-selector",
                            value="bulbasaur",
                            options=[
                                {"label": x.capitalize(), "value": x}
                                for x in poke_df["name"].unique()
                            ],
                            clearable=False,
                            className="pb-1",
                        ),
                        dbc.Card(
                            dbc.CardImg(id="poke-image"),
                            class_name="mb-1",
                        ),
                    ],
                    lg=3,
                    md=12,
                    sm=12,
                    xs=12,
                ),
                dbc.Col(
                    dbc.Card(html.Div(id="poke-description")),
                    lg=3,
                    md=12,
                    sm=12,
                    xs=12,
                    class_name="mb-1",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="poke-bars",
                        config=plotly_buttons,
                    ),
                    lg=6,
                    md=12,
                    sm=12,
                    xs=12,
                    class_name="mb-1",
                ),
            ],
            class_name="me-2 ms-2",
            justify="center",
        ),
        ################ SECOND ROW ################
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="dropdown",
                        value=["bulbasaur", "charmander", "squirtle"],
                        options=[
                            {"label": x.capitalize(), "value": x}
                            for x in poke_df["name"].unique()
                        ],
                        multi=True,
                        clearable=False,
                    ),
                    lg=6,
                    md=12,
                    sm=12,
                    xs=12,
                    class_name="mb-1",
                ),
            ],
            class_name="me-2 ms-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="base-stats-bars",
                        config=plotly_buttons,
                    ),
                    lg=6,
                    md=12,
                    sm=12,
                    xs=12,
                ),
                dbc.Col(
                    dcc.Graph(id="radar-plot", config=plotly_buttons),
                    lg=6,
                    md=12,
                    sm=12,
                    xs=12,
                ),
            ],
            class_name="me-2 ms-2",
        ),
    ],
    class_name="dbc",
    fluid=True,
    style={"fontFamily": "pokemon-gb", "background-color": "#191B1D"},
)


@app.callback(
    Output("poke-image", "src"),
    Output("poke-description", "children"),
    Output("poke-bars", "figure"),
    Input("unique-selector", "value"),
)
def poke_stats(value):
    df = poke_df[poke_df["name"] == value]
    weak_strong_df = df[types].T
    type1 = df["type1"].values[0]
    type2 = f"{'none' if df['type2'].isnull().any() else df['type2'].values[0]}"
    weight = df["weight_kg"].values[0]
    height = df["height_m"].values[0]
    abilities = ", ".join(df["abilities"].values[0])
    v_res_list = []
    res_list = []
    weak_list = []
    inmune_list = []
    for factor, type in zip(weak_strong_df.iloc[:, 0], weak_strong_df.index):
        if factor == 0.25:
            v_res_list.append(type)
        elif factor == 0.5:
            res_list.append(type)
        elif factor == 2:
            weak_list.append(type)
        elif factor == 0:
            inmune_list.append(type)

    very_resistant = "none" if not v_res_list else ", ".join(v_res_list)
    resistant = "none" if not res_list else ", ".join(res_list)
    weak = ", ".join(weak_list)
    inmune = (
        "" if not inmune_list else "Inmune against: " + ", ".join(inmune_list) + "."
    )

    image = df["image"].values[0]
    poke_name = [
        html.H3(
            dbc.CardHeader(
                f'#{df["pokedex_number"].values[0]}: {df["name"].str.capitalize().values[0]}'
            )
        ),
        dbc.CardBody(
            [
                dbc.ListGroupItem(
                    [html.B(f"Abilities: "), f"{abilities}"], class_name="mb-3"
                ),
                dbc.ListGroupItem([html.B("Type 1: "), f"{type1}"]),
                dbc.ListGroupItem([html.B("Type 2: "), f"{type2}"], class_name="mb-2"),
                dbc.ListGroupItem([html.B("Weight: "), f"{weight} kg"]),
                dbc.ListGroupItem(
                    [html.B("Height: "), f"{height} m"], class_name="mb-4"
                ),
                dbc.ListGroupItem(
                    [html.B("Very resistant against: "), f"{very_resistant}."],
                    class_name="mb-2",
                ),
                dbc.ListGroupItem(
                    [html.B("Resistant against: "), f"{resistant}."],
                    class_name="mb-2",
                ),
                dbc.ListGroupItem(
                    [html.B("Weak against: "), f"{weak}."], class_name="mb-2"
                ),
                dbc.ListGroupItem(f"{inmune}", class_name="mb-2"),
            ]
        ),
    ]
    bars_df = df[stats]
    fig = px.bar(
        bars_df.T,
        orientation="h",
        color_discrete_sequence=["#0075BE"],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="#4E5D6C",
    )
    return image, poke_name, fig


@app.callback(
    Output("radar-plot", "figure"),
    Output("base-stats-bars", "figure"),
    Input("dropdown", "value"),
)
def plot_radar(value):
    df = poke_df[poke_df["name"].isin(value)]
    melted = melt_df(df)
    radar = px.line_polar(
        melted, r="value", theta="stat", line_close=True, color="name"
    )
    radar.update_traces(fill="toself")
    radar.update_layout(
        images=[
            dict(
                source="assets/pokeball.png",
                x=0.5,
                y=0.5,
                sizex=1,
                sizey=1,
                xanchor="center",
                yanchor="middle",
                sizing="contain",
                layer="above",
                opacity=0.2,
            )
        ]
    )

    barplot = px.bar(
        df[["name", "base_total"]],
        x="name",
        y="base_total",
        color_discrete_sequence=["#0075BE"],
    )
    barplot.update_traces(marker_line_width=0)
    barplot.update_layout(
        xaxis_title="",
        yaxis_title=("Total Base Abilities"),
        plot_bgcolor="#4E5D6C",
    )
    return radar, barplot


if __name__ == "__main__":
    app.run_server(debug=True)
