from scrapy.crawler import CrawlerProcess

from ukraine.khmelnytsky.utils import mk_dir
from ukraine.khmelnytsky.crawler import KhmelnytskySpider
from ukraine.khmelnytsky.post_processor import post_process_khmelnytsky

def run_khmelnytsky_spider():
    mk_dir()
    process = CrawlerProcess()

    process.crawl(KhmelnytskySpider)
    process.start()

    post_process_khmelnytsky()