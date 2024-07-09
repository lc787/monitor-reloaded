# Running a dev server
0. Get python 3.12
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Setup the environment file:
```bash
cp config.toml.example config.toml
nvim config.toml
```
3. Run project:
```bash
fastapi dev main.py
```

3.' Alternatively, to run a production server:
```bash
uvicorn main:app --host 0.0.0.0 --port <port>
```