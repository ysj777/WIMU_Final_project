import requests
from bs4 import BeautifulSoup

def crawl(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'html.parser')

        links = []
        count = 0
        for link in soup.find_all('a', 
                                  attrs={'data-gtm-service': 'forum', 'data-gtm-area': '熱門看板', 'data-gtm-type':'熱門看板'}):
            href = link['href']
            title = link.get_text(strip=True)
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = url + href
            if 'bsn' in href:
                links.append((title, href))
                count += 1
            if count >= 10:
                break
        
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

def crawl_additional_data(links):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    additional_data = []

    for title, link in links:
        try:
            response = requests.get(link, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract components with class "FM-abox2A"
            components = []
            for div in soup.find_all('div', class_='FM-abox2A'):
                component = {}
                a_tags = div.find_all('a', attrs={'data-gtm': '熱門推薦', 'data-gtm-click': '點擊文章', 'data-gtm-area': '熱門推薦', 'data-gtm-page': 'A頁', 'data-gtm-service': 'forum'})
                for a_tag in a_tags:
                    href = a_tag['href']
                    text = a_tag.get_text(strip=True)
                    img_src = a_tag.find('img')['src'] if a_tag.find('img') else None
                    if href.startswith('//'):
                        href = 'https:' + href
                    component['href'] = href
                    component['text'] = text
                    if img_src:
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        component['img_src'] = img_src
                        paragraph = div.find('p')
                        component['paragraph'] = paragraph.get_text(strip=True) if paragraph else None
                        components.append(component)
            
            additional_data.append((title, link, components))
        except requests.exceptions.RequestException as e:
            print(f"Error: {e} - for URL: {link}")
    
    return additional_data

def merge_results(first_crawl_results, additional_data_results):
    merged_results = []
    for (title, link), (_, _, components) in zip(first_crawl_results, additional_data_results):
        merged_results.append((title, link, components))
    return merged_results

def save_to_markdown(merged_results, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Default Topics\n\n")
        for title, link, components in merged_results:
            f.write(f"## {title}\n")
            f.write(f"- **Forum Link**: [Link]({link})\n")
            for component in components:
                f.write(f"  - **Post Subject**: {component.get('text', 'No text')}\n")
                f.write(f"  - **Link**: [Link]({component.get('href', 'No link')})\n")
                if component.get('img_src'):
                    f.write(f"  - **Image Link**: ![Image]({component.get('img_src')})\n")
                f.write(f"  - **Paragraph**: {component.get('paragraph', 'No paragraph')}\n\n")

url = "https://www.gamer.com.tw/"
first_crawl_results = crawl(url)
additional_data_results = crawl_additional_data(first_crawl_results)

merged_results = merge_results(first_crawl_results, additional_data_results)

filename = 'crawl_results.md'
save_to_markdown(merged_results, filename)
print(f"Results saved to {filename}")
