"""Ollama LLM客户端"""
import requests
import json

OLLAMA_BASE = "http://localhost:11434"
MODEL = "qwen2.5"


def chat(messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> str:
    """调用Ollama聊天接口"""
    url = f"{OLLAMA_BASE}/api/chat"
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception as e:
        return f"LLM调用失败: {e}"


def generate(prompt: str, system: str = "", temperature: float = 0.3) -> str:
    """简单生成接口"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat(messages, temperature)
