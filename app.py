import streamlit as st
import pickle
import pandas as pd
import os

# Join similarity.pkl parts if full file not found
def join_parts(part_prefix, output_file, num_parts):
    with open(output_file, 'wb') as outfile:
        for i in range(num_parts):
            part_file = f"{part_prefix}.part{i}"
            if os.path.exists(part_file):
                with open(part_file, 'rb') as infile:
                    outfile.write(infile.read())
            else:
                st.error(f"Missing part: {part_file}")
                return False
    return True

# Ensure similarity.pkl is created from parts
if not os.path.exists("similarity.pkl"):
    join_parts("similarity.pkl", "similarity.pkl", 8)

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Movie recommender function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movie_list:
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies

# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations',
    movies['title'].values
)

if st.button('Recommend'):
    recommendations = recommend(selected_movie_name)
    st.subheader("Recommended Movies:")
    for i, movie in enumerate(recommendations, start=1):
        st.write(f"{i}. {movie}")
