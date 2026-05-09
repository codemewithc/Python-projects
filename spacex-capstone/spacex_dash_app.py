import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ── Load Data ─────────────────────────────────────────────────────────────────
SPACEX_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
)
spacex_df = pd.read_csv(SPACEX_URL)
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# ── App Layout ────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        "SpaceX Launch Records Dashboard",
        style={"textAlign": "center", "color": "#1565C0", "fontFamily": "Arial"},
    ),

    # ── TASK 1: Launch Site Dropdown ─────────────────────────────────────────
    dcc.Dropdown(
        id="site-dropdown",
        options=[{"label": "All Sites", "value": "ALL"}] + [
            {"label": site, "value": site}
            for site in sorted(spacex_df["Launch Site"].unique())
        ],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True,
        style={"width": "60%", "margin": "20px auto"},
    ),

    html.Br(),

    # ── TASK 2: Success Pie Chart ─────────────────────────────────────────────
    html.Div(
        dcc.Graph(id="success-pie-chart"),
        style={"width": "60%", "margin": "0 auto"},
    ),

    html.Br(),

    html.P("Payload range (Kg):", style={"textAlign": "center", "fontFamily": "Arial"}),

    # ── TASK 3: Payload Range Slider ─────────────────────────────────────────
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        marks={i: f"{i:,}" for i in range(0, 11000, 2000)},
        value=[min_payload, max_payload],
    ),

    html.Br(),

    # ── TASK 4: Scatter Chart ─────────────────────────────────────────────────
    html.Div(
        dcc.Graph(id="success-payload-scatter-chart"),
        style={"width": "95%", "margin": "0 auto"},
    ),
])

# ── TASK 2 CALLBACK: Pie chart ─────────────────────────────────────────────────
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Site",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
    else:
        filtered = spacex_df[spacex_df["Launch Site"] == entered_site]
        outcome_counts = filtered["class"].value_counts().reset_index()
        outcome_counts.columns = ["Outcome", "Count"]
        outcome_counts["Outcome"] = outcome_counts["Outcome"].map({1: "Success", 0: "Failure"})
        fig = px.pie(
            outcome_counts,
            values="Count",
            names="Outcome",
            title=f"Total Success Launches for site {entered_site}",
            color="Outcome",
            color_discrete_map={"Success": "#2E7D32", "Failure": "#C62828"},
        )
    fig.update_layout(
        paper_bgcolor="#FAFAFA",
        plot_bgcolor="#FAFAFA",
        font={"family": "Arial"},
    )
    return fig


# ── TASK 4 CALLBACK: Scatter chart ─────────────────────────────────────────────
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df["Payload Mass (kg)"] >= low) & (spacex_df["Payload Mass (kg)"] <= high)
    filtered = spacex_df[mask] if entered_site == "ALL" else spacex_df[mask & (spacex_df["Launch Site"] == entered_site)]

    title = (
        f"Correlation between Payload and Success for {entered_site}"
        if entered_site != "ALL"
        else "Correlation between Payload and Success for all Sites"
    )

    fig = px.scatter(
        filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title,
        labels={"class": "Launch Outcome (1=Success, 0=Failure)"},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        symbol="Booster Version Category",
    )
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Failure", "Success"])
    fig.update_layout(
        paper_bgcolor="#FAFAFA",
        plot_bgcolor="#FAFAFA",
        font={"family": "Arial"},
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
