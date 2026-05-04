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

#.env, cors and configurations:
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
#Path configurations.
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

# This is for getting the details of the movie from tmdb and then it will return me the data of that movie in the form of dictionary and then i will use that data for recommendation
async def tmdb_movie_details(movie_id: int) -> TMDBMovieDetails:
    data = await tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})
    return TMDBMovieDetails(
        tmdb_id=int(data["id"]),
        title=data.get("title") or "",
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=make_img_url(data.get("poster_path")),
        backdrop_url=make_img_url(data.get("backdrop_path")),
        genres=data.get("genres", []) or [],
    )


# This is for searching the movie from tmdb and then it will return me the data of that movie in the form of dictionary and then i will use that data for recommendation
async def tmdb_search_movies(query: str, page: int = 1) -> Dict[str, Any]:
    return await tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": False,
            "language": "en-US",
            "page": page,
        }
    )


# This is for searching the movie from tmdb and then it will return me the data of that movie in the form of dictionary and then i will use that data for recommendation but this will return me only the first result of that movie which means if user type in small it will also give me the same result as if user type in capital and also if user type in space it will also give me the same result as if user type in without space
async def tmdb_search_first(query: str) -> Optional[dict]:
    data = await tmdb_search_movies(query=query, page=1)
    results = data.get("results", [])
    return results[0] if results else None


def build_title_to_idx_map(indices: Any) -> Dict[str, int]:
    title_to_idx: Dict[str, int] = {}

    if isinstance(indices, dict):
        for k, v in indices.items():
            title_to_idx[_norm_title(k)] = int(v)
        return title_to_idx
    
    #Pandas sreies or similar mapping:
    try:
        for k, v in indices.items():
            title_to_idx[_norm_title(k)] = int(v)
        return title_to_idx
    except Exception:
        raise RuntimeError("indices.pkl must be a dict or pandas Sereis-like (with .items())")
    


# This is for getting the index of the movie from the title of the movie and then it will return me the index of that movie in the form of integer and then i will use that index for recommendation
def get_local_idx_by_title(title: str) -> int:
    global TITLE_TO_IDX
    if TITLE_TO_IDX is None:
        raise HTTPException(status_code=500, detail="TF-IDF indices map not initialized")
    
    key = _norm_title(title)
    if key in TITLE_TO_IDX:
        return int(TITLE_TO_IDX[key])
    raise HTTPException(
        status_code=404, detail=f"Title not found in local dataset: '{title}'"
    )



def tfidf_recommend_titles(
        query_title: str, top_n: int = 10
) -> List[Tuple[str, float]]:
    global df, tfidf_matrix
    if df is None or tfidf_matrix is None:
        raise HTTPException(status_code=500, detail='TF-IDF resources not loaded')
    
    idx = get_local_idx_by_title(query_title)

    #query vector
    qv = tfidf_matrix[idx]
    scores = (tfidf_matrix @ qv.T).toarray().ravel()

    #sort descending
    order = np.argsort(-scores)

    out: List[Tuple[str, float]] = []
    for i in order:
        if int(i) == int(idx):
            continue
        try:
            title_i = str(df.iloc[int(i)]["title"])
        except Exception:
            continue
        out.append((title_i, float(scores[int(i)])))
        if len(out) >= top_n:
            break       
    return out
    

# This is for getting the tmdb card of the movie from the title of the movie and then it will return me the tmdb card of that movie in the form of TMDBMovieCard and then i will use that tmdb card for recommendation
async def attach_tmdb_card_by_title(title: str) -> Optional[TMDBMovieCard]:
    try:
        m = await tmdb_search_first(title)
        if not m:
            return None
        return TMDBMovieCard(
            tmdb_id=int(m["id"]),
            title=m.get("title") or title,
            poster_url=make_img_url(m.get("poster_path")),
            release_date=m.get("release_date"),
            vote_average=m.get("vote_average"),
        )
    except Exception:   
        return None
    

#This code is like when my API is running mode i want this will in running mode it will load the pickles and then it will store the data in the global variables and then i will use that data for recommendation.
# STARTUP: LOAD PICKLES
@app.on_event("startup")
def load_pickles():
    global df, indices_obj, tfidf_matrix, tfidf_obj, TITLE_TO_IDX

    # Load df
    with open(DF_PATH, "rb") as f:
        df = pickle.load(f)

    # Load indices
    with open(INDICES_PATH, "rb") as f:
        indices_obj = pickle.load(f)

    # Load TF_IDF matrix (usually scipy sparse)
    with open(TFIDF_MATRIX_PATH, "rb") as f:
        tfidf_matrix = pickle.load(f)

    #Load tfidf vectorizer (optional, not used directly here)
    with open(TFIDF_PATH, "rb") as f:
        tfidf_obj = pickle.load(f)

    #Build normalized map
    TITLE_TO_IDX = build_title_to_idx_map(indices_obj)

    #sanity
    if df is None or "title" not in df.columns:
        raise RuntimeError("df.pkl must contain a Dataframe with a 'title' column" )
    

#ROUTES
@app.get("/health")
def health():
    return{"status": "ok"}

@app.get("/home", response_model=List[TMDBMovieCard])
async def home(
    category: str = Query("popular"),
    limit: int = Query(24, get=1, le=50)
):
    try:
        if category == "trending":
            data = await tmdb_get("/trending/movie/day", {"language": "en-US"})
            return await tmdb_cards_from_results(data.get("results", []), limit=limit)
        