# %%
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px

poke_df = pd.read_csv("data/poke_data.csv")
stats = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
# %%


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


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
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
                        ),
                        dbc.Card(html.Img(id="poke-image")),
                    ],
                    width=3,
                ),
                dbc.Col(dbc.Card(html.Div(id="poke-description")), width=3),
                dbc.Col(dcc.Graph(id="poke-bars"), width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="base-stats-bars")),
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
                        dcc.Graph(id="radar-plot"),
                    ],
                ),
            ]
        ),
    ]
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
    fig = px.bar(bars_df.T)
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
                opacity=0.05,
            )
        ]
    )

    barplot = px.bar(
        df[["name", "base_total"]],
        x="name",
        y="base_total",
    )
    return radar, barplot


if __name__ == "__main__":
    app.run_server(debug=True)
