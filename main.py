from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List
import httpx
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="BAEKJOON RANDOM PROBLEMS")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class Problem(BaseModel):
    problemId: int
    titleKo: str
    acceptedUserCount: int
    tier: str


@app.get("/boj", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/boj/problems/{tier}", response_model=List[Problem])
async def get_problems(tier: str):
    url = f"https://solved.ac/api/v3/search/problem?query=tier:{tier}&size=20&fields=problemId,titles,acceptedUserCount,averageTries,level&sort=random&direction=asc"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch problems"
        )

    problems_data = response.json().get("items", [])
    problems = []
    for problem in problems_data:
        title_ko = ""
        for title in problem.get("titles", []):
            if title.get("language") == "ko":
                title_ko = title.get("title")
                break
        if title_ko:  # Ensure we have a Korean title before adding the problem
            accepted_user_count = problem.get("acceptedUserCount", 0)
            tier = await convert_level_to_tier(problem.get("level", 0))
            problems.append(
                {
                    "problemId": problem.get("problemId"),
                    "titleKo": title_ko,
                    "acceptedUserCount": accepted_user_count,
                    "tier": tier,
                }
            )

    return problems


async def convert_level_to_tier(level):
    if level == 0:
        return "Unrated"
    tier = ["bronze", "silver", "gold", "platinum", "diamond"]
    tier_level = (level - 1) // 5
    sub_level = 5 - (level - 1) % 5
    return f"{tier[tier_level]}{sub_level}"
