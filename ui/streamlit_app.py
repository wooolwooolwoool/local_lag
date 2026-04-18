import streamlit as st
import requests
import time

API_URL = "http://localhost:8000/query"

st.set_page_config(page_title="Local RAG", layout="wide")

st.title("📚 Local RAG Search")

# ------------------------
# サイドバー（設定）
# ------------------------
st.sidebar.header("設定")

use_api = st.sidebar.checkbox("API経由で実行", value=True)

# ------------------------
# 履歴管理
# ------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------
# 入力UI
# ------------------------
query = st.text_input("質問を入力してください")

col1, col2 = st.columns([1, 5])
search_clicked = col1.button("検索")

# ------------------------
# 検索処理
# ------------------------
def query_api(q):
    res = requests.get(API_URL, params={"q": q})
    return res.json()

def query_local(q):
    # API使わず直接呼ぶ（デバッグ用）
    from retriever import hybrid_search
    from llm import generate

    results = hybrid_search(q)

    context = ""
    sources = set()

    for r in results:
        context += f"[{r['meta']['source']}]\n{r['text']}\n\n"
        sources.add(r["meta"]["source"])

    prompt = f"""
以下の情報のみを使って回答してください。
情報にない場合は「不明」と答えてください。

{context}

質問: {q}
"""
    answer = generate(prompt)

    return {"answer": answer, "sources": list(sources), "contexts": results}

# ------------------------
# 実行
# ------------------------
if search_clicked and query:
    with st.spinner("検索中..."):
        start = time.time()

        if use_api:
            res = query_api(query)
        else:
            res = query_local(query)

        elapsed = time.time() - start

    # 履歴保存
    st.session_state.history.insert(0, {
        "query": query,
        "result": res,
        "time": elapsed
    })

# ------------------------
# 結果表示
# ------------------------
if st.session_state.history:
    latest = st.session_state.history[0]

    st.subheader("🧠 回答")
    st.write(latest["result"]["answer"])

    st.caption(f"⏱ 応答時間: {latest['time']:.2f} sec")

    st.subheader("📄 出典")
    for s in latest["result"]["sources"]:
        st.write(f"- {s}")

    # ------------------------
    # デバッグ用：コンテキスト表示
    # ------------------------
    if st.checkbox("コンテキスト表示（デバッグ）"):
        if "contexts" in latest["result"]:
            for c in latest["result"]["contexts"]:
                with st.expander(f"{c['meta']['source']} (chunk {c['meta']['chunk_id']})"):
                    st.write(c["text"])

# ------------------------
# 履歴表示
# ------------------------
st.sidebar.subheader("履歴")

for h in st.session_state.history[:10]:
    if st.sidebar.button(h["query"]):
        st.session_state.history.insert(0, h)