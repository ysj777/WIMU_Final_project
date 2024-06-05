import os
import re
import asyncio
import aiohttp
import aiofiles

jina_reader_key = os.getenv('JINA_READER_KEY')
jina_headers = {"X-With-Generated-Alt": "true"}
if jina_reader_key:
    jina_headers['Authorization'] = f'Bearer {jina_reader_key}'

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

async def get_jina(page_url, session):
    async with session.get(f'https://r.jina.ai/{page_url}', headers=jina_headers) as response:
        text = await response.text()
        return get_main_article(text)

def get_main_article(jina_md):
    return jina_md.split('回覆')[0]

md_image_pattern = re.compile(r'!\[Image[^\]]*\]\([^)]*\)')
url_from_md_pattern = re.compile(r'\(.*\)')
allow_image_host = ['truth.bahamut.com.tw', 'i.imgur.com']

def clean_images(text) -> list:
    image_list = re.findall(md_image_pattern, text)
    urls = []
    for image in image_list:
        for host in allow_image_host:
            if host in image:
                urls.append(re.search(url_from_md_pattern, image)[0][1:-1])
                break
        else:
            text = text.replace(image, '')
    return text, urls

async def save_crawler_data(text_data, task_name):
    os.makedirs(task_name, exist_ok=True)
    async with aiofiles.open(os.path.join(task_name, '0.md'), 'w', encoding='utf-8') as f:
        await f.write(text_data)

async def save_crawler_images(image_urls, task_name):
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(image_urls):
            async with session.get(url, headers={'User-Agent': ua}) as response:
                if response.ok:
                    content = await response.read()
                    async with aiofiles.open(os.path.join(task_name, f'{i}.jpg'), 'wb') as f:
                        await f.write(content)
                else:
                    print(f'Error: {url}: {response.status}')

async def crawler_pipeline(page_url, task_name):
    async with aiohttp.ClientSession() as session:
        jina_page = await get_jina(page_url, session)
        jina_page, image_urls = clean_images(jina_page)
        await save_crawler_data(jina_page, task_name)
        await save_crawler_images(image_urls, task_name)

if __name__ == '__main__':
    page_url = 'https://forum.gamer.com.tw/C.php?bsn=74934&snA=391'
    asyncio.run(crawler_pipeline(page_url, 'result/74934_391'))