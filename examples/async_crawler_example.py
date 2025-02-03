from crawl4ai import *
import asyncio


async def run_crawler():
    url = 'https://pubs.acs.org/doi/10.1021/acsnano.4c00078'
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        print(result.markdown)


if __name__ in "__main__":
    asyncio.run(run_crawler())