import os
import guessit
import shutil
import requests
import time
import json
import sys

# Expanded list of predefined genres
GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "Game-Show",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "News",
    "Reality-TV",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Talk-Show",
    "Thriller",
    "War",
    "Western",
    "Action-Comedy",
    "Action-Horror",
    "Action-Adventure",
    "Adventure-Comedy",
    "Adventure-Fantasy",
    "Animation-Action",
    "Animation-Comedy",
    "Animation-Drama",
    "Animation-Family",
    "Biography-Drama",
    "Biography-History",
    "Comedy-Drama",
    "Comedy-Romance",
    "Crime-Drama",
    "Crime-Thriller",
    "Documentary-Biography",
    "Documentary-Drama",
    "Documentary-Music",
    "Drama-Family",
    "Drama-Mystery",
    "Drama-Romance",
    "Fantasy-Adventure",
    "Fantasy-Action",
    "Fantasy-Drama",
    "Fantasy-Romance",
    "Film-Noir-Crime",
    "Film-Noir-Drama",
    "Game-Show-Music",
    "History-Drama",
    "History-Romance",
    "Horror-Comedy",
    "Horror-Mystery",
    "Horror-Thriller",
    "Music-Drama",
    "Music-Romance",
    "Musical-Comedy",
    "Musical-Drama",
    "Mystery-Drama",
    "Mystery-Romance",
    "News-Talk-Show",
    "Reality-TV-Game-Show",
    "Romance-Comedy",
    "Romance-Drama",
    "Sci-Fi-Action",
    "Sci-Fi-Adventure",
    "Sci-Fi-Drama",
    "Sci-Fi-Thriller",
    "Sport-Drama",
    "Sport-Documentary",
    "Talk-Show-Comedy",
    "Talk-Show-Drama",
    "Thriller-Action",
    "Thriller-Crime",
    "Thriller-Drama",
    "War-Drama",
    "War-History",
    "Western-Action",
    "Western-Drama",
    "Western-Romance",
    "Anime",
    "Biopic",
    "Docudrama",
    "Experimental",
    "Historical",
    "Neo-Noir",
    "Superhero",
    "Survival",
    "Urban",
    "Zombie",
]


# Fetch movie details from OMDB API
def fetch_movie_details(title, api_key, retries=3, delay=5):
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            movie_data = response.json()
            if movie_data.get("Response") == "True":
                return movie_data
            else:
                print(json.dumps({"error": movie_data.get("Error")}))
                return None
        except requests.RequestException as e:
            print(json.dumps({"error": str(e)}))
        time.sleep(delay)
    print(json.dumps({"error": "Failed to fetch details"}))
    return None


# Sanitize filenames
def sanitize_filename(filename):
    return "".join(
        char for char in filename if char.isalnum() or char in " ._-"
    ).strip()


# Create genre folders and Manual Checking folder
def create_folders(main_directory):
    for genre in GENRES:
        genre_folder = os.path.join(main_directory, genre)
        if not os.path.exists(genre_folder):
            os.makedirs(genre_folder)
    manual_checking_folder = os.path.join(main_directory, "Manual Checking")
    if not os.path.exists(manual_checking_folder):
        os.makedirs(manual_checking_folder)


# Save movie info to a file
def save_movie_info(movie_data, movie_folder):
    title = sanitize_filename(movie_data.get("Title", "Unknown Title"))
    info_file_path = os.path.join(movie_folder, f"{title}_about.txt")
    with open(info_file_path, "w", encoding="utf-8") as file:
        json.dump(movie_data, file, indent=4)
    print(json.dumps({"saved_info": info_file_path}))


# Rename folders based on movie title
def rename_folders(main_directory):
    directories = [
        d
        for d in os.listdir(main_directory)
        if os.path.isdir(os.path.join(main_directory, d))
    ]
    total_dirs = len(directories)
    for i, directory in enumerate(directories):
        old_path = os.path.join(main_directory, directory)
        if directory in GENRES or directory == "Manual Checking":
            continue
        directory_with_spaces = directory.replace("-", " ")
        movie_info = guessit.guessit(directory_with_spaces)
        if "title" in movie_info:
            title = movie_info["title"]
            quality = movie_info.get("screen_size", "")
            new_name = f"{title} ({quality})" if quality else title
            new_name = sanitize_filename(new_name)
            new_path = os.path.join(main_directory, new_name)
            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    print(json.dumps({"renamed": f"{old_path} to {new_path}"}))
                except Exception as e:
                    print(json.dumps({"error": str(e)}))
        else:
            print(
                json.dumps(
                    {"error": f"Could not identify a movie name for '{directory}'"}
                )
            )
        # Print progress
        progress = (i + 1) / total_dirs * 100
        print(f"Progress: {progress:.2f}")


# Keep the best quality version of movies
def keep_best_quality(main_directory):
    best_versions = {}
    directories = [
        d
        for d in os.listdir(main_directory)
        if os.path.isdir(os.path.join(main_directory, d))
    ]
    total_dirs = len(directories)
    for i, directory in enumerate(directories):
        path = os.path.join(main_directory, directory)
        if directory in GENRES or directory == "Manual Checking":
            continue
        movie_info = guessit.guessit(directory)
        if "title" in movie_info:
            title = movie_info["title"]
            quality = movie_info.get("screen_size", "")
            if title in best_versions:
                existing_quality = best_versions[title].get("screen_size", "")
                if quality and (not existing_quality or quality > existing_quality):
                    lower_quality_path = best_versions[title]["path"]
                    try:
                        shutil.rmtree(lower_quality_path)
                        print(json.dumps({"removed": lower_quality_path}))
                    except Exception as e:
                        print(json.dumps({"error": str(e)}))
                    best_versions[title] = {"screen_size": quality, "path": path}
                else:
                    try:
                        shutil.rmtree(path)
                        print(json.dumps({"removed": path}))
                    except Exception as e:
                        print(json.dumps({"error": str(e)}))
            else:
                best_versions[title] = {"screen_size": quality, "path": path}
        else:
            print(
                json.dumps(
                    {"error": f"Could not identify a movie name for '{directory}'"}
                )
            )
        # Print progress
        progress = (i + 1) / total_dirs * 100
        print(f"Progress: {progress:.2f}")
    return best_versions


# Organize movies by genre
def organize_by_genre(main_directory, best_versions, api_key):
    create_folders(main_directory)
    movies_info_folder = os.path.join(main_directory, "movies info")
    if not os.path.exists(movies_info_folder):
        os.makedirs(movies_info_folder)
    total_movies = len(best_versions)
    for i, (title, info) in enumerate(best_versions.items()):
        path = info["path"]
        movie = fetch_movie_details(title, api_key)
        if movie:
            genres = movie.get("Genre", "").split(", ")
            main_genre = genres[0] if genres else None
            if main_genre and main_genre in GENRES:
                genre_folder = os.path.join(main_directory, main_genre)
                new_path = os.path.join(genre_folder, os.path.basename(path))
                if path != new_path:
                    try:
                        os.rename(path, new_path)
                        print(json.dumps({"moved": f"{path} to {genre_folder}"}))
                    except Exception as e:
                        print(json.dumps({"error": str(e)}))
                save_movie_info(movie, movies_info_folder)
            else:
                manual_checking_folder = os.path.join(main_directory, "Manual Checking")
                new_path = os.path.join(manual_checking_folder, os.path.basename(path))
                if path != new_path:
                    try:
                        os.rename(path, new_path)
                        print(json.dumps({"moved": f"{path} to Manual Checking"}))
                    except Exception as e:
                        print(json.dumps({"error": str(e)}))
                save_movie_info(movie, movies_info_folder)
        else:
            manual_checking_folder = os.path.join(main_directory, "Manual Checking")
            new_path = os.path.join(manual_checking_folder, os.path.basename(path))
            if path != new_path:
                try:
                    os.rename(path, new_path)
                    print(json.dumps({"moved": f"{path} to Manual Checking"}))
                except Exception as e:
                    print(json.dumps({"error": str(e)}))
        # Print progress
        progress = (i + 1) / total_movies * 100
        print(f"Progress: {progress:.2f}")
    for genre in GENRES:
        genre_folder = os.path.join(main_directory, genre)
        if os.path.exists(genre_folder) and not os.listdir(genre_folder):
            try:
                os.rmdir(genre_folder)
                print(json.dumps({"removed": genre_folder}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))


# Write summary to a file
def write_summary_to_file(main_directory):
    manual_checking_folder = os.path.join(main_directory, "Manual Checking")
    if os.path.exists(manual_checking_folder):
        manual_count = len(os.listdir(manual_checking_folder))
    else:
        manual_count = 0

    total_count = len(
        [
            d
            for d in os.listdir(main_directory)
            if os.path.isdir(os.path.join(main_directory, d))
        ]
    )

    summary_file = os.path.join(main_directory, "process_summary.txt")
    with open(summary_file, "w") as file:
        file.write(f"{manual_count} / {total_count} movies are in 'Manual Checking'\n")


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python organize_movies.py <directory>"}))
        return

    main_directory = sys.argv[1]
    api_key = "b933be1a"

    rename_folders(main_directory)
    best_versions = keep_best_quality(main_directory)
    organize_by_genre(main_directory, best_versions, api_key)
    write_summary_to_file(main_directory)


if __name__ == "__main__":
    main()
