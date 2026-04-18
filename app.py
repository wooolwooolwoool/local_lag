from fastapi import FastAPI
from retriever import hybrid_search
from llm import generate

app = FastAPI()

def build_prompt(query, contexts):
    context_text = ""
    sources = set()

    for c in contexts:
        context_text += f"[{c['meta']['source']}]\n{c['text']}\n\n"
        sources.add(c['meta']['source'])

    prompt = f"""
以下の情報のみを使って回答してください。
情報にない場合は「不明」と答えてください。

{context_text}

質問: {query}
"""
    return prompt, list(sources)


@app.get("/query")
def query(q: str, db: str):
    results = hybrid_search(q, db)

    prompt, sources = build_prompt(q, results)
    answer = generate(prompt)

    return {
        "answer": answer,
        "sources": sources
    }