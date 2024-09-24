from typing import Callable, Tuple
import math
import random
from datetime import datetime
from utils import make_random_key, alter_key, get_modifications_map, select_modifications, update_modifications_probabilities
from playfair_cipher import decrypt, make_complete_key


# preso da https://www.oranlooney.com/post/playfair/
# temperature 10-20 in http://practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-playfair/

def simulated_annealing(
        cipher_text: str,
        score_fn: Callable,
        starting_key: str = "",
        attempts: int = 1024, 
        initial_temperature: float = 30,
        min_temperature: float=1,
        desired_acceptance: float=0.3,
        #cooling_rate: float = 0.01, 
        # cooling_rate: float = 0.003, 
        restart_patience: int = 256, 
        verbose: bool=True) -> Tuple[str, float, float]:
    if not starting_key:
        current_key = make_random_key()
    else:
        current_key = make_complete_key(starting_key)
    current_score = score_fn(decrypt(cipher_text, current_key))

    best_key = current_key
    best_score = current_score
    time_since_best = 0
    accepted = 0
    K = 50
    modifications = get_modifications_map()
    temperature = initial_temperature

    try:
        for iteration in range(attempts):
            candidate_key = alter_key(current_key, select_modifications(modifications))
            plain_text = decrypt(cipher_text, candidate_key)
            score = score_fn(plain_text)

            delta = score - current_score
            delta_ratio = delta / temperature
            if abs(delta_ratio) > 100:
                delta_ratio = math.copysign(100, delta)
            acceptance_rate = math.exp(delta_ratio)
            if random.random() < acceptance_rate:
                current_score = score
                current_key = candidate_key

                if score > best_score:
                    time_since_best = 0
                    best_score = score
                    best_key = current_key
                    if verbose:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(iteration, timestamp, best_key, best_score, temperature, plain_text[:50])
                else:
                    time_since_best += 1
                    if time_since_best > restart_patience:
                        time_since_best = 0
                        score = best_score
                        current_key = best_key
                accepted += 1

            # adaptive temperature
            if iteration % K == 0:
                acceptance_rate = accepted / K
                if temperature == min_temperature:
                    temperature = initial_temperature
                else:
                    if acceptance_rate > desired_acceptance:
                        temperature *= 0.95 # raffredda più velocemente
                    else:
                        temperature *= 0.99 # raffredda meno velocemente
                accepted = 0
                temperature = max(temperature, min_temperature)
            modifications = update_modifications_probabilities(modifications, temperature, initial_temperature)
            # print(f'temperature {temperature}'.upper())
            # print(f'acceptance_rate {acceptance_rate}'.upper())
            #temperature *= 1 - cooling_rate
    except KeyboardInterrupt:
        if verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(timestamp, best_key, best_score, temperature, "Ended early due to KeyboardInterrupt")

    return best_key, best_score, temperature

