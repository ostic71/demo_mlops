from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType
from sklearn.ensemble import IsolationForest
import numpy as np
import psycopg2
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from datetime import datetime

def save_to_postgres(df):
    conn = psycopg2.connect(
        host="postgres",
        database="bankdb",
        user="user",
        password="password"
    )
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        account_id INTEGER,
        transaction_id INTEGER,
        amount DOUBLE PRECISION,
        location TEXT,
        timestamp BIGINT,
        hour INTEGER,
        anomaly INTEGER
        )
    """)

    # Chèn dữ liệu
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO transactions (account_id, transaction_id, amount, location, timestamp, hour, anomaly)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (row['account_id'], row['transaction_id'], row['amount'], row['location'], row['timestamp'], row['hour'], row['anomaly']))

    conn.commit()
    cur.close()
    conn.close()


def save_to_postgres_anomalies(df):
    conn = psycopg2.connect(
        host="postgres",
        database="bankdb",
        user="user",
        password="password"
    )
    cur = conn.cursor()
    
    # Tạo bảng transactions_anomaly nếu chưa có
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions_anomaly (
        account_id INTEGER,
        transaction_id INTEGER,
        amount DOUBLE PRECISION,
        location TEXT,
        timestamp BIGINT,
        hour INTEGER,
        anomaly INTEGER
    )
    """)
    
    # Chèn dữ liệu vào bảng transactions_anomaly
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO transactions_anomaly (account_id, transaction_id, amount, location, timestamp, hour, anomaly)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (row['account_id'], row['transaction_id'], row['amount'], row['location'], row['timestamp'], row['hour'], row['anomaly']))
    
    conn.commit()
    cur.close()
    conn.close()


schema = StructType([
    StructField("account_id", IntegerType()),
    StructField("transaction_id", IntegerType()),
    StructField("amount", DoubleType()),
    StructField("location", StringType()),
    StructField("timestamp", LongType())
])


spark = SparkSession.builder \
    .appName("SocketBankFraudDetection") \
    .config("spark.ui.port", "4040")  \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.readStream \
    .format("socket") \
    .option("host", "data-generator") \
    .option("port", 9999) \
    .load()

df_parsed = df.select(from_json(col("value"), schema).alias("data")).select("data.*")


def process_batch(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    pdf = batch_df.toPandas()
    pdf['hour'] = pdf['timestamp'].apply(lambda ts: datetime.fromtimestamp(ts).hour)

    le = LabelEncoder()
    pdf['location_encoded'] = le.fit_transform(pdf['location'])

    X = pdf[['amount', 'hour', 'location_encoded']].values

    model = IsolationForest(contamination=0.1)
    preds = model.fit_predict(X)

    pdf['anomaly'] = preds
    print("\n=== Anomaly Detection Result ===")
    print(pdf)
    save_to_postgres(pdf)

    # Lọc các giao dịch có anomaly = -1 (anomaly)
    anomalies = pdf[pdf['anomaly'] == -1]

    # Lưu các giao dịch có anomaly = -1 vào bảng transactions_anomaly
    save_to_postgres_anomalies(anomalies)



df_parsed.writeStream \
    .foreachBatch(process_batch) \
    .start() \
    .awaitTermination()
