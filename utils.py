import unicodedata
import os
from typing import Dict, Callable
from math import log10
import random
from collections import OrderedDict
# corpora da sito http://www.immensola.it/index.php

N_GRAM = 4


def swap_letters(key: str) -> str:
    idx1, idx2 = random.sample(range(len(key)), 2)
    key_list = list(key)
    key_list[idx1], key_list[idx2] = key_list[idx2], key_list[idx1]
    return "".join(key_list)


def swap_rows(key: str) -> str:
    key_matrix = [list(key[i:i+5]) for i in range(0, 25, 5)]
    row1, row2 = random.sample(range(5), 2)
    key_matrix[row1], key_matrix[row2] = key_matrix[row2], key_matrix[row1]
    return ''.join([''.join(row) for row in key_matrix])


def swap_cols(key: str) -> str:
    key_matrix = [list(key[i:i+5]) for i in range(0, 25, 5)]
    col1, col2 = random.sample(range(5), 2)
    for row in key_matrix:
        row[col1], row[col2] = row[col2], row[col1]
    return ''.join([''.join(row) for row in key_matrix])


def shuffle_rows(key: str) -> str:
    key_matrix = [list(key[i:i+5]) for i in range(0, 25, 5)]
    random.shuffle(key_matrix)
    return ''.join([''.join(row) for row in key_matrix])


def shuffle_cols(key: str) -> str:
    key_matrix = [list(key[i:i+5]) for i in range(0, 25, 5)]
    transposed_matrix = [list(col) for col in zip(*key_matrix)]
    random.shuffle(transposed_matrix)
    shuffled_key_matrix = [list(row) for row in zip(*transposed_matrix)]
    return ''.join([''.join(row) for row in shuffled_key_matrix])


def get_modifications_map() -> Dict:
    # probability iniziali
    return OrderedDict({'swap_letters': {'probability': 0.05, 'function': swap_letters},
            'swap_rows': {'probability': 0.125, 'function': swap_rows},
            'swap_cols': {'probability': 0.125, 'function': swap_cols},
            'shuffle_rows': {'probability': 0.35, 'function': shuffle_rows},
            'shuffle_cols': {'probability': 0.35, 'function': shuffle_cols},
            })


def update_modifications_probabilities(mods: Dict, temperature: float, max_temperature: float) -> Dict:
    temp_ratio = temperature / max_temperature
    mods['swap_letters']['probability'] = 0.5 if 0 <= temp_ratio <= 0.5 else 0.05 + 0.9 * (temp_ratio - 0.5)
    mods['swap_rows']['probability'] = 0.35 - 0.45 * abs(temp_ratio - 0.5)
    mods['swap_cols']['probability'] = 0.35 - 0.45 * abs(temp_ratio - 0.5)
    mods['shuffle_rows']['probability'] = 0.35 - 0.125 * temp_ratio
    mods['shuffle_cols']['probability'] = 0.35 - (0.35 - 0.125) * temp_ratio
    return mods


def make_random_key() -> str:
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    return "".join(random.sample(alphabet, 25))


def select_modifications(mods: Dict) -> Callable:
    probs = [mods[mod]['probability'] for mod in mods]
    total = sum(probs)
    probs = [p / total for p in probs]
    selected_mod = random.choices(list(mods.keys()), weights=probs, k=1)[0]
    return mods[selected_mod]['function']


def alter_key(key: str, modification: Callable) -> str:
    assert len(key) == 25
    return modification(key)


def prepare_data(text: str) -> str:
    data_only_letters = ''.join(filter(str.isalpha, text)).lower()
    return remove_accents(data_only_letters)



def remove_accents(text: str) -> str:
    text_norm = unicodedata.normalize('NFD', text)
    return ''.join([c for c in text_norm if unicodedata.category(c) != 'Mn'])


def get_relative_freqs(abs_freqs: Dict) -> Dict:
    total_count = sum(abs_freqs.values())
    return {ngram: abs_freq / total_count for ngram, abs_freq in abs_freqs.items()}


def get_ngrams_relative_frequency(dir_path: str, n_gram: int = N_GRAM) -> Dict:
    corpora = os.listdir(dir_path)
    ngrams = {}
    for corpus in corpora:

        with open(os.path.join(dir_path, corpus), 'r') as file:
            data = file.read()

        processed_data = prepare_data(data)
        tot_ngrams = len(processed_data) - n_gram + 1
        for counter in range(tot_ngrams):
            ngram = processed_data[counter:counter+n_gram].upper()
            if ngram in ngrams:
                ngrams[ngram] += 1
            else:
                ngrams[ngram] = 1
    return get_relative_freqs(ngrams)


def fitness_score(text: str, ngrams_relative_freqs: Dict, n_gram: int = N_GRAM) -> float:
    log_prob = 0
    floor_prob = log10(pow(10, -10))
    counter = 0
    tot_ngrams = len(text) - n_gram + 1
    for counter in range(tot_ngrams):
        ngram = text[counter:counter+n_gram].upper()
        if ngram in ngrams_relative_freqs:
            log_prob += log10(ngrams_relative_freqs[ngram])
        else:
            log_prob += floor_prob
    return log_prob
    

def write_file(filepath: str, key: str, score: float, plaintext: str):

    with open(filepath, 'w') as file:
        file.write(f"Migliore chiave trovata: {key}\n")
        file.write(f"Fitness: {score}\n")
        file.write(f"Testo decodificato: {plaintext}\n")


if __name__ == "__main__":
    ngrams_relative_freqs = get_ngrams_relative_frequency('./corpora')
    italian_text = "Ciao mamma, guarda come mi diverto!"
    english_text = "Hi mum, look how much fun I'm having!"
    fitness_right = fitness_score(italian_text, ngrams_relative_freqs)
    fitness_wrong = fitness_score(english_text, ngrams_relative_freqs)
    print(f"Fitness italian text: {fitness_right}")
    print(f"Fitness english text: {fitness_wrong}")
