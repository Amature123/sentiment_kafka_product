import scrapy
import asyncio
from scrapy.spiders import Spider
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta, timezone
import hashlib
import time
import re
class DemospiderSpider(Spider):
    name = "demospider"
    allowed_domains = ["voz.vn"]
    start_urls = ["https://voz.vn/whats-new"]
    
    processed_posts = set()
    last_scraped_timestamp = None

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
        'COOKIES_ENABLED': True,
        'ROBOTSTXT_OBEY': True,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }
    
    def extract_thread_id(self, url): 
        parsed = urlparse(url)
        path_parts = parsed.path.split('.')
        if len(path_parts) > 1:
            return path_parts[-1]
        return None
    
    def generate_item_id(self, thread_url, timestamp):
        thread_id = self.extract_thread_id(thread_url)
        if thread_id and timestamp:
            id_string = f"{thread_id}_{timestamp}"
            return hashlib.md5(id_string.encode()).hexdigest()
        return None

    def start_requests(self):
        while True:
            yield scrapy.Request(
                self.start_urls[0],
                callback=self.parse,
                dont_filter=True,
                meta={'dont_cache': True}
            )
            time.sleep(10)

    def parse(self, response):
        thread_containers = response.xpath("//div[contains(@class, 'structItem structItem--thread')]")
        
        threads = []
        for thread in thread_containers:
            latest_link = thread.xpath(".//div[@class='structItem-cell structItem-cell--latest']//a[contains(@href, '/latest')]/@href").get()
            if latest_link:
                thread_url = urljoin(response.url, latest_link)
                thread_date_str = thread.xpath(".//div[@class='structItem-cell structItem-cell--main']//time/@datetime").get()
                
                thread_info = {
                    'url': thread_url,
                    'thread_title': thread.xpath(".//div[@class='structItem-title']//a/text()").get(),
                    'thread_date': thread_date_str,
                    'timestamp': datetime.fromisoformat(thread_date_str.replace('Z', '+00:00')) if thread_date_str else None
                }
                threads.append(thread_info)
        
        sorted_threads = sorted(threads, key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min)
        
        for thread in sorted_threads:
            yield scrapy.Request(
                thread['url'],
                callback=self.parse_latest_message,
                meta={'thread_info': thread},
                dont_filter=True
            )

    async def parse_latest_message(self, response):
        thread_info = response.meta['thread_info']

        message_containers = response.xpath("//article[contains(@class, 'message message--post')]")
        sorted_messages = sorted(
            message_containers,
            key=lambda m: m.xpath(".//time[@class='u-dt']/@datetime").get()
        )

        # Calculate the cutoff time: current time (UTC) - 10 minutes
        time_threshold = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(minutes=10)
        
        new_messages = []
        for message_container in sorted_messages:
            message_content = message_container.xpath(".//div[contains(@class, 'message-userContent')]//div[@class='bbWrapper']//text()[not(ancestor::blockquote)]").getall()
            message_content = ' '.join([text.strip() for text in message_content if text.strip()])
            pattern = r'\{\n\t+\"lightbox_.*?\"Toggle sidebar\"\n\t+\}'

            message_content = re.sub(pattern, '', message_content, flags=re.DOTALL).strip()
            username = message_container.xpath(".//h4[@class='message-name']//span[@itemprop='name']/text()").get()
            timestamp_str = message_container.xpath(".//time[@class='u-dt']/@datetime").get()
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')) if timestamp_str else None

            if timestamp and timestamp >= time_threshold:
                item_id = self.generate_item_id(response.url, timestamp_str)
                if item_id and item_id not in self.processed_posts:
                    new_messages.append({
                        'id': item_id,
                        'thread_title': thread_info['thread_title'],
                        'thread_date': thread_info['thread_date'],
                        'latest_poster': username,
                        'latest_post_time': timestamp_str,
                        'message_content': message_content,
                        'thread_url': response.url
                    })

        # Yield each message with a delay between them
        for message in new_messages:
            self.processed_posts.add(message['id'])
            self.logger.info(f"Yielding post: {message['thread_title']} from user {message['latest_poster']}")
            yield message
            await asyncio.sleep(1)  # Set a 1-second delay between each message

        if not new_messages:
            self.logger.info("No new messages found. Waiting 10 seconds before checking again.")
            await asyncio.sleep(10)  # Wait 10 seconds if no new messages are found

        # Resume from the last scraped timestamp in future requests
        if self.last_scraped_timestamp:
            self.logger.info(f"Resuming from last timestamp: {self.last_scraped_timestamp}")
