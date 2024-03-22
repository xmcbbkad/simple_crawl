import os
import requests

def fetch_url(url, output_file=None, skip_exist=True):
    print("start fetch_url:{}".format(url))
    if skip_exist and os.path.exists(output_file):
        return
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        proxies = {
            "http": "http://customer-yjkGhUIi-cc-US-sessid-1704335151_10009:uB343P56@gate-sg.ipfoxy.io:58611",
            "https": "http://customer-yjkGhUIi-cc-US-sessid-1704335151_10009:uB343P56@gate-sg.ipfoxy.io:58611",
        }
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        if output_file:
            #print(output_file)
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(response.text)
        print("finish fetch_url:{}".format(url))
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading page: {e}")
        return None

if __name__ == "__main__":
    url = "https://crxs.me/fiction/id-65930bc618218.html"
    #url = "http://6.6.6.6:54321/exchange?different=1"
    fetch_url(url, "a.html")
