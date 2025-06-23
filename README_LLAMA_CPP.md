# Установка llama-cpp-python

Этот документ содержит инструкции по установке `llama-cpp-python` для работы с GGUF моделями в проекте.

## 🚀 Автоматическая установка (Рекомендуется)

### Для Windows:
```bash
# Активируйте виртуальное окружение
venv\Scripts\activate

# Запустите автоматический скрипт
install_llama_cpp.bat
```

### Для Linux/macOS:
```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите автоматический скрипт
python install_llama_cpp.py
```

## 🔧 Ручная установка

### 1. Установка с поддержкой CUDA

Если у вас есть NVIDIA GPU с CUDA:

```bash
# Удалите существующую установку (если есть)
pip uninstall llama-cpp-python -y

# Установите версию с CUDA 12.1
pip install llama-cpp-python --force-reinstall --index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/cu121

# Или для CUDA 12.0
pip install llama-cpp-python --force-reinstall --index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/cu120

# Или для CUDA 11.8
pip install llama-cpp-python --force-reinstall --index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/cu118
```

### 2. Установка только для CPU

Если у вас нет GPU или хотите использовать только CPU:

```bash
# Удалите существующую установку (если есть)
pip uninstall llama-cpp-python -y

# Установите CPU версию
pip install llama-cpp-python --force-reinstall
```

## 🔍 Проверка установки

После установки проверьте, что все работает:

```python
import llama_cpp
print(f"llama_cpp версия: {llama_cpp.__version__}")

# Проверьте доступность CUDA (если установлена версия с CUDA)
if hasattr(llama_cpp, 'Llama'):
    print("✅ Класс Llama доступен")
else:
    print("❌ Класс Llama недоступен")
```

## 🐛 Решение проблем

### Ошибка: "Could not find module 'llama.dll'"

Эта ошибка возникает, когда нативная библиотека не установлена правильно.

**Решение:**
1. Убедитесь, что вы используете правильную версию для вашей платформы
2. Попробуйте автоматический скрипт: `python install_llama_cpp.py`
3. Для Windows убедитесь, что у вас установлены Visual C++ Redistributables

### Ошибка: "CUDA not available"

**Решение:**
1. Проверьте, что у вас установлен CUDA Toolkit
2. Убедитесь, что PyTorch поддерживает CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
3. Установите версию llama-cpp-python с поддержкой CUDA

### Ошибка: "ImportError: DLL load failed"

**Решение:**
1. Переустановите llama-cpp-python с флагом `--force-reinstall`
2. Убедитесь, что у вас установлены все необходимые системные зависимости
3. Попробуйте CPU версию, если проблемы с CUDA

## 📋 Системные требования

### Windows:
- Python 3.8+
- Visual C++ Redistributables
- CUDA Toolkit (для GPU версии)

### Linux:
- Python 3.8+
- GCC/G++ компилятор
- CUDA Toolkit (для GPU версии)

### macOS:
- Python 3.8+
- Xcode Command Line Tools
- Metal Performance Shaders (для GPU версии)

## 🔗 Полезные ссылки

- [llama-cpp-python GitHub](https://github.com/abetlen/llama-cpp-python)
- [CUDA версии для Windows](https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/)
- [PyTorch CUDA установка](https://pytorch.org/get-started/locally/)

## 📝 Примечания

- Автоматический скрипт определяет доступность CUDA и устанавливает соответствующую версию
- Если CUDA недоступна, автоматически устанавливается CPU версия
- После установки перезапустите сервер: `python app/main.py` 