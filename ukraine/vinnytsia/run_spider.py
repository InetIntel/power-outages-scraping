from scrapy.crawler import CrawlerProcess

from ukraine.vinnytsia.utils import mk_dir
from ukraine.vinnytsia.crawler import VinnytsiaSpider
from ukraine.vinnytsia.post_processor import post_process_vinnytsia

def run_vinnytsia_spider():
    mk_dir()
    process = CrawlerProcess()

    process.crawl(VinnytsiaSpider)
    process.start()

    post_process_vinnytsia()