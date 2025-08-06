import streamlit as st
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Streamlit setup ---
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System (with Real Posters)")

# --- Load CSVs ---
try:
    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")
except FileNotFoundError:
    st.error(
        "CSV files not found. Make sure 'tmdb_5000_movies.csv' and 'tmdb_5000_credits.csv' are in the same folder as this script.")
    st.stop()

# --- Merge & Fix poster_path ---
movies = movies.merge(credits, on='title')
if 'poster_path_x' in movies.columns:
    movies['poster_path'] = movies['poster_path_x']
elif 'poster_path_y' in movies.columns:
    movies['poster_path'] = movies['poster_path_y']
elif 'poster_path' not in movies.columns:
    movies['poster_path'] = ""


# --- Helper functions ---
def convert(obj):
    try:
        return [i['name'] for i in ast.literal_eval(obj)]
    except:
        return []


def get_director(obj):
    try:
        for i in ast.literal_eval(obj):
            if i['job'] == 'Director':
                return i['name']
    except:
        return ""
    return ""


def collapse(L):
    return " ".join(L)


def get_poster_url(path):
    if pd.isna(path) or path.strip() == "":
        return "https://via.placeholder.com/300x450?text=No+Image"
    return f"https://image.tmdb.org/t/p/w500{path}"


# --- Process data ---
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x: convert(x)[:3])
movies['crew'] = movies['crew'].apply(get_director)

movies['cast'] = movies['cast'].apply(collapse)
movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)

movies['tags'] = (
        movies['overview'] + " " +
        movies['genres'] + " " +
        movies['keywords'] + " " +
        movies['cast'] + " " +
        movies['crew']
)

df = movies[['movie_id', 'title', 'tags', 'poster_path']].dropna()
df['tags'] = df['tags'].apply(lambda x: str(x).lower())

# --- Vectorize and calculate similarity ---
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(df['tags']).toarray()
similarity = cosine_similarity(vectors)


# --- Recommendation function ---
def recommend(movie):
    movie = movie.lower()
    if movie not in df['title'].str.lower().values:
        return [], []
    index = df[df['title'].str.lower() == movie].index[0]
    distances = list(enumerate(similarity[index]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]

    titles, posters = [], []
    for i in distances:
        titles.append(df.iloc[i[0]].title)
        posters.append(get_poster_url(df.iloc[i[0]].poster_path))
    return titles, posters


# --- UI ---
selected_movie = st.selectbox("🎥 Select a movie you like:", df['title'].values)

if st.button("Recommend"):
    titles, posters = recommend(selected_movie)
    if not titles:
        st.warning("Movie not found.")
    else:
        st.markdown("### 🎯 You may also like:")
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.image(posters[i], use_container_width=True)
                st.caption(titles[i])
