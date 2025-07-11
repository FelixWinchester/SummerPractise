import random
import string

def generate_hash():
    return ''.join(random.choices('abcdef' + string.digits, k=32))

with open("hashes_6.txt", "w") as f:
    for _ in range(1000000000):
        f.write(generate_hash() + '\n')
