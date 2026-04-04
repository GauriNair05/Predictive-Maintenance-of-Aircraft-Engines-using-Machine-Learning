import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt


st.set_page_config(
    page_title="Engine Health Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
/* Entire app background */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: white !important;
    color: black !important;
}

/* Main content area */
[data-testid="stAppViewContainer"] > .main {
    background: white !important;
}

/* Remove default streamlit chrome */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Layout */
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Title */
.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 800;
    color: black;
    margin-bottom: 2rem;
}

/* Headings/text */
h1, h2, h3, h4, h5, h6, p, label, div, span {
    color: black !important;
}

/* Metric cards */
.metric-card {
    background: white;
    border: 1.5px solid black;
    border-radius: 14px;
    padding: 24px 18px;
    text-align: center;
}

.metric-card h4 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: black !important;
}

.metric-card h2 {
    margin-top: 22px;
    margin-bottom: 8px;
    font-size: 34px;
    font-weight: 800;
    color: black !important;
}

/* Search box */
.stTextInput input {
    background-color: white !important;
    color: black !important;
    border: 1.5px solid black !important;
    border-radius: 8px !important;
}

/* Small note */
.small-note {
    color: #444444 !important;
    font-size: 14px;
    margin-top: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

df = pd.read_json("engines.json")

df["rul"] = df["rul"].astype(float).round(3)
df["name"] = df["name"].astype(str)
df["status"] = df["status"].astype(str)

def extract_engine_number(name):
    try:
        return int(str(name).split()[-1])
    except Exception:
        return 0

df["engine_num"] = df["name"].apply(extract_engine_number)
df = df.sort_values("engine_num").reset_index(drop=True)


st.markdown('<div class="main-title">Engine Health Dashboard</div>', unsafe_allow_html=True)


total_engines = len(df)
critical_engines = len(df[df["status"].str.lower() == "critical"])
avg_rul = df["rul"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h4>TOTAL ENGINES</h4>
        <h2>{total_engines}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h4>CRITICAL ENGINES</h4>
        <h2>{critical_engines}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>AVERAGE RUL</h4>
        <h2>{avg_rul:.3f}</h2>
    </div>
    """, unsafe_allow_html=True)


st.write("")
search = st.text_input("Search by engine number or name")

if search:
    filtered_df = df[df["name"].str.contains(search, case=False, na=False)].copy()
else:
    filtered_df = df.copy()


st.write("")
st.subheader("Engine Status")

table_df = filtered_df[["name", "rul", "status"]].copy()
table_df.columns = ["ENGINE", "RUL", "STATUS"]

rows_html = ""
for _, row in table_df.iterrows():
    status_value = str(row["STATUS"]).strip()
    status_class = "good" if status_value.lower() == "good" else "critical"
    rows_html += f"""
    <tr>
        <td>{row["ENGINE"]}</td>
        <td>{row["RUL"]:.3f}</td>
        <td class="{status_class}">{status_value}</td>
    </tr>
    """

table_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        margin: 0;
        padding: 0;
        background: white;
        font-family: Arial, sans-serif;
        color: black;
    }}

    .table-container {{
        width: 100%;
        background: white;
        border: 1.5px solid black;
        border-radius: 10px;
        overflow: hidden;
        box-sizing: border-box;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        background: white;
        color: black;
        table-layout: fixed;
    }}

    thead th {{
        background: white;
        color: black;
        font-weight: 700;
        text-align: center;
        padding: 12px;
        border-bottom: 1.5px solid black;
        border-right: 1px solid black;
    }}

    thead th:last-child {{
        border-right: none;
    }}

    tbody td {{
        background: white;
        color: black;
        text-align: center;
        padding: 12px;
        border-top: 1px solid black;
        border-right: 1px solid black;
        font-size: 15px;
    }}

    tbody tr:first-child td {{
        border-top: none;
    }}

    tbody td:last-child {{
        border-right: none;
    }}

    .good {{
        color: green;
        font-weight: 700;
    }}

    .critical {{
        color: red;
        font-weight: 700;
    }}
</style>
</head>
<body>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>ENGINE</th>
                    <th>RUL</th>
                    <th>STATUS</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

table_height = min(max(140 + len(table_df) * 42, 220), 500)
components.html(table_html, height=table_height, scrolling=True)


st.write("")
st.subheader("RUL Trend")

chart_df = filtered_df[["name", "rul"]].copy()
chart_df.columns = ["ENGINE", "RUL"]

chart = (
    alt.Chart(chart_df)
    .mark_line(point=True, color="black")
    .encode(
        x=alt.X("ENGINE:N", title="ENGINE"),
        y=alt.Y("RUL:Q", title="RUL"),
        tooltip=[
            alt.Tooltip("ENGINE:N", title="Engine"),
            alt.Tooltip("RUL:Q", title="RUL", format=".3f")
        ]
    )
    .properties(
        height=320
    )
    .configure(background="white")
    .configure_view(
        fill="white",
        stroke="black"
    )
    .configure_axis(
        labelColor="black",
        titleColor="black",
        domainColor="black",
        tickColor="black",
        grid=False
    )
)

st.altair_chart(chart, use_container_width=True)

st.markdown(
    '<p class="small-note">Showing Remaining Useful Life across engines.</p>',
    unsafe_allow_html=True
)