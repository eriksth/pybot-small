#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import subprocess
from urllib.request import urlopen
from datetime import datetime
import uuid

def load_xml(url):
    with urlopen(url) as response:
        return response.read()

def parse_sitemap_or_index(url, log_file, enable_logging):
    xml_content = load_xml(url)
    root = ET.fromstring(xml_content)
    if root.tag.endswith('sitemapindex'):
        if enable_logging:
            write_log(f"{uuid.uuid4()} | Parsing sitemap index | {url}", log_file)
        sitemap_tags = root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
        sitemap_urls = [sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text for sitemap in sitemap_tags]
        urls = []
        for sitemap_url in sitemap_urls:
            urls.extend(parse_sitemap_or_index(sitemap_url, log_file, enable_logging))
        return urls
    else:
        if enable_logging:
            write_log(f"{uuid.uuid4()} | Parsing sitemap | {url}", log_file)
        url_tags = root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        valid_urls = []
        for url_tag in url_tags:
            loc = url_tag.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc is not None and loc.text:
                valid_urls.append(loc.text)
        return valid_urls

def write_log(message, log_file):
    with open(log_file, "a") as file:
        file.write(f"{datetime.now().isoformat()} | {message}\n")

def cache_urls(urls, use_wget=True, log_file=None, enable_logging=False, user_agent=None):
    for url in urls:
        try:
            if use_wget:
                wget_command = ['wget', '--quiet', '--delete-after', '--no-verbose', url]
                if user_agent:
                    wget_command.extend(['--user-agent', user_agent])
                subprocess.run(wget_command, check=True)
                log_message = f"{uuid.uuid4()} | Crawled with wget | {url}"
            else:
                curl_command = ['curl', '-s', '-o', '/dev/null', url]
                if user_agent:
                    curl_command.extend(['-A', user_agent])
                subprocess.run(curl_command, check=True)
                log_message = f"{uuid.uuid4()} | Crawled with curl | {url}"
            if enable_logging:
                write_log(log_message, log_file)
        except subprocess.CalledProcessError as e:
            error_message = f"{uuid.uuid4()} | Error processing | {url} | {e}"
            if enable_logging:
                write_log(error_message, log_file)

if __name__ == "__main__":
    sitemap_url = 'YOUR_SITEMAP_HERE'  # Replace with your sitemap index URL
    log_file = "process_log.txt"  # Set log file name or None to disable logging
    enable_logging = True  # Set to False to disable logging
    user_agent = "ACrawl PyBot-small/1.0" # or set a user agent for mobile caching
    #user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1"

    if enable_logging:
        write_log(f"{uuid.uuid4()} | Crawler started", log_file)

    urls = parse_sitemap_or_index(sitemap_url, log_file, enable_logging)

    use_wget = True  # Set to False to use curl
    cache_urls(urls, use_wget, log_file, enable_logging, user_agent)