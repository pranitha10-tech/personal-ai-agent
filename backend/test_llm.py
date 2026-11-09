
import asyncio
from services.llm_service import get_llm

async def main():
    llm = get_llm()

    response = await llm.ainvoke(
        "Hello! Introduce yourself in two sentences."
    )

    print(response.content)

asyncio.run(main())
