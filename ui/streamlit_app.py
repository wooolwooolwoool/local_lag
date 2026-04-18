import streamlit as st
import requests
import os
import subprocess
import time

API_URL = "http://localhost:8000/query"
DATA_DIR = "data"

st.set_page_config(page_title="Local RAG", layout="wide")
st.title("📚 Local RAG (Multi-DB)")

# ------------------------
# DB一覧
# ------------------------
def list_dbs():
    if not os.path.exists(DATA_DIR):
        return []
    return [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]

db_list = list_dbs()

if not db_list:
    st.warning("データベースがありません。作成してください。")

selected_db = st.sidebar.selectbox("データベース選択", db_list)

# ------------------------
# 新規DB作成
# ------------------------
new_db = st.sidebar.text_input("新規DB名")

if st.sidebar.button("DB作成"):
    if new_db:
        os.makedirs(os.path.join(DATA_DIR, new_db), exist_ok=True)
        st.sidebar.success(f"{new_db} 作成完了")
        st.rerun()

# ------------------------
# インデックス作成
# ------------------------
if st.sidebar.button("インデックス作成"):
    if selected_db:
        subprocess.run(["python", "ingest.py", selected_db])
        st.sidebar.success("インデックス作成完了")

# ------------------------
# 履歴
# ------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------
# 入力
# ------------------------
query = st.text_input("質問を入力")

if st.button("検索") and query and selected_db:
    with st.spinner("検索中..."):
        start = time.time()
        res = requests.get(API_URL, params={"q": query, "db": selected_db}).json()
        elapsed = time.time() - start

    st.session_state.history.insert(0, {
        "query": query,
        "result": res,
        "time": elapsed,
        "db": selected_db
    })

# ------------------------
# 表示
# ------------------------
if st.session_state.history:
    h = st.session_state.history[0]

    st.subheader("回答")
    st.write(h["result"]["answer"])
    st.caption(f"⏱ {h['time']:.2f} sec | DB: {h['db']}")

    st.subheader("出典")
    for s in h["result"]["sources"]:
        st.write(f"- {s}")

# ------------------------
# 履歴表示
# ------------------------
st.sidebar.subheader("履歴")
for item in st.session_state.history[:10]:
    if st.sidebar.button(f"[{item['db']}] {item['query']}"):
        st.session_state.history.insert(0, item)