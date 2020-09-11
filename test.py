import asyncio
import click

output = []


async def fetch(x):
    for i in range(3):
        output.append(i * 10 ** x)
        await asyncio.sleep(1)


async def runner():
    tasks = []
    for i in range(3):
        tasks.append(fetch(i))
    await asyncio.gather(*tasks)
    print(output)


@click.command()
def main():
    asyncio.run(runner())


if __name__ == "__main__":
    main()