import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional


class WebPageParser:
    def __init__(self):
        self.soup = None
    
    def parse(self, html: str) -> dict:
        self.soup = BeautifulSoup(html, 'lxml')
        
        result = {
            'title': self._extract_title(),
            'author': self._extract_author(),
            'publish_date': self._extract_publish_date(),
            'content': self._extract_content(),
            'tags': self._extract_tags()
        }
        
        return result
    
    def _extract_title(self) -> Optional[str]:
        title_tag = self.soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            if ' - ' in title_text:
                return title_text.split(' - ')[0].strip()
            return title_text
        
        og_title = self.soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        h1_tag = self.soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        return None
    
    def _extract_author(self) -> Optional[str]:
        author_meta = self.soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            return author_meta['content'].strip()
        
        author_selectors = [
            {'class': 'author'},
            {'class': 'author-name'},
            {'itemprop': 'author'},
            {'rel': 'author'}
        ]
        
        for selector in author_selectors:
            author_tag = self.soup.find(attrs=selector)
            if author_tag:
                return author_tag.get_text(strip=True)
        
        return None
    
    def _extract_publish_date(self) -> Optional[str]:
        date_meta = self.soup.find('meta', property='article:published_time')
        if date_meta and date_meta.get('content'):
            return date_meta['content'].strip()
        
        date_selectors = [
            {'class': 'publish-date'},
            {'class': 'published'},
            {'class': 'date'},
            {'itemprop': 'datePublished'},
            {'itemprop': 'dateCreated'}
        ]
        
        for selector in date_selectors:
            date_tag = self.soup.find(attrs=selector)
            if date_tag:
                datetime_attr = date_tag.get('datetime')
                if datetime_attr:
                    return datetime_attr.strip()
                return date_tag.get_text(strip=True)
        
        time_tag = self.soup.find('time')
        if time_tag:
            datetime_attr = time_tag.get('datetime')
            if datetime_attr:
                return datetime_attr.strip()
            return time_tag.get_text(strip=True)
        
        return None
    
    def _extract_content(self) -> Optional[str]:
        content_selectors = [
            {'class': 'p-article'},
            {'class': 'article-content'},
            {'class': 'post-content'},
            {'class': 'entry-content'},
            {'class': 's-prose'},
            {'itemprop': 'articleBody'},
            {'role': 'article'}
        ]
        
        for selector in content_selectors:
            content_tag = self.soup.find(attrs=selector)
            if content_tag:
                paragraphs = content_tag.find_all(['p', 'h2', 'h3', 'h4', 'li'])
                if paragraphs:
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text:
                            content_parts.append(text)
                    return '\n\n'.join(content_parts)
        
        article_tag = self.soup.find('article')
        if article_tag:
            paragraphs = article_tag.find_all('p')
            if paragraphs:
                content_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                return '\n\n'.join(content_parts)
        
        main_tag = self.soup.find('main')
        if main_tag:
            paragraphs = main_tag.find_all('p')
            if paragraphs:
                content_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                return '\n\n'.join(content_parts)
        
        return None
    
    def _extract_tags(self) -> list:
        tags = []
        
        tag_selectors = [
            {'class': 'tags'},
            {'class': 'tag'},
            {'class': 'post-tags'},
            {'rel': 'tag'},
            {'itemprop': 'keywords'}
        ]
        
        for selector in tag_selectors:
            tag_container = self.soup.find(attrs=selector)
            if tag_container:
                tag_links = tag_container.find_all('a')
                if tag_links:
                    tags.extend([tag.get_text(strip=True) for tag in tag_links if tag.get_text(strip=True)])
                    break
        
        if not tags:
            keywords_meta = self.soup.find('meta', attrs={'name': 'keywords'})
            if keywords_meta and keywords_meta.get('content'):
                keywords = keywords_meta['content'].strip()
                tags = [k.strip() for k in keywords.split(',') if k.strip()]
        
        if not tags:
            all_tag_links = self.soup.find_all('a', rel='tag')
            if all_tag_links:
                tags = [tag.get_text(strip=True) for tag in all_tag_links if tag.get_text(strip=True)]
        
        return list(set(tags))


def fetch_html_from_url(url: str) -> str:
    try:
        from DrissionPage import ChromiumPage
        page = ChromiumPage()
        page.get(url)
        page.wait.load_start()
        html = page.html
        page.quit()
        return html
    except ImportError:
        print("DrissionPage not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'DrissionPage'])
        from DrissionPage import ChromiumPage
        page = ChromiumPage()
        page.get(url)
        page.wait.load_start()
        html = page.html
        page.quit()
        return html


def main():
    if len(sys.argv) > 1:
        input_source = sys.argv[1]
    else:
        input_source = 'sample.html'
    
    if input_source.startswith('http://') or input_source.startswith('https://'):
        print(f"Fetching HTML from URL: {input_source}")
        html_content = fetch_html_from_url(input_source)
    else:
        file_path = Path(input_source)
        if not file_path.exists():
            print(f"Error: File '{input_source}' not found.")
            sys.exit(1)
        print(f"Reading HTML from file: {input_source}")
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    
    parser = WebPageParser()
    result = parser.parse(html_content)
    
    print("\n" + "="*50)
    print("Parsing Results:")
    print("="*50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    output_file = 'parsed_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()