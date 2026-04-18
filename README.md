# Setup

```
$ pip install -r requirements.txt
```

# How to use

Put files into data/.

```
$ python3 ingest.py
$ ollama pull mistral
$ uvicorn app:app --reload
$ streamlit run ui/streamlit_app.py
```

Access to http://localhost:8501