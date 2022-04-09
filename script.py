# coding=utf-8
import json
import time
import aiohttp
from bs4 import BeautifulSoup
import sys
import asyncio


async def __validate(url:str)-> bool:
    DOMAIN = 'akwam'
    if DOMAIN not in url:
        return False
    return True

async def __soup(data:str,parser='html.parser'):
    soup = BeautifulSoup(data,parser)
    return soup

async def __get_epis(page_soup:BeautifulSoup):
    epis = page_soup.find_all('div',class_='direct_link_box')
    return epis

async def __parse_each_epi(soup:BeautifulSoup):
    # we will get one
    link = soup.find('a',class_="download_btn")
    return link.get('href')  # type: ignore

async def __get_id_links(url:str,session):
    '''this will get indirect download links'''
    if not await __validate(url):
        raise Exception('This is not valid akwam url')
    
    async with session.get(url) as response:
        data = await response.text('utf-8')
        soup = await __soup(data)
    items_mcp =await __get_epis(soup)
    links = [await __parse_each_epi(mcp) for mcp in items_mcp ]
    return links

async def __get_direct_link(ind_link,session) -> str:
    headers = {"X-Requested-With": "XMLHttpRequest","Referer": ind_link}
    async with  session.post(ind_link,headers=headers) as response:
        _data = await response.text('utf-8')
    _link:dict = json.loads(_data).get('direct_link')
    return str(_link).strip()

async def get(url:str,session):
    id_links = await __get_id_links(url,session)
    # d_links = [await (__get_direct_link(link,session)) for link in id_links]
    tasks = [asyncio.create_task(__get_direct_link(link,session)) for link in id_links]
    _d_links = asyncio.gather(*tasks)
    d_links = await _d_links
    return d_links

async def main():
    url = sys.argv[1]
    t1 = time.time()
    async with aiohttp.ClientSession() as session:
        data = await get(url,session)
    print(data)
    t2 = time.time()
    print('Done in {} seconds'.format(t2-t1))
if __name__ == '__main__':
    asyncio.run(main())
    