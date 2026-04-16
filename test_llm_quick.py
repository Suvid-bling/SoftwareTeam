"""Quick test to verify LLM API connectivity and response."""
import asyncio
import time
from anthropic import AsyncAnthropic

async def test_llm():
    # Same config as config2.yaml
    client = AsyncAnthropic(
        api_key="sk-kimi-7dMdDQgxULGom1dqqEJY8kv2SFqmSg7JrRlHiIwYq3r3rgwOemQ7v1mKchgJWrmX",
        base_url="https://api.kimi.com/coding",
    )
    
    print(f"[{time.strftime('%H:%M:%S')}] Sending request to api.kimi.com with model k2p5...")
    print(f"[{time.strftime('%H:%M:%S')}] Waiting (timeout=30s)...")
    
    try:
        resp = await asyncio.wait_for(
            client.messages.create(
                model="k2p5",
                max_tokens=100,
                messages=[{"role": "user", "content": "Say hello in one sentence."}],
            ),
            timeout=30,
        )
        print(f"[{time.strftime('%H:%M:%S')}] SUCCESS! Response: {resp.content[0].text}")
        print(f"[{time.strftime('%H:%M:%S')}] Usage: input={resp.usage.input_tokens}, output={resp.usage.output_tokens}")
    except asyncio.TimeoutError:
        print(f"[{time.strftime('%H:%M:%S')}] TIMEOUT after 30s - LLM API is hanging!")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ERROR: {type(e).__name__}: {e}")

asyncio.run(test_llm())
