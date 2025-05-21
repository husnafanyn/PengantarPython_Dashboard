# IMPORT LIBRARIES
import pandas as pd
import plotly.express as px
import streamlit as st 

# MEMBUAT KONFIGURASI PADA CANVAS DASHBOARD
st.set_page_config(
  page_title="Sales Dashboard",
  page_icon=":bar_chart:",
  layout="wide"                 
)

# MENENTUKAN TEMA WARNA DASHBOARD
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F5F5;
    }
    .stButton>button {
        background-color: #0083B8;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #005f8c;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# IMPORT DATA SALES
data = pd.read_csv(r"https://github.com/husnafanyn/PengantarPython_Dashboard/blob/main/Sales_Superstore.csv")
#st.dataframe(data)

# MEMBUAT HEADER PADA DASHBOARD
st.title(":bar_chart: Sales Dashboard")
# Membuat button klik yang menampilkan credit
klik = st.button("Click Here for Credit")
if klik:
    st.write("Created by husnafanyn")
    st.write("Data Source: Superstore Dataset")
st.markdown("##")

# MEMBUAT SIDEBAR
st.sidebar.header("Please Filter Here:")

category_sb = st.sidebar.multiselect(
  "Select the Category:",
  options = data["category"].unique(),
  default = data["category"].unique()
)

segment_sb = st.sidebar.multiselect(
  "Select the Segment:",
  options = data["segment"].unique(),
  default = data["segment"].unique()
)

data["order_date"] = pd.to_datetime(data["order_date"])
data["order_year"] = data["order_date"].dt.year
year_sb = st.sidebar.multiselect(
    "Select the Year:",
    options = sorted(data["order_year"].unique()),
    default = sorted(data["order_year"].unique())
)

data_selection = data[
    (data['category'].isin(category_sb)) & 
    (data['segment'].isin(segment_sb)) &
    (data['order_year'].isin(year_sb))
]

# MEMBUAT KEY PERFORMANCE INDICATORS (KPI)
total_sales = int(data_selection["sales"].sum())
average_quantity = round(data_selection["quantity"].mean(),1)
box_icon ="📦" * int(round(average_quantity,0))
average_sales = round(data_selection["sales"].mean(),2)

# MEMBUAT KARTU KPI
left_column,middle_column,right_column=st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US$ {total_sales:,}")
with middle_column:
    st.subheader("Average Quantity Sold:")
    st.subheader(f"{box_icon} {average_quantity}")
with right_column:
    st.subheader("Average Sales:")
    st.subheader(f"US$ {average_sales:,}")

st.markdown("---")

# MENAMPILKAN DATA
st.dataframe(data_selection)

# MENAMPILKAN GRAFIK SALES PER SUB-CATEGORY
sales_per_subcategory = data_selection.groupby("sub_category").sum(numeric_only=True)[["sales"]].sort_values(by="sales", ascending=False).reset_index()
fig = px.bar(
    sales_per_subcategory,
    x="sub_category",
    y="sales",
    title="<b>Sales per Sub-Category</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_per_subcategory),
    template="plotly_white"
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="<b>Sub-Category</b>",
    yaxis_title="<b>Sales</b>",
    legend_title="<b>Legend</b>"
)
st.plotly_chart(fig, use_container_width=True)

# MENAMPILKAN GRAFIK LINE SALES PER MONTH
data_selection["order_date"] = pd.to_datetime(data_selection["order_date"])
data_selection["order_date"] = data_selection["order_date"].dt.to_period("M").dt.to_timestamp()
sales_per_month = data_selection.groupby("order_date").sum(numeric_only=True)[["sales"]].reset_index()
fig = px.line(
    sales_per_month,
    x="order_date",
    y="sales",
    title="<b>Sales per Month</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_per_month),
    template="plotly_white"
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="<b>Order Date</b>",
    yaxis_title="<b>Sales</b>",
    legend_title="<b>Legend</b>"
)
st.plotly_chart(fig, use_container_width=True)

# MENAMPILKAN GRAFIK SCATTER PROFIT RATIO (SALES/PROFIT) VS SALES BY SUB-CATEGORY
# Agregasi sales dan profit per sub_category
sales_profit_per_subcategory = data_selection.groupby("sub_category").sum(numeric_only=True)[["sales", "profit"]].reset_index()

# Filter profit ≠ 0 dan bukan NaN agar tidak error saat membagi
sales_profit_per_subcategory = sales_profit_per_subcategory[
    (sales_profit_per_subcategory["profit"] != 0) & (~sales_profit_per_subcategory["profit"].isna())
]

if not sales_profit_per_subcategory.empty:
    # Hitung profit_ratio setelah agregasi
    sales_profit_per_subcategory.loc[:, "profit_ratio"] = sales_profit_per_subcategory["sales"] / sales_profit_per_subcategory["profit"]

    # Pastikan size tidak ada yang NaN, nol, atau negatif
    sales_profit_per_subcategory = sales_profit_per_subcategory[sales_profit_per_subcategory["profit_ratio"] > 0]

    if not sales_profit_per_subcategory.empty:
        # Plot scatter
        fig = px.scatter(
            sales_profit_per_subcategory,
            x="sales",
            y="profit_ratio",
            size="profit_ratio",
            color="sub_category",
            title="<b>Sales vs Profit Ratio by Sub-Category</b>",
            color_discrete_sequence=["#0083B8"] * len(sales_profit_per_subcategory),
            template="plotly_white"
        )
        fig.update_layout(
            autosize=False,
            width=600,
            height=600,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="<b>Sales</b>",
            yaxis_title="<b>Profit Ratio</b>",
            legend_title="<b>Legend</b>"
        )

        # Hitung rata-rata profit_ratio yang benar
        avg_sales = sales_profit_per_subcategory["sales"].mean()
        avg_profit_ratio = sales_profit_per_subcategory["profit_ratio"].mean()

        fig.add_vline(x=avg_sales, line_dash="dash", line_color="red", annotation_text="Avg Sales", annotation_position="top right")
        fig.add_hline(y=avg_profit_ratio, line_dash="dash", line_color="green", annotation_text="Avg Profit Ratio", annotation_position="bottom left")

        st.plotly_chart(fig)
    else:
        st.info("Tidak ada data sub-category dengan profit_ratio > 0 untuk ditampilkan pada scatter plot.")
else:
    st.info("Tidak ada data sub-category dengan profit ≠ 0 untuk ditampilkan pada scatter plot.")
