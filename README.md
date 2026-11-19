# Code Plagiarism Detector

## Setup
```
python -m venv venv
venv\Scripts\activate        # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

## Run the web app
```
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000, upload .py files (try the ones in `data/samples/`), click **Analyze all pairs**.

## Evaluate (for the report)
```
python data/generate_dataset.py
python notebooks/evaluation.py
```

## Shorten a file (make code compact)
In the web app, click **Shorten** next to any uploaded file. Or from the terminal:
```
python -m app.compress data/messy_example.py
```
This writes `messy_example.short.py` and prints what was changed. It is rule-based: removes comments/docstrings,
unused imports, dead code, merges duplicate functions, turns append-loops into list comprehensions.
Always re-run your tests on the shortened file.

## AI shortening with Groq (optional)
1. Get a key at https://console.groq.com/keys
2. Copy `.env.example` to `.env` and put the key after `GROQ_API_KEY=` (no quotes, no spaces)
3. `pip install -r requirements.txt` again (adds httpx), restart the server
4. Click the **AI** button next to a file. The code is sent to Groq, and every answer is checked
   (must parse, same function names/signatures) before it is accepted; otherwise the safe rule-based version is kept.
If Groq says the model is not found, set `GROQ_MODEL` in `.env` (see https://console.groq.com/docs/models).

## Diagrams for the report
```
python docs/diagram_architecture.py
python docs/diagram_flowchart.py
```
Creates `docs/architecture_diagram.png` and `docs/flowchart.png`. Edit the text inside the scripts to change the labels.

## Learned model + ablation (ML part of the report)
```
python data/generate_dataset.py          # 127 files, 297 labelled pairs (10 problems)
python notebooks/train_classifier.py     # ablation table, ROC chart, saves models/classifier.joblib
```
Compares token-only, AST-only, hand-weighted fusion, Logistic Regression and Random Forest with
cross-validation grouped by problem. To make the web app use the learned model, add
`USE_LEARNED_MODEL=1` to `.env` and restart the server.

## Optional semantic layer (CodeBERT)
```
pip install torch transformers
```
Then tick the "Include semantic score" box in the UI, or set `USE_SEMANTIC = True` in `notebooks/evaluation.py`.

## Layout
- app/preprocess.py   comment/format/identifier normalization
- app/token_sim.py    TF-IDF + cosine over token n-grams
- app/ast_sim.py      AST comparison + matched regions
- app/semantic_sim.py CodeBERT embeddings (optional)
- app/compress.py     shortens a file (rule-based, behaviour-preserving)
- app/ai_compress.py  Groq-powered shortening with safety checks
- app/config.py       loads .env
- app/fusion.py       weighted score fusion + risk level
- app/db.py           SQLite storage
- app/main.py         FastAPI endpoints
- frontend/index.html dashboard
- data/               dataset generator, samples, pairs.csv
- notebooks/          evaluation script
