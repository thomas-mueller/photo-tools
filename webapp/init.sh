#! /bin/sh

virtualenv .photo-webapp
. .photo-webapp/bin/activate

pip install -r requirements.txt

uvicorn backend:app --reload --host 0.0.0.0 --port 8000
