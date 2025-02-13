#!/usr/bin/python3.10
# python -m crawler.unser_mdr

import crawler.utilities as utl
import re
from bs4 import BeautifulSoup

def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)
    
    if easy_soup is None:
        print(f"Error: {easy_url} returned None")
        return
    
    publication_date_tag = easy_soup.find("p", {"class": "webtime"})
    if publication_date_tag is None or len(publication_date_tag.find_all("span")) < 2:
        print(f"Error: Publication date not found in {easy_url}")
        return
    
    publication_date = str(publication_date_tag.find_all("span")[1])[6:-9].strip()
    
    if publication_date.endswith(","):
        publication_date = publication_date[:-1]

    normal_urls = utl.get_urls_from_soup(
        easy_soup,
        base_url,
        filter_args={
            "name": "div",
            "attrs": {"class": "con cssBoxTeaserStandard conInline"}
        },
        recursive_filter_args={
            "string": re.compile("auch in schwerer Sprache", flags=re.I)
        }
    )
    
    if not normal_urls:
        print(f"Error: No normal URL found for {easy_url}")
        utl.log_missing_url(easy_url)
        return
    
    normal_url = normal_urls[0]
    normal_soup = utl.read_soup(normal_url)
    if normal_soup:
        utl.save_parallel_soup(normal_soup, normal_url, easy_soup, easy_url, publication_date)

def crawling(base_url):
    home_url = "https://www.mdr.de/nachrichten-leicht/index.html"

    main_soup = utl.read_soup(home_url)
    if main_soup is None:
        print("Error: Failed to load main page.")
        return
    
    easy_news_urls = utl.get_urls_from_soup(
        main_soup,
        base_url,
        filter_args={"name": "div", "attrs": {"class": "sectionWrapper section1er audioApp cssPageAreaWithoutContent"}}
    )
    
    for i, easy_url in enumerate(easy_news_urls):
        print(f"[{i+1}/{len(easy_news_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)
    
    archive_urls = [
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-anhalt-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-thueringen-100.html"
    ]

    for url in archive_urls:
        archive_soup = utl.read_soup(url)
        if archive_soup is None:
            print(f"Error: Failed to load archive page {url}")
            continue
        
        string = "targetNode-nachrichten-leichte-sprache"
        easy_information_urls = utl.get_urls_from_soup(
            archive_soup,
            base_url,
            filter_args={"name": "div", "attrs": {"class": string}}
        )

        for i, easy_url in enumerate(easy_information_urls):
            print(f"[{i+1}/{len(easy_information_urls)}] Crawling {easy_url}")
            crawl_site(easy_url, base_url)

def filter_block(tag) -> bool:
    return tag.name == "div" and tag.has_attr("class") and {"section", "sectionDetailPage", "cssBoxContent"}.issubset(set(tag["class"]))

def filter_tags(tag) -> bool:
    if tag.name == "p" and tag.has_attr("class") and ("text" in tag["class"] or "einleitung" in tag["class"]):
        return True
    elif tag.name == "span" and tag.has_attr("class") and "headline" in tag["class"] and tag.parent.name == "h1":
        if not tag.string.endswith("."):
            tag.string.replace_with(str(tag.string).strip() + ".")
        return True
    elif tag.name == "ul" and tag.parent.name == "div" and tag.parent.has_attr("class") and "paragraph" in tag.parent["class"]:
        return True
    return False

def parser(soup: BeautifulSoup) -> BeautifulSoup:
    article_tag = soup.find_all(filter_block)
    if len(article_tag) != 1:
        print("Unaccounted case occurred. Expected one article, found:", len(article_tag))
        return None
    
    article_tag = article_tag[0]
    content = article_tag.find_all(filter_tags)
    result = BeautifulSoup("", "html.parser")
    for tag in content:
        result.append(tag)
    return result

base_url = "https://www.mdr.de/"

def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)

if __name__ == '__main__':
    main()
