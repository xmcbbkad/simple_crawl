import sys, os
import re
import json
from src.generate_url import GenerateUrl
from src.fetch_url import FetchUrl
import src.html_node_visit as html_node_visit
from bs4 import BeautifulSoup, NavigableString
import shutil
from urllib.parse import quote
from opencc import OpenCC

def extract_title_tag_url_start(node, result):
    if node.name == 'a':
        result["output"]["url"] = "https://crxs.me" + node.get("href")
    if node.name == 'div' and 'title' in node.get("class", []):
        result["output"]['title'] = node.get_text()
    if node.name == 'div' and 'tag' in node.get("class", []):
        result["in_tag"] = True
        result["output"]["tag"] = []

    if result.get("in_tag", False):
        if isinstance(node, NavigableString):
            result["output"]["tag"].append(node.string.strip())
    return html_node_visit.VISIT_NORMAL

def extract_title_tag_url_finish(node, result):
    if node.name == 'div' and 'tag' in node.get("class", []):
        result["in_tag"] = False
    return html_node_visit.VISIT_NORMAL


def extract_chapter_url_start(node, result):
    if node.name == 'a':
        result["url"] = "https://crxs.me" + node.get("href")
        result["title"] = node.get_text()
    return html_node_visit.VISIT_NORMAL

def extract_chapter_url_finish(node, result):
    return html_node_visit.VISIT_NORMAL


def extract_content_from_html_start(node, result):
    if node.name in ["script", "style"]:
        return html_node_visit.VISIT_SKIP_CHILD
    if node.name == "p" and node.get_text().strip():
        if result["content"]:
            #print("--{}--".format(node.get_text().strip()))
            result["content"] += "\n    " + node.get_text().strip()
        else:
            result["content"] += "    " + node.get_text().strip()
        return html_node_visit.VISIT_SKIP_CHILD
    elif node.string and node.string.strip():
        print(node.name)
        result["content"] += "\n" + node.string.strip()

    return html_node_visit.VISIT_NORMAL

def extract_content_from_html_finish(node, result):
    return html_node_visit.VISIT_NORMAL

class CRXS_ME():
    def __init__(self, ):
        self.site = "https://crxs.me/"
        self.output_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/crxs.me/"
        pass
    
    #生成一级列表页url
    def generate_first_list_url(self, first_list_url_file):
        base_url = "https://crxs.me/fictions/{}.html"
        start_index = 1
        end_index = 676
        first_list_url_file = self.output_dir + first_list_url_file
        GenerateUrl().generate_url_1(base_url, start_index, end_index, first_list_url_file)

    #抓取一级列表页html
    def fetch_first_list_url(self, first_list_url_file, first_list_html_dir):
        first_list_url_file = self.output_dir + first_list_url_file
        first_list_html_dir = self.output_dir + first_list_html_dir
        FetchUrl().fetch_url_from_url_list(first_list_url_file, first_list_html_dir)
    
    #从一个列表页html中抽取 标题，tag，内容页url
    def extract_title_tag_url_from_one_first_list_html(self, html_file):
        html_content = open(html_file, 'r', encoding='utf-8').read()
        soup = BeautifulSoup(html_content, 'html.parser')
        list_nodes = soup.select("div.lists")
        list_result = []
        if list_nodes:
            all_children = list_nodes[0].find_all('a')
            for node_a in all_children:
                result = {}
                result["output"] = {}
                html_node_visit.html_node_visit(node_a, extract_title_tag_url_start, extract_title_tag_url_finish, result)
                list_result.append(result["output"])
        return list_result

    #从所有列表页html中抽取 标题，tag, 内容页url
    def extract_title_tag_url_from_first_list_html(self, first_list_html_dir, book_meta_file):
        meta_all = []
        first_list_html_dir = self.output_dir + first_list_html_dir
        html_files = [file for file in os.listdir(first_list_html_dir) if file.endswith('.html')]
        for html_file in html_files:
            file_path = os.path.join(first_list_html_dir, html_file)
            meta_list = self.extract_title_tag_url_from_one_first_list_html(file_path)
            meta_all.extend(meta_list)

        with open(self.output_dir + book_meta_file, 'w', encoding='utf-8') as json_file:
            json.dump(meta_all, json_file, ensure_ascii=False, indent=4)

    #抓取所有的内容页html，内容页html中肯还包含二级列表页
    def fetch_content_or_second_list_url(self, book_meta_file, content_or_second_list_html):
        book_meta_file = self.output_dir + book_meta_file
        meta_list = json.load(open(book_meta_file, 'r', encoding='utf-8'))
        urls = []
        for item in meta_list:
            urls.append(item.get("url", ''))

        content_or_second_list_html = self.output_dir + content_or_second_list_html
        FetchUrl().fetch_urls(urls,content_or_second_list_html)    
    

    #把内容页和一级列表页区分开
    def split_content_and_second_list(self, input_dir, content_dir, second_list_dir):
        input_dir = self.output_dir + input_dir
        content_dir = self.output_dir + content_dir
        second_list_dir = self.output_dir + second_list_dir
        os.makedirs(content_dir, exist_ok=True) 
        os.makedirs(second_list_dir, exist_ok=True) 

        for filename in os.listdir(input_dir):
            if not filename.endswith(".html"):
                continue
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            if "class=\"chapters\"" in file_content:
                second_list_path = os.path.join(input_dir, filename)
                shutil.move(second_list_path, second_list_dir)
            else:
                content_path = os.path.join(input_dir, filename)
                shutil.move(content_path, content_dir)


    #从二级列表页html中抽取出chapter url
    def extract_chapter_url_from_second_list_html(self, second_list_html):
        html_content = open(second_list_html, 'r', encoding='utf-8').read()
        soup = BeautifulSoup(html_content, 'html.parser')
        list_nodes = soup.select("div.chapters")
        chapter_list_url = []
        if list_nodes:
            all_children = list_nodes[0].find_all('div')
            for node_div in all_children:
                result = {}
                html_node_visit.html_node_visit(node_div, extract_chapter_url_start, extract_chapter_url_finish, result)
                chapter_list_url.append(result)
        return chapter_list_url

    #从二级列表页html中抽取出chapter url
    def extract_chapter_url_from_second_list_html_dir(self, second_list_html_dir, old_meta_file, new_meta_file):
        second_list_html_dir = self.output_dir + second_list_html_dir

        old_meta_file = self.output_dir + old_meta_file
        meta_list = json.load(open(old_meta_file, 'r', encoding='utf-8'))
        for item in meta_list:
            second_list_html = os.path.join(self.output_dir, second_list_html_dir, quote(item.get("url", ""), safe=''))
            if os.path.exists(second_list_html):
                chapter_url_list = self.extract_chapter_url_from_second_list_html(second_list_html)
                item["chapters"] = chapter_url_list
        
        with open(self.output_dir + new_meta_file, 'w', encoding='utf-8') as json_file:
            json.dump(meta_list, json_file, ensure_ascii=False, indent=4)

    #抓取所有的chapter内容页 html
    def fetch_content_chapter_url(self, book_meta_file, content_chapter_html):
        book_meta_file = self.output_dir + book_meta_file
        content_chapter_html = self.output_dir + content_chapter_html
        os.makedirs(content_chapter_html, exist_ok=True) 
        meta_list = json.load(open(book_meta_file, 'r', encoding='utf-8'))
        urls = []
        for item in meta_list:
            chapter_list = item.get("chapters", [])
            for chapter in chapter_list:
                urls.append(chapter.get("url", ''))

        print(len(urls))
        FetchUrl().fetch_urls(urls,content_chapter_html, max_threads=1, sleep_time=10)    

    def split_book_urls(self, book_meta_file, book_content_urls_all_file):
        book_meta_file = self.output_dir + book_meta_file
        meta_list = json.load(open(book_meta_file, 'r', encoding='utf-8'))
        urls = []
        for item in meta_list:
            chapter_list = item.get("chapters", [])
            if chapter_list:
                for chapter in chapter_list:
                    urls.append(chapter.get("url", ''))
            else:
                urls.append(item.get("url", ''))
        
        with open(self.output_dir+book_content_urls_all_file, 'w') as file:
            for url in urls:
                file.write(url+'\n')
        
        num_chunks = 10
        avg_chunk_size = len(urls) // num_chunks
        remainder = len(urls) % num_chunks
        chunks = []

        i = 0
        for _ in range(num_chunks):
            chunk_size = avg_chunk_size + 1 if remainder > 0 else avg_chunk_size
            chunks.append(urls[i:i + chunk_size])
            i += chunk_size
            remainder -= 1

        for i, chunk in enumerate(chunks):
            filename = self.output_dir + f"book_content_urls_{i}.txt"
            with open(filename, 'w') as file:
                for item in chunk:
                    file.write(str(item) + '\n')


    def traditional_to_simplified(self, traditional_text):
        cc = OpenCC('t2s')  # 't2s' 表示从繁体到简体的转换
        simplified_text = cc.convert(traditional_text)
        return simplified_text

    def extract_content_from_html(self, html_file, output_file):
        html_content = open(html_file, 'r', encoding='utf-8').read()
        soup = BeautifulSoup(html_content, 'html.parser')
        nodes = soup.select("div.fiction-body")
        result ={}
        result["content"] = ""
        if nodes:
            html_node_visit.html_node_visit(nodes[0], extract_content_from_html_start, extract_content_from_html_finish, result)

        result["content"]  = self.traditional_to_simplified(result["content"])
        rubbish_list = [
            "（看精彩成人小说上《成人小说网》：https://crxs.me）",
            "（成人APP精选（https://xchina.app），每款都经过站长人工审核）",
            "请点击这里继续阅读本文"
        ]
        for rubbish in rubbish_list:
            result["content"] = result["content"].replace(rubbish, "")


        content=""
        content_list = result["content"].split("\n")
        for i in range(len(content_list)):
            if content_list[i].strip():
                content += content_list[i]
            if i != len(content_list)-1:
                content += '\n'

        with open(output_file, "w") as file:
            file.write(content)
    
    def extract_content_from_html_dir(self, html_dir, raw_text_dir):
        html_dir = self.output_dir + html_dir
        raw_text_dir = self.output_dir + raw_text_dir
        os.makedirs(raw_text_dir, exist_ok=True) 
        for filename in os.listdir(html_dir):
            if filename.endswith(".html"):
                input_file_path = os.path.join(html_dir, filename)
                output_file_path = os.path.join(raw_text_dir, filename)
                self.extract_content_from_html(input_file_path, output_file_path)

    def make_pretrain_data_from_file(self, raw_text_file):
        lines = open(raw_text_file, 'r', encoding='utf-8').read().split('\n')
        
        output_list = []
        one_data = ""
        for i in range(len(lines)):
            one_data += lines[i]

            if len(one_data) >=3000:
                output_list.append(one_data)
                one_data = ""
        
        if one_data:
            output_list.append(one_data)
        print("chunk_num:{}".format(len(output_list))) 
        return output_list

    def make_pretrain_data_from_dir(self, raw_text_dir, train_file):
        raw_text_dir = self.output_dir + raw_text_dir
        train_file = self.output_dir + train_file
        with open(train_file, 'w', encoding="utf-8") as file:
            for filename in os.listdir(raw_text_dir):
                if filename.endswith(".html"):
                    input_file_path = os.path.join(raw_text_dir, filename)
                    data_list = self.make_pretrain_data_from_file(input_file_path)
                    for item in data_list:
                        file.write(item+'\n')

    def make_pretrain_data_from_dir_v2(self, raw_text_dir, book_content_urls_all_file, train_file):
        raw_text_dir = self.output_dir + raw_text_dir
        train_file = self.output_dir + train_file
        book_content_urls_all_file = self.output_dir + book_content_urls_all_file

        with open(book_content_urls_all_file, 'r') as file:
            urls = file.readlines()

        with open(train_file, 'w', encoding="utf-8") as file:
            for url in urls:
                if url.strip().endswith(".html"):
                    input_file_path = os.path.join(raw_text_dir, quote(url.strip(), safe=""))
                    lines = open(input_file_path, 'r').readlines()
                    for line in lines:
                        file.write(line)
                    file.write('\n')
            #for filename in os.listdir(raw_text_dir):
            #    if filename.endswith(".html"):
            #        print(filename)
            #        input_file_path = os.path.join(raw_text_dir, filename)
            #        lines = open(input_file_path, 'r').readlines()
            #        for line in lines:
            #            file.write(line)

    def make_story_generate_sft_data(self, book_meta_file, raw_text_dir, train_file):
        book_meta_file = self.output_dir + book_meta_file
        raw_text_dir = self.output_dir + raw_text_dir
        train_file = self.output_dir + train_file

        meta_list = json.load(open(book_meta_file, 'r', encoding='utf-8'))
        urls_and_titles = []
        for item in meta_list:
            if not item.get("chapters", []):
                urls_and_titles.append([item.get("url", ''), item.get("title", '')])
       
        output_list = []
        for [url, title] in urls_and_titles:
            if url.strip().endswith(".html"):
                input_file_path = os.path.join(raw_text_dir, quote(url.strip(), safe=""))
                
                article = open(input_file_path, 'r').read()
                output = {
                    "prompt": '以《{}》为标题，写一个短篇情色故事，故事要完整:'.format(title),
                    "query": "",
                    "response": article,
                    "history": ""
                }
                output_list.append(output)

        with open(train_file, 'w', encoding='utf-8') as json_file:
            json.dump(output_list, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    crxs_me = CRXS_ME()
    #crxs_me.generate_first_list_url("first_list_url.txt")
    #crxs_me.fetch_first_list_url("first_list_url.txt", "first_list_html")
    #crxs_me.extract_title_tag_url_from_first_list_html("first_list_html", "book_meta.json")
    #crxs_me.fetch_content_or_second_list_url("book_meta.json", "content_or_second_list_html")
    #crxs_me.split_content_and_second_list("content_or_second_list_html", "content_html", "second_list_html")
    #crxs_me.extract_chapter_url_from_second_list_html_dir("second_list_html", "book_meta.json", "book_meta_with_chapter.json")
    #crxs_me.fetch_content_chapter_url("book_meta_with_chapter.json", "content_chapter_html_1")
   
    #crxs_me.split_book_urls("book_meta_with_chapter.json", "book_content_urls_all.txt")

    #base_url = os.path.abspath(os.path.dirname(__file__))+"/../data/crxs.me/"
    #split_num = 9
    #FetchUrl().fetch_url_from_url_list(base_url+"book_content_urls_{}.txt".format(split_num), base_url+"book_content_html_{}".format(split_num), 10) 
    
    #crxs_me.extract_content_from_html("/Users/xiaokunfan/Desktop/code/porn_book/simple_crawl/data/crxs.me/book_content_html_all/https%3A%2F%2Fcrxs.me%2Ffiction%2Fid-6433e371e90de%2F15.html", "a.txt")
    #crxs_me.extract_content_from_html_dir("content_chapter_html", "raw_chapter_text_dir")
    #crxs_me.extract_content_from_html_dir("content_html", "raw_text_dir")
    #crxs_me.extract_content_from_html_dir("book_content_html_all", "book_content_raw_text_all")
    #data = crxs_me.make_pretrain_data_from_file("/Users/xiaokunfan/Desktop/code/porn_book/simple_crawl/data/crxs.me/raw_chapter_text_dir/https%3A%2F%2Fcrxs.me%2Ffiction%2Fid-5f1411423419a%2F6.html")
    #crxs_me.make_pretrain_data_from_dir("raw_text_dir", "crxs_pt.txt")
    #crxs_me.make_pretrain_data_from_dir("raw_chapter_text_dir", "crxs_long_pt.txt")
    #crxs_me.make_pretrain_data_from_dir_v2("raw_chapter_text_dir", "crxs_long_pt_v2.txt")
    #crxs_me.make_pretrain_data_from_dir_v2("book_content_raw_text_all", "book_content_urls_all.txt", "crxs_all_pt.txt")
    crxs_me.make_story_generate_sft_data("book_meta_with_chapter.json", "book_content_raw_text_all", "crxs_story_generate.json")
