"""
Утилиты для работы с CPU и оптимизации производительности
"""
import psutil
import os
from typing import Tuple


def get_cpu_info() -> Tuple[int, int, int]:
    """
    Получает информацию о CPU:
    - physical_cores: количество физических ядер
    - logical_cores: количество логических ядер (с гипертредингом)
    - optimal_threads: оптимальное количество потоков для llama-cpp
    
    Returns:
        Tuple[int, int, int]: (physical_cores, logical_cores, optimal_threads)
    """
    # Получаем количество физических ядер
    physical_cores = psutil.cpu_count(logical=False)
    
    # Получаем количество логических ядер
    logical_cores = psutil.cpu_count(logical=True)
    
    # Оптимальное количество потоков = количество физических ядер
    # Это предотвращает блокировку GPU части работы
    optimal_threads = physical_cores
    
    return physical_cores, logical_cores, optimal_threads


def get_optimal_batch_size() -> int:
    """
    Определяет оптимальный размер батча на основе доступной памяти.
    
    Returns:
        int: оптимальный размер батча
    """
    # Получаем доступную оперативную память в ГБ
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    # Определяем оптимальный размер батча на основе памяти
    if memory_gb >= 32:
        return 512  # Большая память - большой батч
    elif memory_gb >= 16:
        return 256  # Средняя память - средний батч
    elif memory_gb >= 8:
        return 128  # Малая память - малый батч
    else:
        return 64   # Очень малая память - минимальный батч


def print_cpu_optimization_info():
    """Выводит информацию об оптимизации CPU для отладки."""
    physical_cores, logical_cores, optimal_threads = get_cpu_info()
    optimal_batch = get_optimal_batch_size()
    
    print("🔧 CPU ОПТИМИЗАЦИЯ:")
    print(f"  Физические ядра: {physical_cores}")
    print(f"  Логические ядра: {logical_cores}")
    print(f"  Оптимальные потоки: {optimal_threads}")
    print(f"  Оптимальный батч: {optimal_batch}")
    print(f"  Соотношение ядер: {logical_cores/physical_cores:.1f}:1")
    
    if logical_cores > physical_cores:
        print("  ⚠️  Обнаружен гипертрединг - используем только физические ядра!")
    
    return optimal_threads, optimal_batch 