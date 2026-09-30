import os
import config
import aiofiles

async def read_links() -> list[str]:
  async with aiofiles.open(os.path.join(config.CACHE_DIRNAME, config.CACHE_FILES["links"])) as file:
    return [line.strip() for line in await file.readlines() if line.strip() != ""]

async def save_links(links: list[str]):
  async with aiofiles.open(os.path.join(config.CACHE_DIRNAME, config.CACHE_FILES["links"]), "w") as file:
    await file.writelines(link + "\n" for link in links)