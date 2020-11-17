#!/bin/bash
export FLASK_DEBUG=1
source .venv/bin/activate
{ python server/app.py & cd client && python3 -m http.server; }
fuser -k 8000/tcp
fuser -k 5000/tcp
