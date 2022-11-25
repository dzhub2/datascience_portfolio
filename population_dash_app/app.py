from dash import Dash, dcc, html, Input, Output
import pandas as pd
pd.set_option("display.float_format", "{:.2}".format)
import seaborn as sns
sns.set_theme()
import plotly.express as px
import os 

app = Dash()

# load data
try:
    fert = pd.read_csv("/home/dzhub2/mysite/data/gapminder_total_fertility.csv", index_col=0)
    life = pd.read_excel("/home/dzhub2/mysite/data/gapminder_lifeexpectancy.xlsx", index_col=0)
    population = pd.read_excel("/home/dzhub2/mysite/data/gapminder_population.xlsx", index_col=0)
    continents = pd.read_csv("/home/dzhub2/mysite/data/continents.csv", index_col=1)
except OSError:
    print("Input file not found.")

## data preprocessing
del life[life.columns[-1]]  # delete last column to match dimensions
continents = continents[["four_regions"]]  # extract continents
continents = continents.reset_index()
continents = continents.rename(columns={"name": "country", "four_regions": "continent"})

# match column data type
fert.columns = fert.columns.astype(int)
life.columns = life.columns.astype(int)
population.columns = population.columns.astype(int)

# prepare all rows and columns for merger
fert.index.name = "country"
life.index.name = "country"
population.index.name = "country"

fert = fert.reset_index()
fert = fert.melt(id_vars="country", var_name="year", value_name="fertility_rate")
life = life.reset_index()
life = life.melt(id_vars="country", var_name="year", value_name="lifeexpectancy_rate")
population = population.reset_index()
population = population.melt(
    id_vars="country", var_name="year", value_name="population"
)

# merge it all
df = fert.merge(life)
df = df.merge(population)
df = df.merge(continents)
df.head(5)

# show the most populated countries for a given year
year = 2015
pop_overview = population[population["year"] == year]
pop_overview = pop_overview.sort_values(by="population", ascending=False)
pop_overview.head(8)


# overview of population by year by histogram
def do_single_histogram(df, year):
    sns.histplot(data=df, x="population", stat="count", bins=20, log_scale=True)


do_single_histogram(df, 2000)


# clean data and choose specific years only
df = df[df["year"] >= 1960].reset_index()
df = df.dropna()
df = df.rename(columns={"year": "Year"})


# draw animated scatter plot with plotly
fig = px.scatter(
    df,
    x="lifeexpectancy_rate",
    y="fertility_rate",
    animation_frame="Year",
    animation_group="country",
    hover_name="country",
    # range_color=[5,8] symbol="population_level"
    color="population",
    color_continuous_scale="Rainbow",
    size="population",
    size_max=60,
    opacity=0.6,
    range_color=(0, 3e8),
    labels={
        "lifeexpectancy_rate": "Life expectancy in years",
        "fertility_rate": "Births per woman",
        "population": "Population",
    },
    category_orders={"population_level": ["< 10", "< 100", "< 350", "> 350"]},
    title="Births per Woman vs. Life Expectancy by Country Size",
    width=1000,
    height=700,
)

# figure styling
fig.update_layout(
    font_family="Garamond",
    font_size=20,
    paper_bgcolor="white",
    plot_bgcolor="white",
    legend=dict(
        yanchor="top",
        xanchor="right",
        font_size=14,
        title="Population in Mio.",
        traceorder="reversed",
        bgcolor="white",
        bordercolor="lightGrey",
        borderwidth=1,
        title_text="Trend",
    ),
    title={"x": 0.5, "y": 0.92, "xanchor": "center", "yanchor": "top"},
    coloraxis={
        "cauto": False,
        "colorbar_len": 1.1,
        "colorbar_outlinewidth": 1.75,
        "colorbar_ticks": "inside",
        "colorbar_tickwidth": 2,
        "colorbar_yanchor": "middle",
        "colorbar_y": 0.55,
    },
)
fig.update_xaxes(
    range=[20, 90],
    gridwidth=0.1,
    linecolor="black",
    linewidth=1.5,
    ticks="outside",
    tickwidth=1.5,
    ticklen=10,
    griddash="dashdot",
    gridcolor="#ededed",
)
fig.update_yaxes(
    range=[0, 10],
    gridwidth=0.1,
    linecolor="black",
    linewidth=1.5,
    ticks="outside",
    tickwidth=1.5,
    ticklen=10,
    griddash="dashdot",
    gridcolor="#ededed",
)
fig.update_yaxes(range=[-1, 10])
fig.update_traces(mode="markers", marker=dict(sizemode="area", line_width=1.5))

# set FPS of animation
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 200  # in ms
fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 200
# fig["layout"].pop("updatemenus") # optional, drop animation buttons

colorscales = px.colors.named_colorscales()
colorscales_capitalized = [str.capitalize() for str in colorscales]
fontfamily = "Garamond"  # pick your own font-family

app.layout = html.Div(
    [
        html.P(
            "Select your color palette:",
            style={"font-family": fontfamily, "text-decoration": "underline"},
        ),
        dcc.Dropdown(
            id="dropdown",
            options=colorscales_capitalized,
            placeholder="Select color palette",
            value="Rainbow",
        ),
        dcc.Graph(figure=fig, id="graph"),
    ],
    style={"width": "25%", 'font-family': fontfamily, 'font-size': 19}
)


@app.callback(Output("graph", "figure"), Input("dropdown", "value"))
# create drop-down for changable colorscale
def change_colorscale(scale):
    fig.update_layout(coloraxis={"colorscale": scale})
    return fig


if __name__ == "__main__":
    app.run_server(debug=False, port=8051)
