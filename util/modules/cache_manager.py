import os
import datetime
import json

LINES_TO_SAVE = 50

PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "util/cached_queries")
os.makedirs(CACHE_DIRECTORY, mode=0o777, exist_ok=True)


def get_cached_query_file_path(file_path):
	file_path = os.path.basename(file_path)[:-4]
	full_path = os.path.join(CACHE_DIRECTORY, file_path, ".json")
	return full_path


def get_cached_query(file_path):
	if not file_path.endswith(".sql") or not os.path.isfile(file_path):
		return {}
	with open(file_path, 'r', encoding='utf-8') as f:
        content = "".join(f.readlines()).replace(';', '')
	full_path = get_cached_query_file_path(file_path)
	if not os.path.isfile(full_path):
		return {}
	cached_query = json.load(open(full_path))
	if cached_query['valid_until'] < datetime.datetime.now() or cached_query['sql'] != content:
		os.remove(full_path)
		return {}
	return cached_query

def set_cached_query(file_path, content, result):
	cached_query = {
		'sql': content,
		'valid_until': datetime.datetime.now() + timedelta(minutes=30),
		'rows': len(result),
		'data': result[:LINES_TO_SAVE]
	}
	full_path = get_cached_query_file_path(file_path)
	json.dump(cached_query, open(file_path))