from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.get("/")
async def read_versions():
	return {
		'nakrutka_soc-proof': 1.1,
		'autojoin': 1.2,
		'autoanswer': 1.1,
		'autoreaction': 1.1
	}