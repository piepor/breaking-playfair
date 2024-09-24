import itertools
import string
from typing import List
from tqdm import tqdm


# Funzione per generare la griglia 5x5 dal testo della chiave
def generate_grid(key: str):
    key = key.upper().replace("J", "I")
    grid = []
    used_letters = set()

    # Aggiungere le lettere della chiave alla griglia
    for char in key:
        if char not in used_letters and char.isalpha():
            grid.append(char)
            used_letters.add(char)

    # Aggiungere le lettere rimanenti dell'alfabeto
    for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in used_letters:
            grid.append(char)
            used_letters.add(char)

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
def decrypt_playfair(ciphertext, key):
    grid = generate_grid(key)
    plaintext = ""

    for i in range(0, len(ciphertext), 2):
        plaintext += decrypt_digram(ciphertext[i:i+2], grid)

    return plaintext


# Funzione per generare possibili chiavi (dizionario o combinazioni di lettere)
def generate_possible_keys():
    # Qui usiamo un insieme ridotto di lettere per esempio, puoi sostituirlo con un dizionario
    #alphabet = "IRONDMEXYZ"
    #alphabet = "EAIONHLR"
    alphabet = "EAIONLRTSCD"
    #first_chunk = "IRON"
    #alphabet = ""
    print("Generating possible keys")
    possible_keys = [''.join(p) for p in itertools.permutations(alphabet)]
    return possible_keys


# Funzione per verificare se il messaggio decifrato ha senso
def is_valid_decryption(plaintext):
    # In questo esempio, usiamo parole comuni per verificare se il testo ha senso
    #common_words = ["ATTACCO", "PROGRAMMA", "ISTANBUL", "CIPRO", "PASSAPORTO"]
    common_words = ["ZERO", "UNO", "DUE", "TRE", "QUATTRO", "CINQUE", "SEI", "SETTE", "OTTO", "NOVE"]
    count_words = 0
    for word in common_words:
        if word in plaintext:
            count_words += 1
    if count_words > 4:
        return True
    return False


# Funzione principale per provare tutte le chiavi possibili
def break_playfair(ciphertext):
    possible_keys = generate_possible_keys()

    for key in tqdm(possible_keys):
        decrypted_message = decrypt_playfair(ciphertext, key)
        if is_valid_decryption(decrypted_message):
            return decrypted_message, key

    return None, None

# Test: inserire qui il messaggio cifrato
#ciphertext = "DSXDRPIAYFQFZTIZMFP" # Esempio di messaggio cifrato
row_1 = "EOORXMSNADOBGEARBSQBOWOESNBMMVONDFQNBQEGCZAEDFMXBR"
row_2 = "PNSPBSQNISTDSNIMEHFRBSAXBRXCQINAGCFMADDNSYSNLHIRCBHEHF"
row_3 = "RNQPBYAXAXSBIRNSSNNOABHCODBMMSTDSNORSMNQNPDANDSPEOBO"
row_4 = "SBMDRTQCFMDTPNIRORSBOIIXROHRHCABOWORXMSNADBYEGBYBMRD"
row_5 = "SPAERDPURIRONPEOINQPBYAHOPSBECZUPUDFDVXCSNSMXOXHSINQNS"
row_6 = "QDADDTEAONBHMDRTQCCZBQEGWCONHXTPBYDAIAACEOOPSBQIAQXA"
row_7 = "DFQEBONCCXEOADOTPNQMDIRNIRQNBRSBSPBSQNRAQDAHFHRNODIST"
row_8 = "DSNHXTPBYDANDADBYOESYSNDTEAONYLMDRTQCNSSNQASYQBWCON"
row_9 = "QNAMRDSPARSYSNTDAONSSNDNWMXMFDINPMDNCHWMBYRPSCSYQN"
row_10 = "AHQIDFCRQCFMHCWMBYOPBQQB"

ciphertext = "".join([row_1, row_2, row_3, row_4, row_5, row_6, row_7, row_8, row_9, row_10])
breakpoint()

# Rompere il cifrario Playfair
decrypted_message, found_key = break_playfair(ciphertext)

if decrypted_message:
    print(f"Messaggio decifrato: {decrypted_message} con chiave: {found_key}")
else:
    print("Nessuna chiave valida trovata.")
