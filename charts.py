"""Two Plotly charts, built from the same tables displayed by the app."""
import pandas as pd
import plotly.graph_objects as go
import branding as brand


def style(fig, height):
    fig.update_layout(
        template="plotly_white", height=height,
        font=dict(family="Arial", size=13, color=brand.TEXT),
        margin=dict(l=12, r=24, t=35, b=55),
        legend=dict(orientation="h", y=1.15, x=0),
        paper_bgcolor="white", plot_bgcolor="white",
        hoverlabel=dict(bgcolor="white"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E5ECEE", zerolinecolor="#C8D7DB")
    return fig


def trend_chart(measure, rows):
    fig = go.Figure()
    label = "Actual · original APR" if measure.id == "internal" else "Actual"
    fig.add_trace(go.Scatter(x=rows.period, y=rows.actual, name=label,
        mode="lines+markers", line=dict(color=brand.NAVY, width=3),
        marker=dict(size=9), hovertemplate="%{x}: %{y:.2f}<extra>%{fullData.name}</extra>"))
    if rows.target.notna().any():
        fig.add_trace(go.Scatter(x=rows.period, y=rows.target, name="Full target",
            mode="lines+markers", line=dict(color=brand.PURPLE, width=2, dash="dash"),
            hovertemplate="%{x}: %{y:.2f}<extra>Full target</extra>"))
    if pd.notna(measure.deadband):
        fig.add_trace(go.Scatter(x=rows.period, y=[measure.deadband] * len(rows),
            name="Payment deadband", mode="lines", line=dict(color="#657B84", dash="dot")))
    if measure.id == "internal":
        fig.add_trace(go.Scatter(x=[rows.period.iloc[-1]], y=[measure.actual],
            name="Ofwat October 2025", mode="markers",
            marker=dict(color=brand.RED, size=13, symbol="diamond")))
    if measure.id == "cmex":
        fig.add_trace(go.Scatter(x=[rows.period.iloc[-1]], y=[measure.benchmark],
            name="2024/25 sector median", mode="markers",
            marker=dict(color=brand.PURPLE, size=12, symbol="diamond")))
    fig.update_xaxes(type="category", title=None)
    fig.update_yaxes(title=measure.history_unit)
    return style(fig, 390)


def peer_chart(measure, rows):
    fig = go.Figure(go.Bar(x=rows.actual, y=rows.company, orientation="h",
        marker_color=[brand.NAVY if c == "Severn Trent Water" else brand.GREY for c in rows.company],
        text=[f"{v:.2f}" for v in rows.actual], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:.2f}<extra></extra>"))
    fig.add_vline(x=measure.benchmark, line_color=brand.PURPLE, line_dash="dash")
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(title=measure.unit, rangemode="tozero")
    return style(fig, max(420, len(rows) * 27 + 85))

