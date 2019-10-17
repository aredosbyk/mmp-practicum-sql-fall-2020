import os
import datetime
import json

PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "util/cached_queries")
os.makedirs(CACHE_DIRECTORY, mode=0o777, exist_ok=True)
now = datetime.datetime.now()


def get_cached_query(file_path):
	if not file_path.endswith(".sql") or not os.path.isfile(file_path):
		return {}
	with open(file_path, 'r', encoding='utf-8') as f:
        content = "".join(f.readlines()).replace(';', '')
	file_path = file_path[:-4]
	full_path = os.path.join(CACHE_DIRECTORY, file_path, ".json")
	if not os.path.isfile(full_path):
		return {}
	cached_query = json.load(open(full_path))
	if cached_query['valid_until'] < now or cached_query['sql'] != content:
		os.remove(full_path)
		return {}
	return cached_query
