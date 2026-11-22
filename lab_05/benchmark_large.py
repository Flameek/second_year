"""One reproducible 100000-key sample per isolated process."""
import random
from time import perf_counter
from teacher_check import build

N = 100_000
SEED = 69
rng = random.Random(SEED)
keys = rng.sample(range(10 * N), N)
queries = [rng.randint(0, 10 * N) for _ in range(1000)]
tree = build(keys)

def measure(search):
    # Warm both access paths locally, then time the full identical query set.
    for item in queries[:100]:
        search(item)
    start = perf_counter()
    for item in queries:
        search(item)
    return perf_counter() - start

print(N, tree.height(), measure(tree.search), measure(keys.__contains__))
