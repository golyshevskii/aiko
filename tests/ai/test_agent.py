import asyncio
from uuid import UUID

from core.ai.agent import POOL, AgentDependencies


async def test_aiko():
    AIKO = await POOL.get_instance()
    try:
        print(
            await AIKO.call(
                "What is love?",
                AgentDependencies(
                    user_id="QWERTY123",
                    username="frank123",
                    conversation_id=UUID(int=1),
                ),
            )
        )
    finally:
        await POOL.return_instance(AIKO)


if __name__ == "__main__":
    asyncio.run(test_aiko())
