from typing import List


def make_complete_key(key: str) -> str:
    key = key.upper().replace("J", "I")
    complete_key = []
    used_letters = set()
    for char in key:
        if char not in used_letters and char.isalpha():
            complete_key.append(char)
            used_letters.add(char)
    for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in used_letters:
            complete_key.append(char)
            used_letters.add(char)
    return "".join(complete_key)


def generate_grid(key: str):
    grid = list(key)
    return [grid[i:i + 5] for i in range(0, 25, 5)]


# Funzione per trovare la posizione di una lettera nella griglia
def find_position(letter: str, grid: List):
    for i, row in enumerate(grid):
        if letter in row:
            return i, row.index(letter)
    return None


# Funzione per decifrare un digramma
def decrypt_digram(digram: List, grid: List):
    row1, col1 = find_position(digram[0], grid)
    row2, col2 = find_position(digram[1], grid)

    # Stessa riga
    if row1 == row2:
        return grid[row1][(col1 - 1) % 5] + grid[row2][(col2 - 1) % 5]
    # Stessa colonna
    elif col1 == col2:
        return grid[(row1 - 1) % 5][col1] + grid[(row2 - 1) % 5][col2]
    # Rettangolo
    else:
        return grid[row1][col2] + grid[row2][col1]


# Funzione per decifrare l'intero messaggio
def decrypt(ciphertext, key):
    grid = generate_grid(key)
    plaintext = ""

    for i in range(0, len(ciphertext), 2):
        plaintext += decrypt_digram(ciphertext[i:i+2], grid)

    return plaintext


if __name__ == "__main__":
    FOUND_KEY = 'CMEABLFGHKUPQSTZVWXYDIRON'
    CIPHERTEXT_PATH = 'ciphertext.txt'
    #key = FOUND_KEY
    key = make_complete_key('IRONDME')
    with  open(CIPHERTEXT_PATH, 'r') as file:
        cipher_text = file.read()
    cipher_text = cipher_text.strip('\n')
    print(decrypt(cipher_text, key))
