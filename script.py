import json
import time
from uuid import uuid4

import aiohttp
from bs4 import BeautifulSoup
from fire import Fire


class AkwamOld(object):
    DOMAIN = 'akwam'

    async def __validate(self,url:str)-> bool:
        if self.DOMAIN not in url:
            return False
        return True

    async def __soup(self,data:str,parser='html.parser'):
        soup = BeautifulSoup(data,parser)
        return soup

    async def __get_epis(self,page_soup:BeautifulSoup):
        epis = page_soup.find_all('div',class_='direct_link_box')
        return epis

    async def __parse_each_epi(self,soup:BeautifulSoup):
        # we will get one
        link = soup.find('a',class_="download_btn")
        return link.get('href')  # type: ignore

    async def __get_id_links(self,url:str):
        '''this will get indirect download links'''
        if not await self.__validate(url):
            raise Exception('This is not valid akwam url')
        async with aiohttp.ClientSession() as session:
            response =await session.get(url)
            data = await response.text('utf-8')
        soup = await self.__soup(data)
        items_mcp =await self.__get_epis(soup)
        links = [await self.__parse_each_epi(mcp) for mcp in items_mcp ]
        return links
    
    async def __get_direct_link(self,ind_link) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": ind_link}
            response =await session.post(ind_link,headers=headers)
        _data = await response.text('utf-8')
        _link:dict = json.loads(_data).get('direct_link')
        return str(_link).strip()
    
    async def get(self,url:str,tojson=False):
        id_links = await self.__get_id_links(url)
        d_links = [await self.__get_direct_link(l) for l in id_links]  # type: ignore
        if tojson:
            f_name = uuid4()
            with open(f'{f_name}.json','w') as file:
                json.dump(d_links,file)
                print(f'[*] saved to {f_name}')
        return d_links


if __name__ == '__main__':
    t1 = time.time()
    Fire(AkwamOld)
    total:float = time.time() - t1
    print(f'[*] Done in: {total} seconds' )
