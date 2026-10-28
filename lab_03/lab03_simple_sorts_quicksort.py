#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией.
Запуск: python lab03-simple-sorts-quicksort-completed.py --variant 39
"""
from __future__ import annotations
import argparse
import random
import statistics
import sys
import time
import traceback
from pathlib import Path


def _less(x, y):
    """Сравнение ключей: для пар (ключ, метка) сравниваем только ключ."""
    if isinstance(x, tuple) and isinstance(y, tuple):
        return x[0] < y[0]
    return x < y


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Пузырёк: лучший случай O(n), средний и худший O(n²). Возвращает копию, сравнения, обмены."""
    arr = list(a)
    comparisons = swaps = 0
    n = len(arr)
    for end in range(n - 1, 0, -1):
        changed = False
        for i in range(end):
            comparisons += 1
            if _less(arr[i + 1], arr[i]):
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swaps += 1
                changed = True
        if not changed:
            break
    return arr, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Вставки: лучший случай O(n), средний и худший O(n²); перемещения — сдвиги и финальные записи."""
    arr = list(a)
    comparisons = moves = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if _less(key, arr[j]):
                arr[j + 1] = arr[j]
                moves += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
        moves += 1
    return arr, comparisons, moves


def selection_sort(a: list) -> tuple[list, int, int]:
    """Выбор: Θ(n²) сравнений при любом порядке; обмены — только если минимум не на месте."""
    arr = list(a)
    comparisons = swaps = 0
    n = len(arr)
    for i in range(n - 1):
        min_i = i
        for j in range(i + 1, n):
            comparisons += 1
            if _less(arr[j], arr[min_i]):
                min_i = j
        if min_i != i:
            arr[i], arr[min_i] = arr[min_i], arr[i]
            swaps += 1
    return arr, comparisons, swaps


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """Рандомизированный QuickSort: среднее O(n log n), худшее O(n²); вход не изменяется."""
    if rng is None:
        rng = random.Random()
    arr = list(a)

    def partition3(lo: int, hi: int) -> tuple[int, int]:
        pivot = arr[rng.randrange(lo, hi + 1)]
        lt, i, gt = lo, lo, hi
        # Dutch-national-flag partition: < pivot | == pivot | > pivot.
        # Равные элементы обрабатываются вместе, избегая деградации на одинаковых ключах.
        while i <= gt:
            if _less(arr[i], pivot):
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif _less(pivot, arr[i]):
                arr[i], arr[gt] = arr[gt], arr[i]
                gt -= 1
            else:
                i += 1
        return lt, gt

    # Явный стек исключает переполнение стека Python на больших массивах.
    stack = [(0, len(arr) - 1)] if len(arr) > 1 else []
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        lt, gt = partition3(lo, hi)
        left, right = (lo, lt - 1), (gt + 1, hi)
        # Сначала обрабатываем меньший диапазон, больший оставляем в стеке.
        if left[1] - left[0] < right[1] - right[0]:
            if right[0] < right[1]:
                stack.append(right)
            if left[0] < left[1]:
                stack.append(left)
        else:
            if left[0] < left[1]:
                stack.append(left)
            if right[0] < right[1]:
                stack.append(right)
    return arr


def stability_demo() -> None:
    """Показывает сохранение/изменение порядка меток при равных ключах."""
    pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (2, "e"), (1, "f")]
    # Стабильность проверяется только по ключу, а не по всей паре.
    algorithms = {
        "bubble_sort": lambda x: bubble_sort(x)[0],
        "insertion_sort": lambda x: insertion_sort(x)[0],
        "selection_sort": lambda x: selection_sort(x)[0],
        "quick_sort": lambda x: quick_sort(x, random.Random(7)),
    }
    print("\nДемонстрация стабильности (ключ, метка):")
    print("  исходный:", pairs)
    for name, fn in algorithms.items():
        result = fn(pairs)
        stable = True
        for key in {p[0] for p in pairs}:
            before = [p[1] for p in pairs if p[0] == key]
            after = [p[1] for p in result if p[0] == key]
            if before != after:
                stable = False
        print(f"  {name:<16} {result} — {'стабильная на этом примере' if stable else 'нестабильная на этом примере'}")


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    rng = random.Random(seed + n)
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {"упорядоченный": sorted(data), "случайный": data, "обратный": sorted(data, reverse=True)}


ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    return all(not _less(a[i + 1], a[i]) for i in range(len(a) - 1))


class SelfCheckError(Exception):
    pass


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)


def check_algorithm(fn) -> None:
    boundary = [[], [7], [5, 5, 5, 5], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: {res}")
        expect(sorted(res) == sorted(a), f"результат не является перестановкой {a}: {res}")
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expect(fn(list(a)) == sorted(a), f"расхождение с sorted() на {a}")


def check_counters() -> None:
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10, f"selection_sort: {comparisons} сравнений вместо 10")
    _, comparisons, swaps = bubble_sort([1, 2, 3])
    expect(comparisons == 2 and swaps == 0, "пузырёк должен завершиться за один проход на отсортированном массиве")
    _, comparisons, _ = insertion_sort([1, 2, 3])
    expect(comparisons == 2, "вставки на упорядоченном массиве должны сделать n-1 сравнений")


def self_check() -> None:
    print("self_check:")
    failed = 0
    for name, fn in ALGORITHMS.items():
        try:
            check_algorithm(fn)
        except Exception as err:
            failed += 1
            print(f"  {name}: ОШИБКА — {err}")
            traceback.print_exc(file=sys.stdout)
        else:
            print(f"  {name}: OK")
    try:
        check_counters()
    except Exception as err:
        failed += 1
        print(f"  счётчики: ОШИБКА — {err}")
    else:
        print("  счётчики: OK")
    if failed:
        raise SystemExit(f"self_check: ошибок — {failed}; бенчмарк отменён")
    print("self_check: OK")


SIZES_QUADRATIC = [500, 750, 1_125, 1_700, 2_500]
SIZES_QUICK = [1_000, 2_000, 4_000, 8_000, 16_000]
REPEATS = 5


def bench(fn, data: list) -> float:
    fn(list(data))  # прогрев, не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int, out_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise SystemExit("Не найден matplotlib. Выполни: pip install matplotlib") from err

    plans = [
        ("bubble_sort", lambda a: bubble_sort(a)[0], SIZES_QUADRATIC),
        ("insertion_sort", lambda a: insertion_sort(a)[0], SIZES_QUADRATIC),
        ("selection_sort", lambda a: selection_sort(a)[0], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    records = {}
    for name, fn, sizes in plans:
        print(f"\n{name} — медиана времени, секунд:")
        records[name] = {"упорядоченный": [], "случайный": [], "обратный": []}
        for n in sizes:
            inputs = make_inputs(n, seed)
            for cls, data in inputs.items():
                elapsed = bench(fn, data)
                records[name][cls].append((n, elapsed))
                print(f"  n={n:>7}  вход={cls:<13} t={elapsed:.6f} с")

    # Log-log график для каждого алгоритма и класса входа.
    for name, _, _ in plans:
        fig, ax = plt.subplots()
        for cls, points in records[name].items():
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            ax.loglog(xs, ys, marker="o", label=cls)
        ax.set_title(f"{name}: время от размера входа")
        ax.set_xlabel("Размер n (log)")
        ax.set_ylabel("Медианное время, с (log)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        path = out_dir / f"lab03_{name}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"График сохранён: {path}")

    # Таблица счётчиков на n=500 для трёх классов.
    print("\nСчётчики сравнений и обменов/перемещений (n=500):")
    for cls, data in make_inputs(500, seed).items():
        print(f"  вход: {cls}")
        for name, fn in [("bubble_sort", bubble_sort), ("insertion_sort", insertion_sort), ("selection_sort", selection_sort)]:
            _, comparisons, moves = fn(data)
            print(f"    {name:<16} сравнения={comparisons:>8}  обмены/перемещения={moves:>8}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", default=None, help="каталог для графиков (по умолчанию рядом со скриптом)")
    args = ap.parse_args()
    seed = 30 + args.variant
    out_dir = Path(args.out).resolve() if args.out else Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Вариант {args.variant}; seed={seed}")
    self_check()
    stability_demo()
    run_benchmarks(seed, out_dir)


if __name__ == "__main__":
    main()
