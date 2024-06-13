from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.get("/")
async def read_versions():
	return {
		'boost_posts_stories_soc-proof': '1.0',
		'multi-autojoin': '1.0',
		'auto-answer': '1.0'
	}