import os
import pickle
from typing import Optional, List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG_500 = "https://image.tmdb.org/t/p/w500"

if not TMDB_API_KEY:

    raise ValueError("TMDB_API_KEY not found in environment variables")


# This is Fast API Code
#For this we take paths of this and store the datas also in data folder and then we will load the data from there and then we will use that data for recommendation
app = FastAPI(title= "Movie Recommender API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#For Global Variables codes:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DF_PATH = os.path.join(BASE_DIR, "data", "movies_df.pkl")
INDICES_PATH = os.path.join(BASE_DIR, "data", "indices.pkl")
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, "data", "tfidf_matrix.pkl")
TFIDF_PATH = os.path.join(BASE_DIR, "data", "tfidf.pkl")

df: Optional[pd.DataFrame] = None
indices_obj: Any = None
tfidf_matrix: Any = None
tfidf_obj: Any = None


TITLE_TO_IDX: Optional[Dict[str, int]] = None

# Using Pidentic here because i dont want my data to split into multiple files and i want to keep it in one file and then i will load that file and then i will use that data for recommendation
class TMDBMovieCard(BaseModel):
    tmdb_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None

class TMDBMovieDetails(BaseModel):
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    backdrop_url: Optional[str] = None
    genres: List[str] = []

# This will match the score of my recommendation system with the movie title and then it will return the movie title and the score of that movie and also it will return the tmdb data of that movie if it is available
class TFDIFRecItem(BaseModel):
    title: str
    score: float
    tmdb: Optional[TMDBMovieCard] = None  


class SearchResponse(BaseModel):
    query: str
    movie_details: TMDBMovieDetails
    tfidf_recommendations: List[TFDIFRecItem]
    genre_recommendations: List[TFDIFRecItem]

#For Creating Utility Functions:
# This is for like if user type in small it will also give me the same result as if user type in capital and also if user type in space it will also give me the same result as if user type in without space
def _norm_title(t: str) -> str:
    return t.strip().lower() 

def make_img_url(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return f"{TMDB_IMG_500}{path}"

#There is also search function code: - 
#This is the basic utility function which means this will get movie to me from tmdb and then it will return me the data of that movie in the form of dictionary and then i will use that data for recommendation
async def tmdb_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safe TMDB GET:
    - Network errors -> 502
    - TMDB API errors -> 502 with details
    """
    q = dict(params)
    q["api_key"] = TMDB_API_KEY

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{TMDB_BASE}{path}", params=q)
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB request error: {type(e).__name__} | {repr(e)}",
        )
    
    if r.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB error: {r.status_code} | {r.text}",
        )
    
    return r.json()


async def tmdb_cards_from_results(
        results: List[Dict], limit: int = 20
) -> List[TMDBMovieCard]:
    out: List[TMDBMovieCard] = []
    for m in (results or [])[:limit]:
        out.append(
            TMDBMovieCard(
                tmdb_id=int(m.get("id")),
                title=m.get("title") or m.get("name") or "",
                poster_url=make_img_url(m.get("poster_path")),
                release_date=m.get("release_date"),
                vote_average=m.get("vote_average"),
            )
        )
        #For here this out will give me movie in particular card in proper format
    return out

