import os
import datetime
import json

PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "util/cached_queries")
os.makedirs(CACHE_DIRECTORY, mode=0o777, exist_ok=True)
now = datetime.datetime.now()


def get_cached_query(filename):
	if not filename.endswith(".sql"):
		return {}
	filename = filename[:-4]
	full_path = os.path.join(CACHE_DIRECTORY, filename, ".json")
	if not os.path.isfile(full_path):
		return {}
	return json.load(open(full_path))