import streamlit as st
import pandas as pd
import psycopg2
from streamlit_autorefresh import st_autorefresh

# Auto-refresh mỗi 5 giây
st_autorefresh(interval=5000, key="refresh")

st.title("📊 Bank Transaction Anomaly Dashboard")

# Hàm load dữ liệu từ bảng transactions
def load_all_transactions():
    conn = psycopg2.connect(
        host="postgres",
        database="bankdb",
        user="user",
        password="password"
    )
    # Lấy dữ liệu từ bảng transactions (tất cả giao dịch)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 100", conn)
    conn.close()
    return df

# Hàm load dữ liệu từ bảng transactions_anomaly
def load_anomalies():
    conn = psycopg2.connect(
        host="postgres",
        database="bankdb",
        user="user",
        password="password"
    )
    # Lấy dữ liệu từ bảng transactions_anomaly (anomaly = -1)
    df = pd.read_sql_query("SELECT * FROM transactions_anomaly ORDER BY timestamp DESC LIMIT 100", conn)
    conn.close()
    return df

# Lấy tất cả dữ liệu giao dịch từ bảng transactions
data_all = load_all_transactions()

# Lấy dữ liệu giao dịch có anomaly = -1 từ bảng transactions_anomaly
anomalies = load_anomalies()

# Hiển thị các giao dịch gần đây từ bảng transactions
st.write(f"### Showing {len(data_all)} Latest Transactions")
st.dataframe(data_all)

# Hiển thị các giao dịch bất thường (anomaly = -1) từ bảng transactions_anomaly
st.write(f"### 🚨 {len(anomalies)} Anomalies Detected")
st.dataframe(anomalies)

st.write("---")
st.header("📝 Thêm Giao Dịch Thủ Công Để Test")

# Form nhập giao dịch mới
with st.form("add_transaction_form"):
    account_id = st.number_input("Account ID", min_value=1, step=1)
    transaction_id = st.number_input("Transaction ID", min_value=1000, step=1)
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    location = st.selectbox("Location", ["HN", "HCM", "DN"])
    timestamp = st.number_input("Timestamp (Epoch)", value=int(pd.Timestamp.now().timestamp()), step=1)
    hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=12)
    anomaly = st.selectbox("Anomaly Flag", [-1, 1], format_func=lambda x: "Anomaly (-1)" if x == -1 else "Normal (1)")

    submitted = st.form_submit_button("Thêm Giao Dịch")

    if submitted:
        try:
            conn = psycopg2.connect(
                host="postgres",
                database="bankdb",
                user="user",
                password="password"
            )
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO transactions (account_id, transaction_id, amount, location, timestamp, hour, anomaly)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (account_id, transaction_id, amount, location, timestamp, hour, anomaly))
            conn.commit()
            cur.close()
            conn.close()
            st.success("Đã thêm giao dịch thành công!")
        except Exception as e:
            st.error(f"Thêm giao dịch thất bại: {e}")
