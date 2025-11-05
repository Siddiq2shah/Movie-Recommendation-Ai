test_code = '''from movie_recommender import DataStore

def setup_sample_data():
    ds = DataStore()
    movies = [
        "Action|m001|Die Hard (1988)",
        "Action|m002|The Dark Knight (2008)",
        "Comedy|m003|The Mask (1994)",
        "Drama|m004|The Shawshank Redemption (1994)",
        "Sci-Fi|m005|Inception (2010)",
        "Sci-Fi|m006|The Matrix (1999)",
        "Romance|m007|Titanic (1997)",
        "Animation|m008|Toy Story (1995)",
    ]
    ratings = [
        "Die Hard (1988)|4.5|u1",
        "Die Hard (1988)|5.0|u2",
        "The Dark Knight (2008)|5.0|u1",
        "The Dark Knight (2008)|4.5|u3",
        "The Mask (1994)|3.0|u2",
        "The Shawshank Redemption (1994)|5.0|u3",
        "The Shawshank Redemption (1994)|4.5|u1",
        "Inception (2010)|4.5|u1",
        "Inception (2010)|5.0|u2",
        "The Matrix (1999)|4.0|u3",
        "Titanic (1997)|4.0|u1",
        "Toy Story (1995)|4.5|u2"
    ]
    with open("test_movies.txt", "w", encoding="utf-8") as f:
        f.write("\\n".join(movies))
    with open("test_ratings.txt", "w", encoding="utf-8") as f:
        f.write("\\n".join(ratings))
    ds.load_movies("test_movies.txt")
    ds.load_ratings("test_ratings.txt")
    return ds

def run_tests():
    ds = setup_sample_data()
    print("\\n=== TEST 1: Top 3 Movies Overall ===")
    for m, avg, count in ds.top_movies(3):
        print(f"{m:40s} {avg:.2f} ({count})")
    print("\\n=== TEST 2: Top 2 Action Movies ===")
    for m, avg, count in ds.top_movies_in_genre("Action", 2):
        print(f"{m:40s} {avg:.2f} ({count})")
    print("\\n=== TEST 3: Top 3 Genres ===")
    for g, avg, count in ds.top_genres(3):
        print(f"{g:15s} {avg:.2f} ({count})")
    print("\\n=== TEST 4: Preferred Genre for u1 ===")
    result = ds.user_preferred_genre("u1")
    if result:
        print(f"{result[0]} ({result[1]:.2f})")
    else:
        print("(no data)")
    print("\\n=== TEST 5: Recommendations for u1 ===")
    for m, avg, count in ds.recommend_for_user("u1", 3):
        print(f"{m:40s} {avg:.2f} ({count})")

if __name__ == "__main__":
    run_tests()
'''

path = "/mnt/data/test_movie_recommender.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(test_code)

path