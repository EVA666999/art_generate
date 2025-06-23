from llama_cpp import Llama

llm = Llama(
    model_path="D:/lm_models/DavidAU/L3.2-8X4B-MOE-V2-Dark-Champion-Inst-21B-uncen-ablit-D_AU-Q6_k.gguf",
    n_ctx=2048,
    n_gpu_layers=100,
    verbose=True
)

response = llm("Привет, как дела?", max_tokens=50)
print(response["choices"][0]["text"])

