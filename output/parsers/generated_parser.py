import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


class WebPageParser:
    def __init__(self):
        self.soup = None
        
    def parse(self, html: str) -> dict:
        """解析HTML并提取所有字段"""
        self.soup = BeautifulSoup(html, 'lxml')
        
        result = {
            "page_type": self._extract_page_type(),
            "title": self._extract_title(),
            "author": self._extract_author(),
            "publication_date": self._extract_publication_date(),
            "content": self._extract_content(),
            "section_headings": self._extract_section_headings(),
            "related_articles": self._extract_related_articles(),
            "tags": self._extract_tags(),
            "error_code": self._extract_error_code(),
            "error_message": self._extract_error_message(),
            "error_description": self._extract_error_description(),
            "button_text": self._extract_button_text(),
            "additional_info": self._extract_additional_info()
        }
        
        return result
    
    def _extract_page_type(self) -> Dict[str, Any]:
        """提取页面类型"""
        try:
            og_type = self.soup.find('meta', property='og:type')
            if og_type and og_type.get('content'):
                page_type = og_type['content']
                confidence = 0.98
            else:
                title_tag = self.soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text(strip=True).lower()
                    if 'not found' in title_text or '404' in title_text:
                        page_type = "错误页"
                        confidence = 0.95
                    elif self.soup.find('article'):
                        page_type = "文章页"
                        confidence = 0.90
                    else:
                        page_type = "未知"
                        confidence = 0.50
                else:
                    page_type = "未知"
                    confidence = 0.50
            
            return {
                "type": "string",
                "description": "页面类型",
                "value": page_type,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "页面类型",
                "value": "未知",
                "confidence": 0.5
            }
    
    def _extract_title(self) -> Dict[str, Any]:
        """提取文章标题"""
        try:
            title = None
            confidence = 0.5
            
            h1_tag = self.soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
                confidence = 0.95
            
            if not title:
                og_title = self.soup.find('meta', property='og:title')
                if og_title and og_title.get('content'):
                    title = og_title['content']
                    confidence = 0.90
            
            if not title:
                title_tag = self.soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    confidence = 0.85
            
            if not title:
                title = ""
                confidence = 0.0
            
            return {
                "type": "string",
                "description": "文章标题",
                "value": title,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "文章标题",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_author(self) -> Dict[str, Any]:
        """提取作者姓名"""
        try:
            author = None
            confidence = 0.5
            
            author_meta = self.soup.find('meta', attrs={'name': 'author'})
            if author_meta and author_meta.get('content'):
                author = author_meta['content']
                confidence = 0.95
            
            if not author:
                author_meta = self.soup.find('meta', property='article:author')
                if author_meta and author_meta.get('content'):
                    author = author_meta['content']
                    confidence = 0.90
            
            if not author:
                author_tag = self.soup.find(class_=lambda x: x and 'author' in x.lower())
                if author_tag:
                    author = author_tag.get_text(strip=True)
                    confidence = 0.80
            
            if not author:
                author_tag = self.soup.find('a', rel='author')
                if author_tag:
                    author = author_tag.get_text(strip=True)
                    confidence = 0.85
            
            if not author:
                author = ""
                confidence = 0.0
            
            return {
                "type": "string",
                "description": "作者姓名",
                "value": author,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "作者姓名",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_publication_date(self) -> Dict[str, Any]:
        """提取发布日期"""
        try:
            date = None
            confidence = 0.5
            
            date_meta = self.soup.find('meta', property='article:published_time')
            if date_meta and date_meta.get('content'):
                date = date_meta['content']
                confidence = 0.97
            
            if not date:
                date_meta = self.soup.find('meta', attrs={'name': 'publication_date'})
                if date_meta and date_meta.get('content'):
                    date = date_meta['content']
                    confidence = 0.95
            
            if not date:
                time_tag = self.soup.find('time')
                if time_tag:
                    date = time_tag.get('datetime') or time_tag.get_text(strip=True)
                    confidence = 0.90
            
            if not date:
                date_tag = self.soup.find(class_=lambda x: x and ('date' in x.lower() or 'publish' in x.lower()))
                if date_tag:
                    date = date_tag.get_text(strip=True)
                    confidence = 0.80
            
            if not date:
                date = ""
                confidence = 0.0
            
            return {
                "type": "string",
                "description": "发布日期",
                "value": date,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "发布日期",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_content(self) -> Dict[str, Any]:
        """提取文章正文内容"""
        try:
            content = ""
            confidence = 0.5
            
            article_tag = self.soup.find('article')
            if article_tag:
                paragraphs = article_tag.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    confidence = 0.96
            
            if not content:
                content_div = self.soup.find(class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower()))
                if content_div:
                    paragraphs = content_div.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                        confidence = 0.90
            
            if not content:
                main_tag = self.soup.find('main')
                if main_tag:
                    paragraphs = main_tag.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                        confidence = 0.85
            
            if not content:
                paragraphs = self.soup.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                    confidence = 0.70
            
            if len(content) > 500:
                content = content[:500]
            
            return {
                "type": "string",
                "description": "文章正文内容",
                "value": content,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "文章正文内容",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_section_headings(self) -> Dict[str, Any]:
        """提取文章章节标题列表"""
        try:
            headings = []
            confidence = 0.5
            
            article_tag = self.soup.find('article')
            if article_tag:
                heading_tags = article_tag.find_all(['h2', 'h3', 'h4'])
                if heading_tags:
                    headings = [h.get_text(strip=True) for h in heading_tags if h.get_text(strip=True)]
                    confidence = 0.98
            
            if not headings:
                content_div = self.soup.find(class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower()))
                if content_div:
                    heading_tags = content_div.find_all(['h2', 'h3', 'h4'])
                    if heading_tags:
                        headings = [h.get_text(strip=True) for h in heading_tags if h.get_text(strip=True)]
                        confidence = 0.90
            
            if not headings:
                main_tag = self.soup.find('main')
                if main_tag:
                    heading_tags = main_tag.find_all(['h2', 'h3', 'h4'])
                    if heading_tags:
                        headings = [h.get_text(strip=True) for h in heading_tags if h.get_text(strip=True)]
                        confidence = 0.85
            
            if not headings:
                heading_tags = self.soup.find_all(['h2', 'h3'])
                if heading_tags:
                    headings = [h.get_text(strip=True) for h in heading_tags[:10] if h.get_text(strip=True)]
                    confidence = 0.70
            
            return {
                "type": "array",
                "description": "文章章节标题列表",
                "value": headings,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "array",
                "description": "文章章节标题列表",
                "value": [],
                "confidence": 0.0
            }
    
    def _extract_related_articles(self) -> Dict[str, Any]:
        """提取相关文章列表"""
        try:
            related = []
            confidence = 0.5
            
            related_section = self.soup.find(class_=lambda x: x and 'related' in x.lower())
            if related_section:
                links = related_section.find_all('a')
                if links:
                    related = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
                    confidence = 0.95
            
            if not related:
                aside_tag = self.soup.find('aside')
                if aside_tag:
                    links = aside_tag.find_all('a')
                    if links:
                        related = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
                        confidence = 0.85
            
            if not related:
                sidebar = self.soup.find(class_=lambda x: x and 'sidebar' in x.lower())
                if sidebar:
                    links = sidebar.find_all('a')
                    if links:
                        related = [link.get_text(strip=True) for link in links[:5] if link.get_text(strip=True)]
                        confidence = 0.75
            
            return {
                "type": "array",
                "description": "相关文章列表",
                "value": related,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "array",
                "description": "相关文章列表",
                "value": [],
                "confidence": 0.0
            }
    
    def _extract_tags(self) -> Dict[str, Any]:
        """提取文章标签"""
        try:
            tags = []
            confidence = 0.5
            
            keywords_meta = self.soup.find('meta', attrs={'name': 'keywords'})
            if keywords_meta and keywords_meta.get('content'):
                tags = [tag.strip() for tag in keywords_meta['content'].split(',')]
                confidence = 0.94
            
            if not tags:
                tag_section = self.soup.find(class_=lambda x: x and ('tag' in x.lower() or 'category' in x.lower()))
                if tag_section:
                    tag_links = tag_section.find_all('a')
                    if tag_links:
                        tags = [link.get_text(strip=True) for link in tag_links if link.get_text(strip=True)]
                        confidence = 0.90
            
            if not tags:
                article_tag = self.soup.find('meta', property='article:tag')
                if article_tag and article_tag.get('content'):
                    tags = [article_tag['content']]
                    confidence = 0.85
            
            return {
                "type": "array",
                "description": "文章标签",
                "value": tags,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "array",
                "description": "文章标签",
                "value": [],
                "confidence": 0.0
            }
    
    def _extract_error_code(self) -> Dict[str, Any]:
        """提取错误代码"""
        try:
            error_code = ""
            confidence = 0.0
            
            title_tag = self.soup.find('title')
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                if '404' in title_text:
                    error_code = "404"
                    confidence = 0.99
                elif '403' in title_text:
                    error_code = "403"
                    confidence = 0.99
                elif '500' in title_text:
                    error_code = "500"
                    confidence = 0.99
            
            if not error_code:
                h1_tag = self.soup.find('h1')
                if h1_tag:
                    h1_text = h1_tag.get_text(strip=True)
                    if '404' in h1_text:
                        error_code = "404"
                        confidence = 0.95
                    elif '403' in h1_text:
                        error_code = "403"
                        confidence = 0.95
                    elif '500' in h1_text:
                        error_code = "500"
                        confidence = 0.95
            
            return {
                "type": "string",
                "description": "错误代码",
                "value": error_code,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "错误代码",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_error_message(self) -> Dict[str, Any]:
        """提取错误信息"""
        try:
            error_message = ""
            confidence = 0.0
            
            title_tag = self.soup.find('title')
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                if 'not found' in title_text.lower() or '404' in title_text:
                    error_message = title_text
                    confidence = 0.99
            
            if not error_message:
                h1_tag = self.soup.find('h1')
                if h1_tag:
                    h1_text = h1_tag.get_text(strip=True)
                    if 'not found' in h1_text.lower() or 'error' in h1_text.lower():
                        error_message = h1_text
                        confidence = 0.95
            
            return {
                "type": "string",
                "description": "错误信息",
                "value": error_message,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "错误信息",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_error_description(self) -> Dict[str, Any]:
        """提取错误详细描述"""
        try:
            error_description = ""
            confidence = 0.0
            
            error_div = self.soup.find(class_=lambda x: x and 'error' in x.lower())
            if error_div:
                p_tag = error_div.find('p')
                if p_tag:
                    error_description = p_tag.get_text(strip=True)
                    confidence = 0.98
            
            if not error_description:
                main_tag = self.soup.find('main')
                if main_tag:
                    p_tags = main_tag.find_all('p')
                    if p_tags:
                        for p in p_tags:
                            text = p.get_text(strip=True)
                            if 'sorry' in text.lower() or 'could' in text.lower():
                                error_description = text
                                confidence = 0.90
                                break
            
            return {
                "type": "string",
                "description": "错误详细描述",
                "value": error_description,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "错误详细描述",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_button_text(self) -> Dict[str, Any]:
        """提取按钮文本"""
        try:
            button_text = ""
            confidence = 0.0
            
            buttons = self.soup.find_all('button')
            if buttons:
                for button in buttons:
                    text = button.get_text(strip=True)
                    if text and len(text) < 50:
                        button_text = text
                        confidence = 0.99
                        break
            
            if not button_text:
                links = self.soup.find_all('a', class_=lambda x: x and 'button' in x.lower())
                if links:
                    for link in links:
                        text = link.get_text(strip=True)
                        if text and len(text) < 50:
                            button_text = text
                            confidence = 0.95
                            break
            
            return {
                "type": "string",
                "description": "按钮文本",
                "value": button_text,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "按钮文本",
                "value": "",
                "confidence": 0.0
            }
    
    def _extract_additional_info(self) -> Dict[str, Any]:
        """提取附加信息"""
        try:
            additional_info = ""
            confidence = 0.0
            
            main_tag = self.soup.find('main')
            if main_tag:
                p_tags = main_tag.find_all('p')
                if len(p_tags) > 1:
                    for p in p_tags[1:]:
                        text = p.get_text(strip=True)
                        if text and 'looking for' in text.lower():
                            additional_info = text
                            confidence = 0.97
                            break
            
            if not additional_info:
                all_p = self.soup.find_all('p')
                for p in all_p:
                    text = p.get_text(strip=True)
                    if text and 'looking for' in text.lower():
                        additional_info = text
                        confidence = 0.90
                        break
            
            return {
                "type": "string",
                "description": "附加信息",
                "value": additional_info,
                "confidence": confidence
            }
        except Exception:
            return {
                "type": "string",
                "description": "附加信息",
                "value": "",
                "confidence": 0.0
            }


def main():
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Usage: python parser.py <input_html> <output_json>"}))
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        html_content = Path(input_file).read_text(encoding='utf-8')
        
        parser = WebPageParser()
        result = parser.parse(html_content)
        
        Path(output_file).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        
    except Exception as e:
        error_result = {"error": str(e)}
        Path(output_file).write_text(json.dumps(error_result, ensure_ascii=False, indent=2), encoding='utf-8')
        sys.exit(1)


if __name__ == "__main__":
    main()