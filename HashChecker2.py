import os
import time
from collections import defaultdict
from multiprocessing import Pool, Manager, cpu_count
import mmap

# Конфигурация
user_file = "users.txt"
hash_files_dir = "./hashes/"
output_file = "leaked_users.txt"
MAX_PROCESSES = cpu_count()

def parse_users(file_path):
    users = {}
    hashes_set = set()
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or '$' in line.split(":")[0]:
                continue
            try:
                username, hash_value = line.split(":")
                hash_lower = hash_value.lower()
                users[hash_lower] = username
                hashes_set.add(hash_lower)
            except ValueError:
                continue
    return hashes_set, users

def check_hash_file(hash_file, hashes_set, users, hashes_dir, result_queue):
    """Проверяет один файл с хешами"""
    file_path = os.path.join(hashes_dir, hash_file)
    found = defaultdict(list)
    with open(file_path, "r+", encoding="utf-8", errors="ignore") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        for line in iter(mm.readline, b""):
            h = line.decode().strip().lower()
            if h in hashes_set:
                found[h].append(hash_file)
        mm.close()
    for h, files in found.items():
        result_queue.put((h, files))

def check_hashes(hashes_set, users, hashes_dir, output_path):
    """Многопроцессорная проверка"""
    hash_files = [f for f in os.listdir(hashes_dir) if f.startswith("hashes_")]
    manager = Manager()
    result_queue = manager.Queue()
    with Pool(processes=MAX_PROCESSES) as pool:
        pool.starmap(
            check_hash_file,
            [(f, hashes_set, users, hashes_dir, result_queue) for f in hash_files]
        )
    found_hashes = defaultdict(list)
    while not result_queue.empty():
        h, files = result_queue.get()
        found_hashes[h].extend(files)
    with open(output_path, "w") as out:
        for h, files in found_hashes.items():
            out.write(f"{users[h]} / {h} / {';'.join(files)}\n")

if __name__ == "__main__":
    start_time = time.time()
    print("Загрузка пользователей...")
    hashes_set, users = parse_users(user_file)
    print(f"Загружено пользователей: {len(users)}")
    print("Сканирование хешей...")
    check_hashes(hashes_set, users, hash_files_dir, output_file)
    print(f"Готово! Результаты в {output_file}")
    print(f"Время: {time.time() - start_time:.2f} сек")
