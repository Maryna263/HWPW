import time
from multiprocessing import Pool, cpu_count

def factorize_number(n):
    """Шукає всі дільники числа n."""
    factors = []
    for i in range(1, n + 1):
        if n % i == 0:
            factors.append(i)
    return factors

def factorize_sync(numbers):
    return [factorize_number(num) for num in numbers]

def factorize_parallel(numbers):
    with Pool(processes=cpu_count()) as pool:
        return pool.map(factorize_number, numbers)

if __name__ == "__main__":
    # Список вхідних чисел
    numbers = [128, 255, 99999, 10651060]
    
    print(f"Вхідні числа: {numbers}")
    print(f"Кількість ядер: {cpu_count()}")
    print("-" * 30)

    # Синхронний запуск
    start = time.time()
    results = factorize_sync(numbers)
    end = time.time()

    # Виведення результатів
    for num, factors in zip(numbers, results):
        print(f"Число {num} має дільники: {factors}")

    print("-" * 30)
    print(f"Час виконання (синхронно): {end - start:.4f} сек")

    # Паралельний запуск (для порівняння часу)
    start_p = time.time()
    factorize_parallel(numbers)
    end_p = time.time()
    print(f"Час виконання (паралельно): {end_p - start_p:.4f} сек")