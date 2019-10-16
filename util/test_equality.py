#!/usr/bin/python3

import MySQLdb
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exit_code = 0
MAX_WORKERS = 5

def create_new_connection():
    return MySQLdb.connect(host = "localhost",
                           user = "root",
                           passwd = "root",
                           db = "srcdt",
                           charset = "utf8")


def get_sql_result(sql_query):
    connection = create_new_connection()
    cursor = connection.cursor()
    cursor.execute(sql_query)
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    return row


def get_sql_result_verbosed(sql_query, filename):
    print(f"Fetching {filename}...")
    sys.stdout.flush()
    start_time = time.perf_counter()
    result = get_sql_result(sql_query)
    end_time = time.perf_counter()
    print(f"Fetched {filename}. Time: {end_time - start_time} s")
    sys.stdout.flush()
    return result


class TaskInfo:
    __slots__ = ['task', 'subtask', 'ordered', 'skip']

    def __init__(self, task, subtask, skip=False, ordered=False):
        self.task = task
        self.subtask = subtask
        self.skip = skip
        self.ordered = ordered

    def get_folder(self):
        return os.path.join(PROJECT_DIRECTORY, f"task{self.task}")

    def get_file_regex(self):
        return re.compile(fr"[A-Z][a-z]*_{self.task}_{self.subtask}\.sql")

    def get_files(self):
        folder = self.get_folder()
        if not os.path.exists(folder):
            return []
        all_files = sorted(os.listdir(folder))
        re_files = self.get_file_regex()
        files = []
        for file in all_files:
            if re_files.fullmatch(file):
                if file == "Chernyshev_3_2.sql" or file == "Tashevtsev_3_2.sql":
                    continue
                files.append(file)
        return files

    def get_first_row(self, table):
        if self.ordered:
            return table[0]
        for first_row in sorted(table):
            return first_row
        return []

    def test(self):
        success = True
        if self.skip:
            return success
        folder = self.get_folder()
        sql_queries = []
        files = self.get_files()
        for file in files:
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                sql_queries.append("".join(f.readlines()).replace(';', ''))

        groups = {}
        queries = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for sql_query, filename in zip(sql_queries, files):
                while len(queries) >= 2 * MAX_WORKERS:
                    for completed_query in as_completed(queries):
                        break
                    cur_filename = queries[completed_query]
                    try:
                        result = completed_query.result()
                        if not self.ordered:
                            result = frozenset(result)
                    except Exception as e:
                        print(f"{cur_filename} -> Exception: {e}")
                        success = False 
                    else:
                        filenames = groups.get(result, [])
                        filenames.append(cur_filename)
                        groups[result] = filenames
                    del queries[completed_query]
                future_query = executor.submit(get_sql_result_verbosed, sql_query, filename)
                queries[future_query] = filename

            while len(queries) > 0:
                for completed_query in as_completed(queries):
                    break
                cur_filename = queries[completed_query]
                try:
                    result = completed_query.result()
                    if not self.ordered:
                        result = frozenset(result)
                except Exception as e:
                    print(f"{cur_filename} -> Exception: {e}")
                    success = False 
                else:
                    filenames = groups.get(result, [])
                    filenames.append(cur_filename)
                    groups[result] = filenames
                del queries[completed_query]
        
        if len(groups) > 0:
            print("-" * 25)
        if len(groups) > 1:
            success = False
            print(f"{self.task}.{self.subtask} -> ERROR!")
            for group_num, x in enumerate(groups):
                first_row = self.get_first_row(x)
                print(f"Group {group_num + 1} ({len(x)} rows, first row: {list(first_row)}):")
                for user in groups[x]:
                    print(f"\t{user[:user.find('_')]}")
            print()
            print("Differences between groups:")
            for i, group1 in enumerate(groups):
                if self.ordered:
                    group1 = frozenset(group1)
                for j, group2 in enumerate(groups):
                    if j <= i:
                        continue
                    if self.ordered:
                        group2 = frozenset(group2)
                    common_lines = group1.intersection(group2)
                    group1_only = group1.difference(common_lines)
                    group2_only = group2.difference(common_lines)
                    group1_example = []
                    group2_example = []
                    for group1_example in sorted(group1_only):
                        break
                    for group2_example in sorted(group2_only):
                        break
                    print(f"Group {i + 1} vs Group {j + 1}:")
                    print(f"\tCommon rows: {len(common_lines)} rows")
                    print(f"\tGroup {i + 1} only: {len(group1_only)} rows, first row: {list(group1_example)}")
                    print(f"\tGroup {j + 1} only: {len(group2_only)} rows, first row: {list(group2_example)}")
                    if self.ordered and len(group1_only) == 0 and len(group2_only) == 0:
                        print(f"\tOrder differs")
        elif len(groups) == 1:
            for x in groups:
                first_row = self.get_first_row(x)
                break
            print(f"{self.task}.{self.subtask} -> OK ({len(x)} rows, first row: {list(first_row)})")
        if len(groups) > 0:
            print("-" * 25)
        sys.stdout.flush()
        return success

tasks = [
    TaskInfo(1, 1, skip=True, ordered=False),
    TaskInfo(1, 2, skip=True, ordered=False),
    TaskInfo(1, 3, skip=True, ordered=True),

    TaskInfo(2, 1, skip=True, ordered=False),
    TaskInfo(2, 2, skip=True, ordered=False),
    TaskInfo(2, 3, skip=True, ordered=True),

    TaskInfo(3, 2, skip=False, ordered=False),
    TaskInfo(3, 3, skip=False, ordered=False),
    TaskInfo(3, 1, skip=False, ordered=False),

    TaskInfo(4, 1, skip=False, ordered=True),
    TaskInfo(4, 2, skip=False, ordered=False),
    TaskInfo(4, 3, skip=False, ordered=False)
]

for task in tasks:
    if not task.test():
        exit_code = 1

sys.exit(exit_code)
