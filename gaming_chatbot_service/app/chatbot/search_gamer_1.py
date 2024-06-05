import requests
from bs4 import BeautifulSoup
import os
import tqdm
import threading
from pathlib import Path
from .get_jina_parse_1 import crawler_pipeline

current_path = os.path.dirname(os.path.abspath(__file__))
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def search(topic_bsn, question, top_k=5):
    response = requests.get(f'https://forum.gamer.com.tw/search.php?bsn={topic_bsn}&q={question}', headers=headers)
    text = response.text

    soup = BeautifulSoup(text, 'html.parser')
    search_results = soup.select('.search-result_article')

    parse_result = []
    for result in search_results[:top_k]:
        title = result.select_one('.search-result_title').text.strip()
        link = result.select_one('.search-result_title a')['href']
        text = result.select_one('.search-result_text').text.strip()
        info = result.select_one('.forum-textinfo').text.strip()
        
        # print('標題:', title)
        # print('連結:', link)
        # print('內文:', text)
        # print('資訊:', info)
        # print('-'*50)
        parse_result.append({
            'title': title,
            'link': link,
            'text': text,
            'info': info
        })

    return parse_result

def search_and_save(topic_bsn, question, top_k=5) -> list:
    search_result = search(topic_bsn, question, top_k)
    if not search_result:
        print('查無結果')
        return()
    os.makedirs(Path.joinpath(Path(current_path), f'result/{topic_bsn}_{question}'), exist_ok=True)

    threads = []
    for i, result in enumerate(search_result):
        result_link = result['link']
        # result_title = result['title']
        # result_title = result_title.replace('/', '_')
        # result_title = result_title.replace('\\', '_')
        # result_title = result_title.replace('?', '_')
        threads.append(threading.Thread(target = crawler_pipeline, args = (result_link, Path.joinpath(Path(current_path), f'result/{topic_bsn}_{question}/{i}'))))
        threads[-1].start()        
        # image_urls = crawler_pipeline(result_link, f'result/{topic_bsn}_{question}/{i}')

    for thread in tqdm.tqdm(threads):
        thread.join()

if __name__ == '__main__':
    topic_bsn = '74934'
    question = '角色'
    search_and_save(topic_bsn, question)