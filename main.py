"""
    this script is used to download memes on basis of search result.
"""

import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time
import os
import shutil
import sys

FOLDER = "memes"

if os.path.exists(FOLDER):
    shutil.rmtree(FOLDER)
os.mkdir(FOLDER)


def get_links(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    meme_list = soup.select('div.mt-box')

    links = []
    for meme in meme_list:
        text = meme.select_one("h3").text.strip()
        link = BASE_URL + meme.select_one("h3 a").attrs['href']

        print(f"{text}     {link}")
        links.append(link)
    return links


def get_search_url(search):
    search = '+'.join(search.split(" "))
    url = BASE_URL + "/memesearch?q=" + search
    return url


async def download(url, session, index):
    page = await session.get(url)
    content = await page.text()
    soup = BeautifulSoup(content, "html.parser")

    try:
        img = soup.select_one("img.base-img")
        if not img:
            img = soup.select_one('a.meme-link img')
        image_link = img.attrs['src']
    except AttributeError:
        print("not a valid link.skipping....")
        return

    image_link = "https://" + image_link[2:]

    async with session.get(image_link) as s:
        data = await s.read()
        with open(f"{FOLDER}/image{index}.jpg", "wb") as f:
            f.write(data)

    print(f"downloading image {index}......")


async def start_process(links):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, url in enumerate(links):
            tasks.append(asyncio.create_task(download(url, session, i)))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    BASE_URL = "https://imgflip.com"
    search_meme = input("enter meme text : ")

    search_url = get_search_url(search_meme)
    start = time.time()
    print("fetching the links....\n")
    meme_links = get_links(search_url)
    if not meme_links:
        print("sorry could not find the meme you are looking for, try searching something else.")
        sys.exit()

    print(f"total links fetched : {len(meme_links)}\ntime took : {time.time() - start}\n")

    start = time.time()
    print("download started.......\n")
    asyncio.run(start_process(meme_links))
    print("\ndownload complete\ntime took : ", time.time() - start)
