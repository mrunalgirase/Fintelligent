"""
LLM streaming service for AI Coach.

Uses Groq cloud API when GROQ_API_KEY is set (no local CPU load).
Falls back to local Ollama with a concurrency lock so only one inference
runs at a time — prevents the whole platform from freezing.
"""
import json
import os
import threading
from typing import Generator, Optional

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
GROQ_MODEL = os.environ.get("GROQ_CHAT_MODEL", "llama-3.1-8b-instant")
KEEP_ALIVE = os.environ.get("OLLAMA_KEEP_ALIVE", "5m")

# Serialize local Ollama calls — llama3 is heavy and parallel runs freeze the machine.
_ollama_lock = threading.Semaphore(1)
_OLLAMA_BUSY_MSG = "AI is processing another request. Please wait a moment and try again."


def _sse_content(text: str) -> str:
    return f"data: {json.dumps({'content': text})}\n\n"


def _sse_error(message: str) -> str:
    return f"data: {json.dumps({'error': message})}\n\n"


def _ollama_options(temperature: float, max_tokens: int) -> dict:
    return {
        "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "2048")),
        "num_predict": max_tokens,
        "temperature": temperature,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    }


def stream_llm(
    *,
    system: str,
    user: str,
    temperature: float = 0.7,
    max_tokens: int = 400,
) -> Generator[str, None, None]:
    """Stream an assistant reply as Server-Sent Events."""
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        yield from _stream_groq(system, user, api_key, temperature, max_tokens)
    else:
        yield from _stream_ollama(system, user, temperature, max_tokens)


def _stream_groq(
    system: str,
    user: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> Generator[str, None, None]:
    try:
        import groq

        client = groq.Groq(api_key=api_key)
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield _sse_content(delta.content)
        yield "data: [DONE]\n\n"
    except Exception as exc:
        yield _sse_error(str(exc))


def _stream_ollama(
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
) -> Generator[str, None, None]:
    acquired = _ollama_lock.acquire(timeout=45)
    if not acquired:
        yield _sse_error(_OLLAMA_BUSY_MSG)
        return

    prompt = f"{system.strip()}\n\nUser: {user.strip()}\nAssistant:"
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True,
            "keep_alive": KEEP_ALIVE,
            "options": _ollama_options(temperature, max_tokens),
        }
        with requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=(10, 90),
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("response"):
                    yield _sse_content(data["response"])
                if data.get("done"):
                    yield "data: [DONE]\n\n"
    except requests.exceptions.ConnectionError:
        yield _sse_error(
            "Ollama is not running. Start it with 'ollama serve', "
            "or add GROQ_API_KEY to .env for faster cloud AI."
        )
    except requests.exceptions.Timeout:
        yield _sse_error("AI response timed out. Try a shorter question.")
    except Exception as exc:
        yield _sse_error(str(exc))
    finally:
        _ollama_lock.release()
