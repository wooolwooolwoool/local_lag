# 📚 Local RAG (Multi-DB) — README

完全ローカルで動作する **RAG（Retrieval-Augmented Generation）システム**です。
Word / Excel / ソースコードなどの社内ドキュメントをインデックス化し、**出典付きで回答**を返します。

---

# ■ 特徴

* 🔒 完全ローカル（外部通信なしで運用可能）
* 📂 データベース（DB）単位で分離（プロジェクトごとに管理）
* ⚡ 高速検索（ベクトル検索 + BM25）
* 📄 出典（ファイル名）付き回答
* 🧩 拡張しやすいシンプル構成

---

# ■ ディレクトリ構成

```
rag/
 ├── data/               # 元データ（DBごとにディレクトリ分け）
 │    ├── projectA/
 │    ├── projectB/
 │
 ├── index/              # インデックス保存（自動生成）
 │    ├── projectA/
 │    ├── projectB/
 │
 ├── ingest.py           # インデックス作成
 ├── retriever.py        # 検索処理
 ├── app.py              # API（FastAPI）
 ├── llm.py              # LLM呼び出し（Ollama）
 ├── ui/
 │    └── streamlit_app.py  # UI
```

---

# ■ 対応ファイル形式（デフォルト）

* `.txt`, `.md`
* `.c`, `.cpp`, `.h`, `.hpp`
* `.docx`
* `.xlsx`, `.xlsm`

---

# ■ セットアップ

## 1. 依存ライブラリ

```
pip install -r requirements.txt
```

---

## 2. ローカルLLM起動

Ollama を使用：

```
ollama run mistral
```

---

## 3. データ配置

```
data/projectA/
 ├── spec.docx
 ├── code.cpp
 └── data.xlsx
```

---

## 4. インデックス作成

```
python ingest.py projectA
```

---

## 5. API起動

```
uvicorn app:app --reload
```

---

## 6. UI起動

```
streamlit run ui/streamlit_app.py
```

---

# ■ 使い方

## ① DB選択

UIのサイドバーから対象DB（例：projectA）を選択

## ② 質問入力

例：

```
APIのタイムアウトは？
```

## ③ 回答取得

```
回答:
タイムアウトは30秒です

出典:
- spec.docx
- api_design.md
```

---

## ④ 新規DB追加

UIから：

1. DB名を入力
2. 「DB作成」
3. `data/<DB名>/` にファイルを配置
4. 「インデックス作成」

---

# ■ アーキテクチャ概要

```
[ファイル]
   ↓
[チャンク分割]
   ↓
[Embedding]
   ↓
[FAISS + BM25]
   ↓
[検索]
   ↓
[LLM]
   ↓
[回答]
```

---

# ■ 拡張ガイド

---

# ① 新しいファイルフォーマットを追加

編集箇所：`ingest.py`

---

## 手順

### 1. 読み込み関数を追加

```python
def read_pdf(path):
    ...
```

---

### 2. チャンク分割関数（必要なら）

```python
def chunk_pdf(text):
    ...
```

---

### 3. ingest内に追加

```python
elif ext == ".pdf":
    text = read_pdf(path)
    chunks = chunk_pdf(text)
```

---

👉 ポイント：

* **テキスト抽出品質が最重要**
* 構造（見出し・段落）を壊さない

---

# ② チャンク分割ロジックの改善

編集箇所：`ingest.py`

---

例：

```python
def chunk_text(text, size=500, overlap=50):
```

---

改善案：

* 見出しベース分割（Word）
* 関数単位分割（コード）
* テーブル単位（Excel）

---

👉 精度に直結する最重要ポイント

---

# ③ 検索アルゴリズム改善

編集箇所：`retriever.py`

---

## 現在

* ベクトル検索（FAISS）
* BM25

---

## 拡張例

### リランキング追加

```python
# cross-encoder導入
```

---

### スコア融合

```python
final_score = vector_score + bm25_score
```

---

# ④ LLM変更

編集箇所：`llm.py`

---

変更例：

```python
def generate(prompt, model="llama3"):
```

---

👉 モデルを変えるだけでOK

---

# ⑤ UI拡張

編集箇所：`ui/streamlit_app.py`

---

追加例：

* ファイルアップロード
* 出典クリックでファイル表示
* ハイライト表示

---

# ⑥ DB横断検索（応用）

編集箇所：`retriever.py`

---

```python
for db in db_list:
    results += search(db)
```

---

👉 複数DB統合検索が可能

---

# ■ 運用のコツ（重要）

---

## ✔ インデックスは頻繁に更新しない

* 差分更新が理想（将来拡張）

---

## ✔ データは整理しておく

悪い例：

```
data/projectA/misc/random.txt
```

良い例：

```
data/projectA/spec/
data/projectA/code/
```

---

## ✔ チャンクサイズ調整

* 小さすぎ → 文脈不足
* 大きすぎ → ノイズ増加

---

# ■ トラブルシュート

---

## Q. 検索精度が低い

原因：

* チャンク分割が悪い
* BM25が弱い

対策：

* チャンク改善
* リランキング追加

---

## Q. 遅い

原因：

* CPUのみ
* インデックス巨大

対策：

* GPU導入
* キャッシュ追加

---

## Q. ファイルが読めない

原因：

* encoding
* ライブラリ不足

対策：

* `errors="ignore"`使用
* ログ確認

---

# ■ 今後の拡張（おすすめ）

* 差分インデックス更新
* ファイル監視（自動更新）
* tree-sitterによるコード解析
* React UI化
* 権限管理

---

# ■ ライセンス

社内利用想定（必要に応じて設定）

---

# ■ まとめ

* シンプル構成で拡張しやすい
* DB単位で管理できる
* 完全ローカルで安全

👉 **小規模から始めて、段階的に強化できるRAG基盤**
