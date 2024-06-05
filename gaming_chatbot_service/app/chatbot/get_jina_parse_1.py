import requests
import os
import regex as re

jina_reader_key = os.getenv('JINA_READER_KEY')
jina_headers = {
        "X-With-Generated-Alt": "true"
    }
if jina_reader_key:
    jina_headers['Authorization'] = f'Bearer {jina_reader_key}'
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

def get_jina(page_url):
    def get_main_article(jina_md):
        return jina_md.split('回覆')[0]
    
    page_url = 'https://r.jina.ai/' + page_url
    
    response = requests.get(page_url, headers=jina_headers)
    text = get_main_article(response.text)
    # text = response.text
    return text

md_image_pattern = re.compile(r'!\[Image[^\]]*\]\([^\)]*\)')
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

def save_crawler_data(text_data, task_name):
    os.makedirs(task_name, exist_ok=True)
    with open(os.path.join(task_name,'0.md'), 'w', encoding='utf-8') as f:
        f.write(text_data)

def save_crawler_images(image_urls, task_name):
    for i, url in enumerate(image_urls):
        response = requests.get(url, headers={'User-Agent': ua})
        if not response.ok:
            print(f'Error: {url}: {response.status_code}')
            continue
        with open(os.path.join(task_name,f'{i}.jpg'), 'wb') as handler:
            handler.write(response.content)

def crawler_pipeline(page_url, task_name) -> list:
    jina_page = get_jina(page_url)
    jina_page, image_urls = clean_images(jina_page)
    save_crawler_data(jina_page, task_name)
    save_crawler_images(image_urls, task_name)
    return image_urls

if __name__ == '__main__':
    page_url = 'https://forum.gamer.com.tw/C.php?bsn=74934&snA=391'
    crawler_pipeline(page_url, 'result/74934_391')