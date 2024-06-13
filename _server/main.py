from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.get("/")
async def read_versions():
	try:
		with open('versions.json', 'r') as f:
			data = json.load(f)
		return JSONResponse(content=data)
	except FileNotFoundError:
		return JSONResponse(content={"error": "File not found"})
