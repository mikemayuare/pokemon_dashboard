# %%
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
from math import isnan

load_figure_template("flatly")
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
style = "./assets/style.css"
bootstrap = dbc.themes.PULSE
title_size = 30
poke_df = pd.read_csv("data/poke_data.csv", converters={"abilities": pd.eval})
# %%
dropdown_options = [
    {"label": f"#{y} " + x.capitalize(), "value": x}
    for x, y in zip(poke_df["name"], poke_df["pokedex_number"])
]

type_matrix = pd.read_csv("data/type_chart.csv", index_col="Attacking")

stats = [
    "health points",
    "attack",
    "defense",
    "special attack",
    "special defense",
    "speed",
]
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

plotly_buttons = {
    "displayModeBar": False,
    "displaylogo": False,
    "scrollZoom": False,
}

hoverlabel = dict(font_size=15)


def melt_df(df):
    """melt_df melts DataFrame intoa  format suitable
    to the plotly.express.line_radar
    """
    melt_columns = [
        "health points",
        "attack",
        "defense",
        "special attack",
        "special defense",
        "speed",
        "name",
    ]
    melted_df = df[melt_columns].melt(id_vars=["name"], var_name="stat")
    return melted_df


treemap = px.treemap(
    poke_df,
    path=[px.Constant("All pokémons"), "generation", "type1", "type2", "name"],
    title="Pokémons by generation and type",
)
treemap.update_traces(
    marker_cornerradius=5,
    maxdepth=2,
    hovertemplate="<b>%{label}</b>" + "<br>%{value} <b>pokémons</b></br>",
)
treemap.update_layout(
    height=600,
    title_x=0.5,
    title_font_size=title_size,
    font=dict(size=18),  # CHANGE :Size of the font in treemap
    hoverlabel=hoverlabel,
)

heatmap = px.imshow(
    type_matrix,
    text_auto=True,
    aspect="auto",
    title="Damage multiplier by type",
    color_continuous_scale=[(0, "red"), (0.5, "white"), (1, "green")],
)
heatmap.update_traces(
    hovertemplate="<b>Attacking</b>: %{y}"
    + "<br><b>Defending</b>: %{x}</br>"
    + "<b>Multiplier</b>: %{z}"
)
heatmap.update_layout(
    coloraxis_showscale=False,
    height=600,
    # yaxis_autorange="reversed",
    yaxis_showgrid=False,
    xaxis_title="Defending",
    xaxis_showgrid=False,
    title_x=0.5,
    title_font_size=title_size,
    hoverlabel=hoverlabel,
)

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
server = app.server

app.layout = dbc.Container(
    [
        ########## HEADER #############
        dbc.Row(
            html.Div(
                html.Img(
                    src="assets/headerlogo.png",
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
                            options=dropdown_options,
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
                        value=["bulbasaur", "ivysaur", "venusaur"],
                        options=dropdown_options,
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
        ###### third row
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure=treemap, config=plotly_buttons),
                    lg=6,
                    md=12,
                    sm=12,
                    xs=12,
                ),
                dbc.Col(
                    dcc.Graph(figure=heatmap, config=plotly_buttons),
                    lg=6,
                    md=12,
                    sm=12,
                    xs=12,
                ),
            ]
        ),
    ],
    class_name="dbc",
    fluid=True,
    style={"fontFamily": "pokemon-gb"},
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
        html.H3(dbc.CardHeader("Pokédex", style={"fontSize": "0,6em"})),
        dbc.CardBody(
            [
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.B(f"Abilities: "), f"{abilities}"],
                        ),
                        dbc.ListGroupItem([html.B("Type 1: "), f"{type1}"]),
                        dbc.ListGroupItem(
                            [html.B("Type 2: "), f"{type2}"],
                        ),
                        dbc.ListGroupItem([html.B("Weight: "), f"{weight} kg"]),
                        dbc.ListGroupItem(
                            [html.B("Height: "), f"{height} m"],
                        ),
                        dbc.ListGroupItem(
                            [html.B("Very resistant against: "), f"{very_resistant}."],
                        ),
                        dbc.ListGroupItem(
                            [html.B("Resistant against: "), f"{resistant}."]
                        ),
                        dbc.ListGroupItem([html.B("Weak against: "), f"{weak}."]),
                        dbc.ListGroupItem(html.B(f"{inmune}")),
                    ]
                )
            ],
            style={"fontSize": "0.7em"},
        ),
    ]
    bars_df = df[stats].T
    bars_df.columns = ["name"]
    fig = px.bar(
        bars_df,
        x="name",
        orientation="h",
        color_discrete_sequence=["#0075BE"],
    )
    fig.update_traces(hovertemplate="%{x} points")
    fig.update_layout(
        title="Base stats",
        font_size=16,
        xaxis_title="",
        yaxis_categoryorder="total ascending",
        # Forbid the user to zoom in in the axes
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        showlegend=False,
        title_x=0.5,
        title_font_size=title_size,
        hoverlabel=hoverlabel,
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
                opacity=0.1,
            )
        ],
        hoverlabel=hoverlabel,
        font_size=16,
    )

    barplot = px.bar(
        df[["name", "base_total"]],
        x="name",
        y="base_total",
        color_discrete_sequence=["#0075BE"],
    )
    barplot.update_traces(hovertemplate="<b>%{x}</b>: %{y} points")
    barplot.update_layout(
        xaxis_title="",
        xaxis_categoryorder="total descending",
        yaxis_title=("Total base abilities"),
        # Forbid user to zoom in the axes
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        hoverlabel=hoverlabel,
    )
    return radar, barplot


if __name__ == "__main__":
    app.run_server(debug=True)
