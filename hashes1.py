import os
import time
from collections import defaultdict

# Конфигурация
user_file = "users.txt"              # файл с пользователями
hash_files_dir = "./hashes/"         # директория с файлами hashes_*
output_file = "leaked_users.txt"     # результат

def parse_users(file_path):
    users = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or '$' in line.split(":")[0]:
                continue
            try:
                username, hash_value = line.split(":")
                users[hash_value.lower()] = username
            except ValueError:
                continue
    return users

def check_hashes(users, hashes_dir, output_path):
    found_hashes = defaultdict(list)
    hash_files = [f for f in os.listdir(hashes_dir) if f.startswith("hashes_")]

    for hash_file in hash_files:
        file_path = os.path.join(hashes_dir, hash_file)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                h = line.strip().lower()
                if h in users:
                    if hash_file not in found_hashes[h]:
                        found_hashes[h].append(hash_file)

    with open(output_path, "w") as out:
        for h, files in found_hashes.items():
            username = users[h]
            out.write(f"{username} / {h} / {';'.join(files)}\n")

if __name__ == "__main__":
    start_time = time.time()
    
    users = parse_users(user_file)
    check_hashes(users, hash_files_dir, output_file)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Проверка завершена. Пользователей: {len(users)}")
    print(f"Результаты сохранены в: {output_file}")
    print(f"Время выполнения: {elapsed_time:.2f} секунд")
