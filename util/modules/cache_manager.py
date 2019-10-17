import os

PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "util/cached_queries")
os.makedirs(CACHE_DIRECTORY, mode=0o777, exist_ok=True)