import subprocess
import os

def test_moe_model():
    model_path = "/mnt/d/lm_models/DavidAU/L3.2-8X4B-MOE-V2-Dark-Champion-Inst-21B-uncen-ablit-D_AU-Q6_k.gguf"
    llama_path = "./llama-b1337-bin-linux-x64/main"
    
    if not os.path.exists(llama_path):
        print("llama.cpp не найден. Скачайте готовую сборку.")
        return
    
    cmd = [
        llama_path,
        "-m", model_path,
        "--gpu-layers", "50",
        "--ctx-size", "2048",
        "--temp", "0.7",
        "-n", "50",
        "-p", "Привет, как дела?"
    ]
    
    try:
        print("Запускаем llama.cpp с MOE моделью...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Успех!")
            print("Ответ:", result.stdout.strip())
        else:
            print("❌ Ошибка:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("Таймаут выполнения")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_moe_model() 