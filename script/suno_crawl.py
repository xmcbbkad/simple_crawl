import os,sys
import requests
import time

class SunoCrawl():
    def __init__(self,):
        self.output_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/suno/"
        pass

    def fetch_google_search_results(self, page=0):
        query = "site%3Aapp.suno.ai%2Fsong"
        url = f"https://www.google.com/search?q={query}&start={page*10}"
        print(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to fetch search results.")
            return None

    def save_goole_search_results(self):
        output_dir = self.output_dir + "google_results"
        for i in range(350):
            r = self.fetch_google_search_results(page=i) 
            if r:
                with open("{}/page-{}.html".format(output_dir, i), 'w') as file:
                    file.write(r)
            time.sleep(5)
if __name__ == "__main__":
    SunoCrawl().save_goole_search_results()
