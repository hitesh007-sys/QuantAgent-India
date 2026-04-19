import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_csv("accuracy_results.csv")

# ── Chart 1: Average accuracy bar chart ──
models    = ["Random (%)", "LR (%)", "XGBoost (%)", "QuantAgent(%)"]
labels    = ["Random", "Linear Regression", "XGBoost", "QuantAgent"]
colors    = ["#636e72", "#74b9ff", "#fdcb6e", "#a29bfe"]
averages  = [df[m].mean() for m in models]

fig1 = go.Figure()
for i, (label, avg, color) in enumerate(
    zip(labels, averages, colors)
):
    fig1.add_trace(go.Bar(
        x=[label],
        y=[round(avg, 2)],
        name=label,
        marker_color=color,
        text=[f"{round(avg, 2)}%"],
        textposition="outside",
        textfont=dict(size=14, color="white")
    ))

fig1.update_layout(
    title=dict(
        text="Average Accuracy — All 4 Models (25 Indian Stocks)",
        font=dict(size=18, color="white")
    ),
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    yaxis=dict(
        range=[40, 65],
        title="Accuracy (%)",
        gridcolor="#2a2a3d",
        color="white"
    ),
    xaxis=dict(color="white"),
    showlegend=False,
    height=450
)
fig1.write_html("chart_average_accuracy.html")
print("Saved: chart_average_accuracy.html")

# ── Chart 2: Daily vs Weekly comparison ──
daily  = df[df['Timeframe'] == 'Daily']
weekly = df[df['Timeframe'] == 'Weekly']

daily_avgs  = [daily[m].mean()  for m in models]
weekly_avgs = [weekly[m].mean() for m in models]

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    name="Daily",
    x=labels,
    y=[round(v, 2) for v in daily_avgs],
    marker_color="#a29bfe",
    text=[f"{round(v,2)}%" for v in daily_avgs],
    textposition="outside",
    textfont=dict(color="white")
))
fig2.add_trace(go.Bar(
    name="Weekly",
    x=labels,
    y=[round(v, 2) for v in weekly_avgs],
    marker_color="#fd79a8",
    text=[f"{round(v,2)}%" for v in weekly_avgs],
    textposition="outside",
    textfont=dict(color="white")
))

fig2.update_layout(
    title=dict(
        text="Daily vs Weekly Accuracy — All 4 Models",
        font=dict(size=18, color="white")
    ),
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    barmode="group",
    yaxis=dict(
        range=[40, 68],
        title="Accuracy (%)",
        gridcolor="#2a2a3d"
    ),
    height=450
)
fig2.write_html("chart_daily_vs_weekly.html")
print("Saved: chart_daily_vs_weekly.html")

# ── Chart 3: Win count pie chart ──
win_counts = df['Best Model'].value_counts()

fig3 = go.Figure(go.Pie(
    labels=win_counts.index,
    values=win_counts.values,
    hole=0.4,
    marker=dict(colors=["#a29bfe", "#fdcb6e", "#74b9ff", "#636e72"]),
    textfont=dict(size=14, color="white"),
    textinfo="label+percent"
))
fig3.update_layout(
    title=dict(
        text="Best Model Win Distribution (36 total cases)",
        font=dict(size=18, color="white")
    ),
    paper_bgcolor="#0f0f1a",
    font=dict(color="white"),
    height=400
)
fig3.write_html("chart_win_distribution.html")
print("Saved: chart_win_distribution.html")

# ── Chart 4: QuantAgent per company ──
qa_daily = daily[["Company", "QuantAgent(%)"]].sort_values(
    "QuantAgent(%)", ascending=True
)

fig4 = go.Figure(go.Bar(
    x=qa_daily["QuantAgent(%)"],
    y=qa_daily["Company"],
    orientation='h',
    marker=dict(
        color=qa_daily["QuantAgent(%)"],
        colorscale="Purples",
        showscale=False
    ),
    text=[f"{v}%" for v in qa_daily["QuantAgent(%)"]],
    textposition="outside",
    textfont=dict(color="white")
))
fig4.add_vline(
    x=50, line_dash="dash",
    line_color="#636e72",
    annotation_text="50% baseline",
    annotation_font_color="#636e72"
)
fig4.update_layout(
    title=dict(
        text="QuantAgent Daily Accuracy — Per Company",
        font=dict(size=18, color="white")
    ),
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    xaxis=dict(
        range=[30, 80],
        title="Accuracy (%)",
        gridcolor="#2a2a3d"
    ),
    height=600
)
fig4.write_html("chart_quantagent_per_company.html")
print("Saved: chart_quantagent_per_company.html")

print("\nAll 4 charts generated successfully!")
print("Open the .html files in your browser to view them.")