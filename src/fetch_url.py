import os,sys
import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from retrying import retry
import time

class FetchUrl():
    def __init__(self):
        pass
    
    @retry(wait_fixed=2000, stop_max_attempt_number=3)
    def fetch_url(self, url, output_file=None, sleep_time=0, skip_exist=True, proxy=""):
        print("start fetch_url:{}".format(url))
        if skip_exist and output_file and os.path.exists(output_file):
            return
                
        if sleep_time >0:
            time.sleep(sleep_time)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        try:
            if proxy :
                proxies = {
                        "http": proxy,
                        "https": proxy
                }
                response = requests.get(url, headers=headers, proxies=proxies)
            else:
                response = requests.get(url, headers=headers)
            
            response.raise_for_status()
            if output_file:
                #print(output_file)
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(response.text)
            print("finish fetch_url:{}".format(url))
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error downloading page: {e} proxy={proxy}")
            return None


    def fetch_url_from_url_list(self, url_list_file, output_dir, sleep_time=0):
        url_list = []
        with open(url_list_file, 'r') as file:
            for line in file:
                url_list.append(line.strip())
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        #for i in range(len(url_list)):
        #    print("fetch_url_from_url_list——{}/{}".format(i, len(url_list)))
        #    output_file = output_dir+"/"+quote(url_list[i], safe='')
        #    if not os.path.exists(output_file) or os.path.getsize(output_file)==0:
        #        self.fetch_url(url_list[i], output_file)
        self.fetch_urls(url_list, output_dir, 1, sleep_time) 

    def fetch_urls(self, urls, output_dir, max_threads=1, sleep_time=0):
        with ThreadPoolExecutor(max_threads) as executor:
            executor.map(lambda url: self.fetch_url(url, os.path.join(output_dir, quote(url, safe='')), sleep_time), urls)
        
