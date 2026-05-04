import html
import os

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# STYLES (minimal modern)
# =============================
st.markdown(
    """
<style>
.stApp {
    background:
        linear-gradient(120deg, rgba(229, 9, 20, .20), transparent 28%),
        linear-gradient(240deg, rgba(0, 178, 255, .14), transparent 30%),
        linear-gradient(180deg, #050507 0%, #101014 42%, #07070a 100%);
    color: #f5f5f7;
}
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 3rem;
    max-width: 1340px;
}
[data-testid="stSidebar"] {
    background: rgba(12, 12, 16, 0.68);
    border-right: 1px solid rgba(255, 255, 255, 0.10);
    box-shadow: 24px 0 70px rgba(0, 0, 0, 0.42);
    backdrop-filter: blur(28px) saturate(150%);
}
[data-testid="stSidebar"] * {
    color: #f5f5f7;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label {
    color: rgba(245, 245, 247, .72);
    font-size: .82rem;
    font-weight: 650;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.11);
    margin: 1.35rem 0;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    letter-spacing: -0.02em;
}
.sidebar-brand {
    margin: .45rem 0 1.1rem;
    padding: 1rem;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 22px;
    background: linear-gradient(145deg, rgba(255,255,255,.12), rgba(255,255,255,.045));
    box-shadow: inset 0 1px 0 rgba(255,255,255,.12), 0 18px 40px rgba(0,0,0,.24);
}
.sidebar-kicker {
    color: #ffb3b8;
    font-size: .75rem;
    font-weight: 750;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.sidebar-title {
    color: #ffffff;
    font-size: 1.45rem;
    font-weight: 850;
    letter-spacing: -0.03em;
    margin-top: .2rem;
}
.sidebar-note {
    color: rgba(245,245,247,.68);
    font-size: .82rem;
    line-height: 1.35;
    margin-top: .35rem;
}
.app-hero {
    text-align: center;
    padding: 2.3rem 2rem 1.85rem;
    margin: 0 auto 1.25rem;
    max-width: 980px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 32px;
    background: linear-gradient(145deg, rgba(255,255,255,.13), rgba(255,255,255,.045));
    box-shadow: inset 0 1px 0 rgba(255,255,255,.14), 0 26px 80px rgba(0,0,0,.38);
    backdrop-filter: blur(26px) saturate(145%);
}
.app-eyebrow {
    color: #ff3b45;
    font-size: .75rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}
.app-title {
    color: #ffffff;
    font-size: clamp(3.15rem, 6vw, 6.2rem);
    line-height: .95;
    font-weight: 900;
    letter-spacing: -0.065em;
    margin: .3rem 0 .75rem;
    text-shadow: 0 20px 70px rgba(229,9,20,.25);
}
.app-subtitle {
    color: rgba(245,245,247,.72);
    font-size: clamp(1.02rem, 1.55vw, 1.24rem);
    line-height: 1.45;
    max-width: 760px;
    margin: 0 auto;
}
.section-head {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 1rem;
    margin: 1.75rem 0 1rem;
}
.section-title {
    color: #ffffff;
    font-size: 1.72rem;
    line-height: 1.2;
    font-weight: 850;
    letter-spacing: -0.04em;
}
.small-muted {
    color: rgba(245,245,247,.64);
    font-size: .94rem;
}
.movie-title {
    color: #ffffff;
    font-size: .93rem;
    font-weight: 720;
    line-height: 1.18rem;
    min-height: 2.36rem;
    overflow: hidden;
    margin-top: .65rem;
    letter-spacing: -0.02em;
}
.movie-meta {
    color: rgba(245,245,247,.56);
    font-size: .78rem;
    line-height: 1rem;
    min-height: 1rem;
    margin-top: .15rem;
}
.poster-placeholder {
    aspect-ratio: 2 / 3;
    border: 1px dashed rgba(255,255,255,.22);
    border-radius: 18px;
    background: rgba(255,255,255,.06);
    color: rgba(245,245,247,.60);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: .85rem;
}
.stImage img {
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 22px 48px rgba(0, 0, 0, .48);
    transform: perspective(900px) translateZ(0) rotateX(0deg);
    transition: transform .22s ease, box-shadow .22s ease, filter .22s ease;
}
.stImage img:hover {
    transform: perspective(900px) translateY(-7px) translateZ(18px) rotateX(2deg) scale(1.025);
    box-shadow: 0 34px 75px rgba(0,0,0,.62), 0 0 0 1px rgba(255,255,255,.14);
    filter: saturate(1.12) contrast(1.05);
}
.stButton > button {
    width: 100%;
    min-height: 2.25rem;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, .14);
    background: linear-gradient(145deg, rgba(255,255,255,.16), rgba(255,255,255,.06));
    color: #ffffff;
    font-size: .86rem;
    font-weight: 700;
    transition: all .16s ease;
    backdrop-filter: blur(14px);
}
.stButton > button:hover {
    border-color: rgba(255,59,69,.72);
    background: linear-gradient(135deg, #e50914, #ff6a3d);
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 16px 36px rgba(229, 9, 20, .30);
}
.stTextInput input,
.stSelectbox [data-baseweb="select"] {
    border-radius: 16px;
}
.stTextInput input {
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.12);
    color: #ffffff;
    min-height: 3rem;
    backdrop-filter: blur(18px);
}
.stTextInput input::placeholder {
    color: rgba(245,245,247,.46);
}
[data-testid="stWidgetLabel"] {
    color: rgba(245,245,247,.78);
}
[data-baseweb="select"] > div {
    background: rgba(255,255,255,.10);
    border-color: rgba(255,255,255,.12);
    color: #ffffff;
}
.detail-shell {
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 26px;
    background: linear-gradient(145deg, rgba(255,255,255,.14), rgba(255,255,255,.055));
    padding: 1.55rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.14), 0 26px 76px rgba(0,0,0,.44);
    backdrop-filter: blur(26px) saturate(150%);
}
.detail-title {
    color: #ffffff;
    font-size: clamp(2rem, 4vw, 4.4rem);
    line-height: 1.04;
    font-weight: 900;
    letter-spacing: -0.06em;
    margin: 0 0 .65rem;
}
.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: .45rem;
    margin: .7rem 0 1rem;
}
.pill {
    border: 1px solid rgba(255,255,255,.13);
    background: rgba(255,255,255,.09);
    border-radius: 999px;
    color: rgba(255,255,255,.84);
    font-size: .8rem;
    font-weight: 700;
    padding: .25rem .62rem;
}
.overview {
    color: rgba(245,245,247,.78);
    font-size: 1.03rem;
    line-height: 1.65;
}
.cinema-banner {
    min-height: 260px;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 30px;
    margin: .75rem 0 1.25rem;
    background-size: cover;
    background-position: center;
    box-shadow: 0 30px 90px rgba(0,0,0,.52);
    overflow: hidden;
    position: relative;
}
.cinema-banner::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(5,5,7,.90), rgba(5,5,7,.48), rgba(5,5,7,.14));
}
.cinema-banner-content {
    position: relative;
    z-index: 1;
    padding: 2rem;
    max-width: 650px;
}
.cinema-label {
    color: #ff3b45;
    font-size: .75rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}
.api-ok {
    border: 1px solid rgba(48, 209, 88, .30);
    background: rgba(48, 209, 88, .12);
    color: #7dff9f;
    border-radius: 14px;
    padding: .68rem .78rem;
    font-size: .86rem;
    font-weight: 700;
}
.api-bad {
    border: 1px solid rgba(255, 69, 58, .34);
    background: rgba(255, 69, 58, .12);
    color: #ffb4ae;
    border-radius: 14px;
    padding: .68rem .78rem;
    font-size: .86rem;
    font-weight: 700;
}
.stTabs [data-baseweb="tab-list"] {
    gap: .35rem;
    border-bottom: 1px solid rgba(255,255,255,.10);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: .35rem .85rem;
    color: rgba(245,245,247,.72);
}
.stTabs [aria-selected="true"] {
    background: rgba(255,255,255,.12);
    color: #ffffff;
}
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 20px;
    background: rgba(255,255,255,.06);
    backdrop-filter: blur(18px);
}
[data-testid="stAlert"] {
    border-radius: 18px;
    background: rgba(255,255,255,.10);
    color: #ffffff;
    border-color: rgba(255,255,255,.12);
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)  # short cache for autocomplete
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


@st.cache_data(ttl=15)
def api_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.status_code == 200, None if r.status_code == 200 else r.text[:120]
    except Exception as e:
        return False, str(e)


def safe_text(value) -> str:
    return html.escape(str(value or ""))


def format_meta(movie: dict) -> str:
    release = (movie.get("release_date") or "")[:4]
    rating = movie.get("vote_average")
    parts = []
    if release:
        parts.append(release)
    if isinstance(rating, int | float):
        parts.append(f"{rating:.1f}/10")
    return " | ".join(parts)


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")
            meta = format_meta(m)

            with colset[c]:
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown(
                        "<div class='poster-placeholder'>No poster</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"<div class='movie-title'>{safe_text(title)}</div>"
                    f"<div class='movie-meta'>{safe_text(meta)}</div>",
                    unsafe_allow_html=True,
                )
                if st.button("View details", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "release_date": tmdb.get("release_date"),
                    "vote_average": tmdb.get("vote_average"),
                }
            )
    return cards


# =============================
# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]
# =============================
def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    # A) If API returns dict with 'results'
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )

    # B) If API returns already as list
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            # might be {tmdb_id,title,poster_url}
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )
    else:
        return [], []

    # Word-match filtering (contains)
    matched = [x for x in raw_items if keyword_l in x["title"].lower()]

    # If nothing matched, fallback to raw list (so never blank)
    final_list = matched if matched else raw_items

    # Suggestions = top 10 labels
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    # Cards = top N
    cards = [
        {
            "tmdb_id": x["tmdb_id"],
            "title": x["title"],
            "poster_url": x["poster_url"],
            "release_date": x.get("release_date"),
            "vote_average": x.get("vote_average"),
        }
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR (clean)
# =============================
CATEGORY_LABELS = {
    "trending": "Trending",
    "popular": "Popular",
    "top_rated": "Top Rated",
    "now_playing": "Now Playing",
    "upcoming": "Upcoming",
}

with st.sidebar:
    st.markdown(
        """
        <div class='sidebar-brand'>
            <div class='sidebar-kicker'>MovieLens</div>
            <div class='sidebar-title'>Discovery Studio</div>
            <div class='sidebar-note'>Browse TMDB films and explore recommendations from your local model.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    ok, health_err = api_health()
    if ok:
        st.markdown("<div class='api-ok'>API connected</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div class='api-bad'>API offline<br>{safe_text(health_err)}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("Home", use_container_width=True):
        goto_home()

    st.markdown("---")
    st.markdown("### Browse")
    selected_category_label = st.selectbox(
        "Browse category",
        list(CATEGORY_LABELS.values()),
        index=0,
    )
    home_category = next(
        key for key, value in CATEGORY_LABELS.items() if value == selected_category_label
    )
    grid_cols = st.slider("Grid columns", 4, 8, 6)
    st.markdown(
        f"<div class='sidebar-note'>Connected to<br>{safe_text(API_BASE)}</div>",
        unsafe_allow_html=True,
    )

# =============================
# HEADER
# =============================
st.markdown(
    """
    <div class='app-hero'>
        <div class='app-eyebrow'>Movie recommendations powered by TMDB and TF-IDF</div>
        <div class='app-title'>Movie Recommender</div>
        <div class='app-subtitle'>
            A focused movie discovery interface for browsing TMDB titles, opening rich
            detail pages, and comparing recommendations from your local TF-IDF model.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title",
        placeholder="Search Batman, Interstellar, Toy Story, The Matrix...",
    )

    # SEARCH MODE (Autocomplete + word-match results)
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                # Dropdown
                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Best matches", labels, index=0)

                    if selected != "-- Select a movie --":
                        # map label -> id
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown(
                    f"""
                    <div class='section-head'>
                        <div>
                            <div class='section-title'>Search results</div>
                            <div class='small-muted'>{len(cards)} titles matched "{safe_text(typed.strip())}"</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE
    feed_title = home_category.replace("_", " ").title()
    st.markdown(
        f"""
        <div class='section-head'>
            <div>
                <div class='section-title'>{safe_text(feed_title)}</div>
                <div class='small-muted'>Curated from TMDB and ready for recommendation browsing</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("Back to Home"):
            goto_home()
        st.stop()

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("<div class='section-title'>Movie details</div>", unsafe_allow_html=True)
    with b:
        if st.button("Back to Home"):
            goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    if data.get("backdrop_url"):
        st.markdown(
            f"""
            <div class='cinema-banner' style='background-image: url("{safe_text(data["backdrop_url"])}");'>
                <div class='cinema-banner-content'>
                    <div class='cinema-label'>Now viewing</div>
                    <div class='detail-title'>{safe_text(data.get("title", ""))}</div>
                    <div class='small-muted'>{safe_text((data.get("overview") or "")[:180])}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        if data.get("poster_url"):
            st.image(data["poster_url"], use_container_width=True)
        else:
            st.markdown(
                "<div class='poster-placeholder'>No poster</div>",
                unsafe_allow_html=True,
            )

    with right:
        release = data.get("release_date") or "-"
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
        genre_pills = "".join(
            f"<span class='pill'>{safe_text(g.get('name'))}</span>"
            for g in data.get("genres", [])
            if g.get("name")
        )
        if not genre_pills:
            genre_pills = "<span class='pill'>No genre data</span>"
        st.markdown(
            f"""
            <div class='detail-shell'>
                <div class='detail-title'>{safe_text(data.get('title', ''))}</div>
                <div class='small-muted'>Release date: {safe_text(release)}</div>
                <div class='pill-row'>{genre_pills}</div>
                <div class='section-title' style='font-size:1.05rem;margin-bottom:.35rem;'>Overview</div>
                <div class='overview'>{safe_text(data.get("overview") or "No overview available.")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if data.get("backdrop_url"):
        with st.expander("Backdrop", expanded=False):
            st.image(data["backdrop_url"], use_container_width=True)

    st.markdown(
        """
        <div class='section-head'>
            <div>
                <div class='section-title'>Recommendations</div>
                <div class='small-muted'>Switch between semantic similarity and TMDB genre discovery</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            tfidf_tab, genre_tab = st.tabs(["Similar by story text", "More from the same genre"])
            with tfidf_tab:
                poster_grid(
                    to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                    cols=grid_cols,
                    key_prefix="details_tfidf",
                )
            with genre_tab:
                poster_grid(
                    bundle.get("genre_recommendations", []),
                    cols=grid_cols,
                    key_prefix="details_genre",
                )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")
