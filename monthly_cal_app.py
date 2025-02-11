import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ページ全体を広げるスタイル
st.set_page_config(layout="wide")

# 住宅ローン計算関数
def calculate_mortgage(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100
    months = years * 12
    if monthly_rate > 0:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    else:
        monthly_payment = principal / months
    return round(monthly_payment / 10000, 2)  # 万円単位に変換

# 小数点の表示設定（整数なら .0 を省略）
def format_number(value):
    return f"{value:.2f}".rstrip("0").rstrip(".") if "." in f"{value:.2f}" else f"{value:.0f}"

# 初期値設定
initial_income = {"給与": 30.00, "副業": 0.00}
initial_expenses = {
    "固定費": {"住宅費": 12.98, "水道光熱費": 2.00, "通信費": 1.00, "保険料": 2.00, "教育費": 0.00, "サブスクリプション費用": 0.30},
    "変動費": {"食費": 5.00, "交通費": 0.00, "日用品費": 2.00, "医療費": 0.40, "交際費": 0.20, "娯楽費": 1.00, "衣服費": 0.40},
    "貯蓄・投資": {"貯金": 0.00, "投資": 7.00, "年金・保険の積立": 0.00},
    "特別支出": {"家電・家具購入": 0.00, "車関連費": 3.00, "イベント関連費": 0.00, "修繕費": 0.00, "入学費": 0.00},
}

# 住宅ローンのデフォルト値
default_mortgage = {"借入金額": 5000, "年利": 0.50, "返済期間": 35}

# セッションステートの初期化
if "income" not in st.session_state:
    st.session_state.income = initial_income.copy()

if "expenses" not in st.session_state:
    st.session_state.expenses = initial_expenses.copy()

if "mortgage" not in st.session_state:
    st.session_state.mortgage = default_mortgage.copy()

# レイアウト設定
col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])

with col1:
    st.markdown("#### 収入の入力（万円）")
    for category in initial_income:
        st.session_state.income[category] = st.number_input(
            f"{category}", value=st.session_state.income[category], step=0.1
        )

    # 配当収入の計算
    st.markdown("#### 株による配当収入（万円）")
    dividend_option = st.radio("配当収入の入力方法", ("手入力", "投資額から計算"), horizontal=True)

    if dividend_option == "手入力":
        st.session_state.income["株による配当"] = st.number_input(
            "株による配当収入", value=0.02, step=0.01
        )
    else:
        investment_amount = st.number_input("投資額（万円）", value=7.00, step=1.0)
        dividend_yield = st.number_input("配当利回り（%）", value=3.0, step=0.1)
        calculated_dividend = (investment_amount * dividend_yield / 100) / 12
        st.session_state.income["株による配当"] = round(calculated_dividend, 2)
        st.write(f"**計算された月間配当:** {calculated_dividend:,.2f} 万円")

    # 住宅ローンの計算機能
    st.markdown("#### 住宅費の入力（万円）")
    housing_option = st.radio("住宅費の計算方法", ("家賃を手入力", "住宅ローンを計算"), horizontal=True)

    if housing_option == "家賃を手入力":
        st.session_state.expenses["固定費"]["住宅費"] = st.number_input(
            "家賃・管理費・修繕費など",
            value=st.session_state.expenses["固定費"]["住宅費"],
            step=0.1
        )
    else:
        st.session_state.mortgage["借入金額"] = st.number_input("借入金額（万円）", value=default_mortgage["借入金額"], step=100)
        st.session_state.mortgage["年利"] = st.number_input("年利（%）", value=default_mortgage["年利"], step=0.1)
        st.session_state.mortgage["返済期間"] = st.number_input("返済期間（年）", value=default_mortgage["返済期間"], step=1)

        monthly_mortgage = calculate_mortgage(
            st.session_state.mortgage["借入金額"] * 10000,
            st.session_state.mortgage["年利"],
            st.session_state.mortgage["返済期間"]
        )
        st.session_state.expenses["固定費"]["住宅費"] = monthly_mortgage
        st.write(f"**計算された毎月の住宅ローン返済額:** {monthly_mortgage:,.2f} 万円")

# 各支出カテゴリの入力
cols = [col2, col3, col4, col5]
for i, (category, items) in enumerate(initial_expenses.items()):
    with cols[i]:
        st.markdown(f"#### {category}")
        for item in items:
            st.session_state.expenses[category][item] = st.number_input(
                f"{item}", value=st.session_state.expenses[category][item], step=0.1
            )

# 収支計算
total_income = sum(st.session_state.income.values())
total_expense = sum(sum(items.values()) for items in st.session_state.expenses.values())

# **円グラフのデータを小項目ベースで作成**
expense_details = {}
for category, items in st.session_state.expenses.items():
    for item, amount in items.items():
        if amount > 0:  # 0円の項目は表示しない
            expense_details[item] = amount

# グラフ表示
st.markdown("### 収支グラフ")
col6, col7 = st.columns([1, 1])

with col6:
    fig, ax = plt.subplots()
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Yu Gothic", "Hiragino Sans", "sans-serif"]
    # plt.rcParams["font.family"] = "Meiryo"  # もしくは "MS Gothic" (Windows), "Meiryo"
    bars = ax.bar(["Income", "Expenses"], [total_income, total_expense], color=['blue', 'red'])
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{format_number(height)}", ha='center', va='bottom')

    ax.set_ylabel("Amount (Million Yen)")
    ax.set_title("Income vs Expenses")
    st.pyplot(fig)

with col7:
    if expense_details:
        plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Yu Gothic", "Hiragino Sans", "sans-serif"]
        # plt.rcParams["font.family"] = "Meiryo"  # もしくは "MS Gothic" (Windows), "Meiryo"
        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(
            expense_details.values(),
            labels=expense_details.keys(),
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )
        ax.axis("equal")  # 円形にする
        st.pyplot(fig)

# CSVダウンロード
st.markdown("#### データをCSVとして保存")
df_data = [{"項目": category, "金額": amount} for category, amount in st.session_state.income.items()]
df_data += [{"項目": item, "金額": amount} for category, items in st.session_state.expenses.items() for item, amount in items.items()]
df = pd.DataFrame(df_data)
csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(label="CSVダウンロード", data=csv, file_name="kakeibo_data.csv", mime="text/csv")