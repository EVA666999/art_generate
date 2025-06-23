#!/usr/bin/env python3
"""
Скрипт для автоматической установки llama-cpp-python с поддержкой CUDA или CPU.
Автоматически определяет доступность CUDA и устанавливает соответствующую версию.
"""

import subprocess
import sys
import os
from typing import Optional, Tuple


def check_cuda_availability() -> Tuple[bool, Optional[str]]:
    """
    Проверяет доступность CUDA и возвращает версию.
    
    Returns:
        Tuple[bool, Optional[str]]: (доступна ли CUDA, версия CUDA)
    """
    try:
        # Проверяем наличие nvidia-smi
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Извлекаем версию CUDA из вывода nvidia-smi
            output = result.stdout
            if 'CUDA Version:' in output:
                for line in output.split('\n'):
                    if 'CUDA Version:' in line:
                        cuda_version = line.split('CUDA Version:')[1].strip()
                        return True, cuda_version
            return True, "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    return False, None


def check_torch_cuda() -> bool:
    """
    Проверяет, поддерживает ли установленный PyTorch CUDA.
    
    Returns:
        bool: True если PyTorch поддерживает CUDA
    """
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def install_llama_cpp_cuda(cuda_version: str = "cu121") -> bool:
    """
    Устанавливает llama-cpp-python с поддержкой CUDA.
    
    Args:
        cuda_version: Версия CUDA (по умолчанию cu121)
    
    Returns:
        bool: True если установка прошла успешно
    """
    print(f"Устанавливаю llama-cpp-python с поддержкой CUDA {cuda_version}...")
    
    try:
        # Удаляем существующую установку
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'llama-cpp-python', '-y'], 
                      check=False)
        
        # Устанавливаем версию с CUDA
        cmd = [
            sys.executable, '-m', 'pip', 'install', 'llama-cpp-python',
            '--force-reinstall',
            '--index-url', f'https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/{cuda_version}'
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ llama-cpp-python с CUDA установлен успешно!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке llama-cpp-python с CUDA: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False


def install_llama_cpp_cpu() -> bool:
    """
    Устанавливает llama-cpp-python только для CPU.
    
    Returns:
        bool: True если установка прошла успешно
    """
    print("Устанавливаю llama-cpp-python для CPU...")
    
    try:
        # Удаляем существующую установку
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'llama-cpp-python', '-y'], 
                      check=False)
        
        # Устанавливаем CPU версию
        cmd = [sys.executable, '-m', 'pip', 'install', 'llama-cpp-python', '--force-reinstall']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ llama-cpp-python для CPU установлен успешно!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке llama-cpp-python для CPU: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False


def test_llama_cpp_import() -> bool:
    """
    Тестирует импорт llama_cpp.
    
    Returns:
        bool: True если импорт прошел успешно
    """
    try:
        import llama_cpp
        print(f"✅ llama_cpp импортирован успешно! Версия: {llama_cpp.__version__}")
        
        # Проверяем доступность CUDA в llama_cpp
        if hasattr(llama_cpp, 'Llama'):
            print("✅ Класс Llama доступен")
            return True
        else:
            print("❌ Класс Llama недоступен")
            return False
            
    except ImportError as e:
        print(f"❌ Ошибка импорта llama_cpp: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка при тестировании llama_cpp: {e}")
        return False


def main():
    """Основная функция установки."""
    print("🚀 Автоматическая установка llama-cpp-python")
    print("=" * 50)
    
    # Проверяем доступность CUDA
    cuda_available, cuda_version = check_cuda_availability()
    torch_cuda_available = check_torch_cuda()
    
    print(f"CUDA доступна: {cuda_available}")
    if cuda_available:
        print(f"Версия CUDA: {cuda_version}")
    print(f"PyTorch CUDA: {torch_cuda_available}")
    
    # Определяем версию CUDA для установки
    if cuda_version and cuda_version != "unknown":
        if "12.1" in cuda_version or "12.2" in cuda_version:
            cuda_suffix = "cu121"
        elif "12.0" in cuda_version:
            cuda_suffix = "cu120"
        elif "11.8" in cuda_version:
            cuda_suffix = "cu118"
        else:
            cuda_suffix = "cu121"  # По умолчанию
    else:
        cuda_suffix = "cu121"
    
    print(f"Будет использована версия CUDA: {cuda_suffix}")
    
    # Пытаемся установить версию с CUDA, если доступна
    if cuda_available and torch_cuda_available:
        print("\n🔄 Пытаюсь установить версию с CUDA...")
        if install_llama_cpp_cuda(cuda_suffix):
            if test_llama_cpp_import():
                print("\n🎉 Установка завершена успешно! Используется версия с CUDA.")
                return
            else:
                print("\n⚠️ Установка с CUDA прошла, но импорт не работает. Пробую CPU версию...")
    
    # Fallback на CPU версию
    print("\n🔄 Устанавливаю CPU версию...")
    if install_llama_cpp_cpu():
        if test_llama_cpp_import():
            print("\n🎉 Установка завершена успешно! Используется CPU версия.")
            return
    
    print("\n❌ Установка не удалась. Попробуйте установить вручную:")
    print("Для CUDA: pip install llama-cpp-python --force-reinstall --index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/cu121")
    print("Для CPU: pip install llama-cpp-python")
    sys.exit(1)


if __name__ == "__main__":
    main() 