import subprocess
import json
import os

class LlamaCppWrapper:
    def __init__(self, model_path, llama_cpp_path="./llama.cpp/build/main"):
        self.model_path = model_path
        self.llama_cpp_path = llama_cpp_path
        
    def generate(self, prompt, max_tokens=50, temperature=0.7, gpu_layers=50):
        """Генерирует ответ используя llama.cpp"""
        cmd = [
            self.llama_cpp_path,
            "-m", self.model_path,
            "--gpu-layers", str(gpu_layers),
            "--ctx-size", "2048",
            "--temp", str(temperature),
            "--repeat-penalty", "1.1",
            "-n", str(max_tokens),
            "-p", prompt
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Ошибка: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Таймаут выполнения"
        except Exception as e:
            return f"Ошибка: {e}"

# Тест
if __name__ == "__main__":
    model_path = "/mnt/d/lm_models/DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF/L3.2-8X3B-MOE-Dark-Champion-Inst-18.4B-uncen-ablit_D_AU-Q4_k_s.gguf"
    
    llm = LlamaCppWrapper(model_path)
    response = llm.generate("Привет, как дела?", max_tokens=50, gpu_layers=50)
    print("Ответ:", response) 