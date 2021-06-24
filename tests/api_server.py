"""Fake api server to run the tests against."""

from typing import Dict

from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/existent")
async def existent() -> Dict[str, str]:
    """Return a status code of 200."""
    return {"msg": "exists!"}


@app.get("/inexistent")
async def inexistent() -> None:
    """Return a status code of 404."""
    raise HTTPException(status_code=404, detail="It doesn't exist")


@app.get("/wrong_404_page")
async def wrong_404_page() -> Dict[str, str]:
    """Return a 200 status code even if it's not found."""
    return {"msg": "404 error"}
