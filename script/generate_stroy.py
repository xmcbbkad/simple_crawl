import os, sys
import json
import requests

class GenerateStory():
    def __init__(self, ):
        #self.data_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/teacher_zhanglimin_story/"
        self.data_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/dingtang/"

    def get_baai_embedding(self, input_string):
        url = "https://alpha-chatimage.inceptions.io/api/v1/embedding"
        data = {
            "query": input_string,
            "language": "cn"
        }
        response = requests.post(url, json=data)
        # 检查请求是否成功
        if response.status_code == 200:
            print("请求成功")
            #print("响应内容:", response.json())
            return response.json().get("embedding", [])
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
        return []

    def generate_embedding(self, input_file, output_file):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file

        story_list = []
        with open(input_file, 'r') as file:
            for line in file:
                story_list.append(json.loads(line))
    
        for item in story_list:
            item["title"]  = item["topic"]
            item["content"]  = item["response"]
            item["embedding"] = self.get_baai_embedding(item['title'])
            del item["topic"]
            del item["response"]
    
        with open(output_file, 'w') as file:
            file.write(json.dumps(story_list, ensure_ascii=False, indent=2))
    
    def merge_prompt_and_story_list(self, prompt_file, story_list_file, output_file):
        prompt_file = self.data_dir + prompt_file
        story_list_file = self.data_dir + story_list_file
        output_file = self.data_dir + output_file
       
        prompt = open(prompt_file, 'r').read()
        story_list = []
        with open(story_list_file, 'r') as file:
            story_list = json.load(file)
    
        output = {
            "voice": "voice://openai/nova/default",
            "prompt": prompt,
            "story_list": story_list
        }
            
        with open(output_file, 'w') as file:
            file.write(json.dumps(output, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    #GenerateStory().generate_embedding(input_file="story.jsonl", output_file="story_with_embedding.json")
    #GenerateStory().merge_prompt_and_story_list(story_list_file="story_with_embedding.json", output_file="zhanglimin_story_config.json")
    
    #GenerateStory().generate_embedding(input_file="story.jsonl", output_file="story_with_embedding.json")
    GenerateStory().merge_prompt_and_story_list(prompt_file="prompt.txt", story_list_file="story_with_embedding.json", output_file="zhaolinger_story_config.json")

