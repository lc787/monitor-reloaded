# Deployment
Get python 3.12.*.

Install dependencies:
```bash
pip install -r requirements.txt
```
Setup the config file:
```bash
cp config.toml.example config.toml
nvim config.toml
```
Run in dev:
```bash
fastapi dev main.py
```
Alternatively, to run a production server:
```bash
uvicorn main:app --host 0.0.0.0 --port <port>
```

# Releases
This service uses [semantic versioning](https://semver.org/).

# Contributing
Contributions welcome. Shoot us a PR! Or you can setup your own fork if you wanna. I'm not your boss.
