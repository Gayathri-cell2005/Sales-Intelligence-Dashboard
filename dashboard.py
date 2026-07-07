"""
dashboard.py
-------------
Real-Time Sales Intelligence Dashboard.

Run with:  streamlit run dashboard.py

This connects to the MySQL 'sales' table and displays KPIs and charts.
It auto-refreshes every few seconds so that if generate_live_sales.py
is running in another terminal, you'll see the numbers update live.

NOTE ON AUTO-REFRESH:
We use @st.fragment(run_every=...) so only part of the page reruns on
a timer instead of reloading the whole app (which caused asset-fetch
errors in earlier testing).

NOTE ON SIDEBAR FILTERS:
Streamlit does not allow a fragment to place widgets into the sidebar,
since the sidebar lives outside the fragment's own container. So the
filter widgets (date range, region, category) are built in the static
part of the page (outside the fragment), and only the data display
(KPIs, charts, tables) lives inside the auto-refreshing fragment.
"""

import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from datetime import datetime
from config import DB_CONFIG

# ---------- Page setup ----------
st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
)

REFRESH_INTERVAL_SECONDS = 5


# ---------- Data access layer ----------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
def load_all_sales():
    """Run a SQL query and return the result as a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM sales ORDER BY sale_date", conn)
    conn.close()
    return df


# ---------- Static page shell (loads once) ----------
st.title("📊 Real-Time Sales Intelligence Dashboard")
st.caption("Live sales analytics powered by Python, MySQL, and Streamlit")

st.sidebar.title("Filters")

# Load data once here (outside the fragment) so we can build the filter
# widgets with real min/max dates and option lists. The fragment below
# will reload fresh data on its own timer, but these filter widgets and
# their current values stay put in the sidebar in between refreshes.
_raw_df_for_filters = load_all_sales()

if _raw_df_for_filters.empty:
    st.warning("No data found in the 'sales' table yet. Run load_data.py first.")
    st.stop()

_raw_df_for_filters["sale_date"] = pd.to_datetime(_raw_df_for_filters["sale_date"])

min_date = _raw_df_for_filters["sale_date"].min().date()
max_date = _raw_df_for_filters["sale_date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

region_options = ["All"] + sorted(_raw_df_for_filters["region"].unique().tolist())
selected_region = st.sidebar.selectbox("Region", region_options)

category_options = ["All"] + sorted(_raw_df_for_filters["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Category", category_options)

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Auto-refreshes every {REFRESH_INTERVAL_SECONDS}s. "
    f"Run generate_live_sales.py in another terminal to see live updates."
)


# ---------- Everything below refreshes automatically ----------
@st.fragment(run_every=REFRESH_INTERVAL_SECONDS)
def render_dashboard(date_range, selected_region, selected_category):
    raw_df = load_all_sales()

    if raw_df.empty:
        st.warning("No data found in the 'sales' table yet. Run load_data.py first.")
        return

    raw_df["sale_date"] = pd.to_datetime(raw_df["sale_date"])

    st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")

    # ---------- Apply filters ----------
    df = raw_df.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[
            (df["sale_date"].dt.date >= start_date) & (df["sale_date"].dt.date <= end_date)
        ]

    if selected_region != "All":
        df = df[df["region"] == selected_region]

    if selected_category != "All":
        df = df[df["category"] == selected_category]

    if df.empty:
        st.info("No sales match the selected filters.")
        return

    # ---------- KPI row ----------
    total_revenue = df["total_amount"].sum()
    total_orders = len(df)
    avg_order_value = df["total_amount"].mean() if total_orders > 0 else 0
    total_units = df["quantity"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Avg Order Value", f"₹{avg_order_value:,.0f}")
    col4.metric("Units Sold", f"{total_units:,}")

    st.markdown("---")

    # ---------- Charts row 1 ----------
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Revenue Over Time")
        daily_revenue = (
            df.assign(date=df["sale_date"].dt.date)
            .groupby("date")["total_amount"]
            .sum()
            .reset_index()
        )
        fig_trend = px.line(
            daily_revenue, x="date", y="total_amount",
            labels={"total_amount": "Revenue (₹)", "date": "Date"},
        )
        st.plotly_chart(fig_trend, use_container_width=True, key="trend_chart")

    with chart_col2:
        st.subheader("Revenue by Category")
        category_revenue = (
            df.groupby("category")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)
        )
        fig_cat = px.bar(
            category_revenue, x="category", y="total_amount",
            labels={"total_amount": "Revenue (₹)", "category": "Category"},
            color="category",
        )
        st.plotly_chart(fig_cat, use_container_width=True, key="category_chart")

    # ---------- Charts row 2 ----------
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.subheader("Sales by Region")
        region_revenue = df.groupby("region")["total_amount"].sum().reset_index()
        fig_region = px.pie(
            region_revenue, names="region", values="total_amount", hole=0.4,
        )
        st.plotly_chart(fig_region, use_container_width=True, key="region_chart")

    with chart_col4:
        st.subheader("Top 5 Products by Revenue")
        top_products = (
            df.groupby("product")["total_amount"].sum().reset_index()
            .sort_values("total_amount", ascending=False).head(5)
        )
        fig_top = px.bar(
            top_products, x="total_amount", y="product", orientation="h",
            labels={"total_amount": "Revenue (₹)", "product": "Product"},
        )
        fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top, use_container_width=True, key="top_products_chart")

    # ---------- Sales Rep Leaderboard ----------
    st.subheader("Sales Rep Leaderboard")
    rep_performance = (
        df.groupby("sales_rep")
        .agg(total_revenue=("total_amount", "sum"), total_orders=("sale_id", "count"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    st.dataframe(rep_performance, use_container_width=True, hide_index=True)

    # ---------- Recent transactions ----------
    st.subheader("Most Recent Transactions")
    recent = df.sort_values("sale_date", ascending=False).head(10)
    st.dataframe(
        recent[["sale_date", "product", "category", "region", "quantity", "total_amount", "sales_rep"]],
        use_container_width=True,
        hide_index=True,
    )


render_dashboard(date_range, selected_region, selected_category)