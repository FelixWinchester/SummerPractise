import mmap
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from tqdm import tqdm

def process_file(file_path, user_hashes, device_hashes, results, pbar=None):
    start_time = time.time()
    found_in_file = defaultdict(list)
    file_size = os.path.getsize(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                with tqdm(total=file_size, unit='B', unit_scale=True, 
                         desc=f"Обработка {os.path.basename(file_path)}", leave=False) as file_pbar:
                    for line in iter(mm.readline, b''):
                        try:
                            line = line.decode('utf-8').strip()
                            if not line:
                                continue
                                
                            if ':' in line:
                                name, hash_val = line.split(':', 1)
                                hash_val = hash_val.strip()
                                
                                if '-GFG$' in name or any(d in name for d in device_hashes):
                                    continue
                                    
                                if hash_val in user_hashes:
                                    found_in_file[hash_val].append(name)
                            
                            file_pbar.update(len(line))
                            if pbar:
                                pbar.update(1)
                                
                        except Exception as e:
                            continue
                            
        for hash_val, names in found_in_file.items():
            results[hash_val].append((file_path, names))
            
        return (file_path, len(found_in_file)), None
    except Exception as e:
        return (file_path, 0), str(e)

def main():
    users_file = "users.txt"
    device_indicators = ["P05-GFG$", "P06-GFG$"]
    
    print("Загрузка пользователей...")
    user_hashes = {}
    with open(users_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in tqdm(lines, desc="Чтение пользователей", unit="пользователей"):
            line = line.strip()
            if ':' in line:
                user, hash_val = line.split(':', 1)
                user_hashes[hash_val.strip()] = user.strip()
    
    print(f"\nЗагружено {len(user_hashes)} пользователей для проверки")
    
    files_to_check = [
        "hash_file_1.txt",
        "hash_file_2.txt",
        "hash_file_3.txt",
        "hash_file_4.txt",
        "hash_file_5.txt",
        
    ]
    
    print("\nПроверка файлов...")
    valid_files = []
    for file_path in tqdm(files_to_check, desc="Проверка файлов"):
        if os.path.exists(file_path):
            valid_files.append(file_path)
        else:
            print(f"\nФайл {file_path} не существует, пропускаем")
    
    if not valid_files:
        print("Нет файлов для обработки!")
        return
    
    total_lines = 0
    print("\nПодсчет строк в файлах...")
    for file_path in tqdm(valid_files, desc="Анализ файлов"):
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines += sum(1 for _ in f)
    
    results = defaultdict(list)
    start_time = time.time()
    
    print("\nНачало обработки файлов...")
    with tqdm(total=total_lines, desc="Общий прогресс", unit="строк") as pbar:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {executor.submit(process_file, file_path, user_hashes, 
                                     device_indicators, results, pbar): file_path 
                     for file_path in valid_files}
            
            for future in as_completed(futures):
                (file_path, matches), error = future.result()
                if error:
                    pbar.write(f"Ошибка в файле {file_path}: {error}")
                elif matches > 0:
                    pbar.write(f"Файл {os.path.basename(file_path)}: найдено {matches} совпадений")
    
    print("\nРезультаты поиска: ")
    found_users = 0
    
    with tqdm(user_hashes.items(), desc="Анализ результатов", unit="пользователей") as users_pbar:
        for hash_val, user in users_pbar:
            if hash_val in results:
                found_users += 1
                print(f"\nПользователь {user} (хеш: {hash_val}) найден в:")
                for file_path, names in results[hash_val]:
                    print(f"  - Файл: {file_path}")
                    print(f"    Соответствующие имена: {', '.join(names)}")
    
    print(f"\nИтоги:")
    print(f"Обработано файлов: {len(valid_files)}")
    print(f"Проверено пользователей: {len(user_hashes)}")
    print(f"Найдено пользователей с совпадениями: {found_users}")
    print(f"Общее время выполнения: {time.time() - start_time:.2f} секунд")

if __name__ == "__main__":
    main()
