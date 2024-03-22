import os,sys
from bs4 import BeautifulSoup, NavigableString
from src.fetch_url import FetchUrl

class CN_PROXY_TOOLS():
    def __init__(self,):
        self.site = "https://cn.proxy-tools.com/"
        self.output_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/cn.proxy-tools.com/"
    
    #从原始网页生成proxy列表
    def generate_candidate_proxy_list(self, html_file, candidate_proxy_file):
        html_file = self.output_dir + html_file
        candidate_proxy_file = self.output_dir + candidate_proxy_file

        html_content = open(html_file, 'r', encoding='utf-8').read()
        soup = BeautifulSoup(html_content, 'html.parser')
       
        
        proxy_list = []
        tr_tags = soup.find_all('tr')
        for tr_tag in tr_tags:
            td_tags = tr_tag.find_all('td')
            if len(td_tags) >= 3:
                if td_tags[2].get_text(strip=True).startswith("HTTP"):
                    proxy = "{}://{}:{}".format(td_tags[2].get_text(strip=True), td_tags[0].get_text(strip=True), td_tags[1].get_text(strip=True))
                    proxy = proxy.lower()
                    proxy_list.append(proxy)

        with open(candidate_proxy_file, "w") as file:
            for item in proxy_list:
                file.write(f"{item}\n")

    def select_good_proxy(self, candidate_proxy_file, good_proxy_file, test_url):
        candidate_proxy_file = self.output_dir + candidate_proxy_file
        good_proxy_file = self.output_dir + good_proxy_file
        with open(candidate_proxy_file, 'r') as file:
            candidate_proxy = file.readlines()
        
        good_proxy = []
        for proxy in candidate_proxy:
            r = FetchUrl().fetch_url(url=test_url, output_file=None, skip_exist=True, proxy=proxy.strip())
            if r:
                good_proxy.append(proxy)

        with open(good_proxy_file, "w") as file:
            for item in good_proxy:
                file.write(f"{item}\n")

if __name__ == "__main__":
    cn_proxy_tools = CN_PROXY_TOOLS()
    cn_proxy_tools.generate_candidate_proxy_list("candidate.html", "candidate_proxy.txt")
    cn_proxy_tools.select_good_proxy("candidate_proxy.txt", "good_proxy.txt", "https://crxs.me/fiction/id-60b7c6bebcd9f/1.html")
    #cn_proxy_tools.select_good_proxy("candidate_proxy.txt", "good_proxy.txt", "https://www.google.com/")

