import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go

load_figure_template("flatly")
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
style = "./assets/style.css"

poke_df = pd.read_csv("data/poke_data.csv")
bootstrap = dbc.themes.FLATLY
stats = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]

plotly_buttons = {
    "modeBarButtonsToRemove": [
        "zoom2d",
        "pan2d",
        "select2d",
        "lasso2d",
        "zoomIn2d",
        "zoomOut2d",
        "autoScale2d",
        "resetScale2d",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "zoom3d",
        "pan3d",
        "resetCameraDefault3d",
        "resetCameraLastSave3d",
        "hoverClosest3d",
        "orbitRotation",
        "tableRotation",
        "zoomInGeo",
        "zoomOutGeo",
        "resetGeo",
        "hoverClosestGeo",
        "toImage",
        "sendDataToCloud",
        "hoverClosestGl2d",
        "hoverClosestPie",
        "toggleHover",
        "resetViews",
        "toggleSpikelines",
        "resetViewMapbox",
    ],
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
server = app.server
app.title = "Pokémon Dashboard"
app._favicon = "favicon.png"

app.layout = dbc.Container(
    [
        dbc.Row(
            # html.H1("POKÉMON DASHBOARD"),
            # style={
            #     "background-color": "red",
            #     "text-align": "center",
            #     "fontFamily": "Pokemon, sans-serif",
            #     "color": "#eeeeee",
            # },
            # class_name="mb-4 pb-4",
            html.Div(
                html.Img(
                    src="https://fontmeme.com/permalink/230315/b8c6b5d4ddb3dd97bcb8677ef0c4bd1d.png",
                    className="center pb-3 pt-3",
                ),
                style={"backgroundColor": "#ee1515"},
                className="mb-2",
            )
        ),
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
                            html.Img(id="poke-image"),
                            class_name="bg-card",
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(dbc.Card(html.Div(id="poke-description")), width=3),
                dbc.Col(
                    dcc.Graph(
                        id="poke-bars",
                        config=plotly_buttons,
                    ),
                    width=6,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="base-stats-bars", config=plotly_buttons)),
                dbc.Col(
                    [
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
                        dcc.Graph(id="radar-plot", config=plotly_buttons),
                    ],
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
    image = df["image"].values[0]
    description = "place-holder"
    bars_df = df[stats]
    fig = px.bar(
        bars_df.T,
        orientation="h",
        color_discrete_sequence=["#0075BE"],
    )
    return image, description, fig


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
    return radar, barplot


if __name__ == "__main__":
    app.run_server(debug=True)
