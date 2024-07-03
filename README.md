# Running a dev server
0. Get python 3.12
1. Install requirements.txt:
```bash
pip install -r requirements.txt
```
2. Setup the environment file:
```bash
cp .env.example .env
nvim .env
```
3. Run project
```bash
fastapi dev main.py
```
