from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import sys, math, os

@dataclass(frozen=True)
class Movie:
    movie_id: str
    name: str
    genre: str

@dataclass(frozen=True)
class Rating:
    user_id: str
    movie_name: str
    rating: float

class DataStore:
    def __init__(self) -> None:
        self.movies_by_name: Dict[str, Movie] = {}
        self.ratings_by_movie: Dict[str, List[Rating]] = {}
        self.ratings_by_user: Dict[str, List[Rating]] = {}

    def load_movies(self, filepath: str) -> None:
        self.movies_by_name.clear()
        with open(filepath, "r", encoding="utf-8") as f:
            for i, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line: continue
                parts = line.split("|")
                if len(parts) != 3:
                    raise ValueError(f"Movies line {i} malformed: {line}")
                genre, movie_id, movie_name = [p.strip() for p in parts]
                if movie_name in self.movies_by_name:
                    raise ValueError(f"Duplicate movie: {movie_name}")
                self.movies_by_name[movie_name] = Movie(movie_id, movie_name, genre)

    def load_ratings(self, filepath: str) -> None:
        self.ratings_by_movie.clear()
        self.ratings_by_user.clear()
        seen = set()
        with open(filepath, "r", encoding="utf-8") as f:
            for i, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line: continue
                parts = line.split("|")
                if len(parts) != 3:
                    raise ValueError(f"Ratings line {i} malformed: {line}")
                movie_name, rating_str, user_id = [p.strip() for p in parts]
                try:
                    rating = float(rating_str)
                except ValueError:
                    raise ValueError(f"Invalid rating: {rating_str}")
                if not (0 <= rating <= 5):
                    raise ValueError(f"Rating out of range [0,5]: {rating}")
                if (user_id, movie_name) in seen:
                    raise ValueError(f"Duplicate rating for {movie_name} by {user_id}")
                seen.add((user_id, movie_name))
                if movie_name not in self.movies_by_name:
                    continue
                r = Rating(user_id, movie_name, rating)
                self.ratings_by_movie.setdefault(movie_name, []).append(r)
                self.ratings_by_user.setdefault(user_id, []).append(r)

    def _avg(self, movie: str) -> Optional[float]:
        rs = self.ratings_by_movie.get(movie, [])
        if not rs: return None
        return sum(r.rating for r in rs)/len(rs)

    def _movies_in_genre(self, g: str):
        return [m.name for m in self.movies_by_name.values() if m.genre == g]

    def top_movies(self, n: int):
        rows = [(m, self._avg(m), len(self.ratings_by_movie.get(m, []))) for m in self.movies_by_name]
        rows = [r for r in rows if r[1] is not None]
        rows.sort(key=lambda x:(x[1],x[2],x[0]), reverse=True)
        return rows[:n]

    def top_movies_in_genre(self, g: str, n: int):
        rows = [(m, self._avg(m), len(self.ratings_by_movie.get(m, []))) for m in self._movies_in_genre(g)]
        rows = [r for r in rows if r[1] is not None]
        rows.sort(key=lambda x:(x[1],x[2],x[0]), reverse=True)
        return rows[:n]

    def top_genres(self, n: int):
        g2a: Dict[str, List[float]] = {}
        for m in self.movies_by_name.values():
            a = self._avg(m.name)
            if a is not None:
                g2a.setdefault(m.genre, []).append(a)
        rows = [(g, sum(v)/len(v), len(v)) for g,v in g2a.items()]
        rows.sort(key=lambda x:(x[1],x[2],x[0]), reverse=True)
        return rows[:n]

    def user_preferred_genre(self, u: str):
        rs = self.ratings_by_user.get(u, [])
        g2a: Dict[str, List[float]] = {}
        for r in rs:
            m = self.movies_by_name.get(r.movie_name)
            if not m: continue
            a = self._avg(r.movie_name)
            if a is None: continue
            g2a.setdefault(m.genre, []).append(a)
        if not g2a: return None
        best = sorted([(g,sum(v)/len(v)) for g,v in g2a.items()], key=lambda x:(x[1],x[0]), reverse=True)
        return best[0]

    def recommend_for_user(self, u: str, k: int=3):
        pref = self.user_preferred_genre(u)
        if not pref: return []
        g = pref[0]
        rated = {r.movie_name for r in self.ratings_by_user.get(u, [])}
        rows = [(m, self._avg(m), len(self.ratings_by_movie.get(m, []))) for m in self._movies_in_genre(g) if m not in rated]
        rows = [r for r in rows if r[1] is not None]
        rows.sort(key=lambda x:(x[1],x[2],x[0]), reverse=True)
        return rows[:k]

def main():
    ds = DataStore()
    while True:
        print("""\nMovie Recommender — Menu
1) Load movies file
2) Load ratings file
3) Top N movies (overall)
4) Top N movies in a genre
5) Top N genres
6) User's preferred genre
7) Recommend movies for a user
8) Quit""")
        c = input("Choice: ").strip()
        if c=="1":
            p = input("Enter path to movies file: ").strip()
            ds.load_movies(p); print(f"Loaded {len(ds.movies_by_name)} movies.")
        elif c=="2":
            p = input("Enter path to ratings file: ").strip()
            ds.load_ratings(p); print("Ratings loaded.")
        elif c=="3":
            n=int(input("N = ") or "10")
            for m,a,cnt in ds.top_movies(n):
                print(f"{m:40s} {a:4.2f} ({cnt})")
        elif c=="4":
            g=input("Genre = ").strip(); n=int(input("N = ") or "10")
            for m,a,cnt in ds.top_movies_in_genre(g,n):
                print(f"{m:40s} {a:4.2f} ({cnt})")
        elif c=="5":
            n=int(input("N = ") or "10")
            for g,a,cnt in ds.top_genres(n):
                print(f"{g:15s} {a:4.2f} ({cnt})")
        elif c=="6":
            u=input("User ID = ").strip(); res=ds.user_preferred_genre(u)
            print("(no data)" if not res else f"{res[0]} ({res[1]:.2f})")
        elif c=="7":
            u=input("User ID = ").strip(); k=int(input("How many? ") or "3")
            for m,a,cnt in ds.recommend_for_user(u,k):
                print(f"{m:40s} {a:4.2f} ({cnt})")
        elif c=="8":
            break
        else:
            print("Invalid choice.")

if __name__=="__main__":
    main()
