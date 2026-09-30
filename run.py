from aiogram import Router
from bot import main, dp
import asyncio

main_router = Router()
dp.include_router(main_router)

if __name__ == "__main__":
  asyncio.run(main())