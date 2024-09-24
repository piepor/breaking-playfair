from functools import partial
from utils import get_ngrams_relative_frequency, fitness_score, make_random_key, write_file
from cracking import simulated_annealing
from playfair_cipher import decrypt, make_complete_key
import random
import multiprocessing
import shutil


CORPORA_DIR_PATH = './corpora'
CIPHERTEXT_PATH = 'ciphertext.txt'
GLOBAL_PATIENCE = 1000000
RESTART_EPOCH_PATIENCE = 50000

with  open(CIPHERTEXT_PATH, 'r') as file:
    cipher_text = file.read()
cipher_text = cipher_text.strip('\n')

ngrams_relative_freqs = get_ngrams_relative_frequency('./corpora')

score_fn = partial(fitness_score, ngrams_relative_freqs=ngrams_relative_freqs)

best_key, best_score, temperature = simulated_annealing(cipher_text, score_fn, attempts=100000, initial_temperature=100)
print(best_key, best_score)


def process_worker(args):
    # TODO global temperature?
    key, cipher_text, global_best, global_best_key, global_since, global_lock = args
    best_score = 0
    best_key = key
    since = 0
    #temperature = initial_temperature
    attempts_per_epoch = 100000

    while True:
        key, score, temperature = simulated_annealing(
                cipher_text, score_fn, attempts=attempts_per_epoch, starting_key=key)
        if score > best_score:
            best_score = score
            best_key = key
            since = 0
        else:
            since += 1

        with global_lock:
            if best_score > global_best.value:
                global_best.value = best_score
                global_best_key.value = best_key
                global_since.value = 0
                plaint_text = decrypt(cipher_text, best_key)
                write_file('./.solutions_reserved.txt', best_key, best_score, plaint_text)
                shutil.copyfile('./.solutions_reserved.txt', '')
            else:
                global_since.value += 1

        if global_since.value > GLOBAL_PATIENCE:
            break

        if since > RESTART_EPOCH_PATIENCE:
            if random.random() < 0.5:
                key = global_best_key.value
                score = global_best.value
            else:
                key = best_key
                score = best_score
            since = 0

    return best_score, best_key


def parallel_crack(ciphertext):
    pool_size = multiprocessing.cpu_count()
    keys = [make_random_key() for i in range(pool_size)]

    with multiprocessing.Manager() as manager:
        global_best = manager.Value('f', 0.0)
        global_best_key = manager.Value('s', keys[0])
        global_since = manager.Value('i', 0)
        global_lock = manager.Lock()
        args = [(key, ciphertext, global_best, global_best_key, global_since, global_lock) for key in keys]
        with multiprocessing.Pool(pool_size) as worker_pool:
            solutions = worker_pool.map(process_worker, args)
        return global_best_key.value, global_best.value

                
if __name__ == "__main__":
     global_best_key, global_best = parallel_crack(cipher_text)
