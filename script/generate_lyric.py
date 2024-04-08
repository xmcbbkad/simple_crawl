import requests
import json
import openai
import os,sys
from retry import retry
import random
import re

GENERAL_CONF_FILE = os.path.abspath(os.path.dirname(__file__))+"/../conf/general_conf.json"
GENERAL_CONF = json.load(open(GENERAL_CONF_FILE, 'r'))
API_KEY = GENERAL_CONF["azure_api_key"]
API_BASE = GENERAL_CONF["azure_api_base"]
#client = OpenAI(api_key=API_KEY)

PROMPT = """
请根据 {topic} 为主题为一段歌曲作词，要求如下：
1. 歌词需要结合歌曲的风格，该歌曲的风格为：{music_style}
2. 歌词的风格为：{lyric_style}
3. 歌词要强调主题和情感，将其贯穿于整个歌词中。清晰地传达情感，让听众能够共鸣和理解你所想表达的内容。
4. 歌词通过讲述一个故事或描述一个场景，使歌词更具故事性和生动性。通过具体的细节和描述，让听众能够形象地感受到歌曲所表达的意境。
5. 考虑使用修辞手法，如比喻、拟人、排比、对仗等，来增强歌词的表现力和艺术性。这些手法可以使歌词更富有想象力和诗意。
6. 考虑歌词与旋律和节奏的配合，使其在音乐中流畅地呈现出来。注意音节的长度、重音的位置以及歌词的节奏感，使其与音乐和唱法相协调。
7. 运用形象化的语言和意象，创造出生动的画面感。通过用词的选择和组合，让听众能够产生视觉上的联想，加强歌词的表现力和记忆性。
8. 在歌词中使用反复和重复的手法，以增加歌曲的吸引力和记忆性。通过重复某个关键词、短语或句子，使其在听众心中留下深刻的印象。
9. 在歌词中展示自己的独特风格和观点，不拘泥于传统的写作方式。尝试创新的词语组合、句式结构和表达方式，让歌词更具个性和独特性。
"""

class GenerateLyric():
    def __init__(self, ):
        self.data_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/lyric/"
        self.music_style_list = self.load_music_style()
        self.lyric_style_list = self.load_lyric_style()

    def load_music_style(self):
        music_style_conf_file = self.data_dir + "music_style_conf.txt"
        with open(music_style_conf_file, 'r') as file:
            music_style_conf = [line.strip() for line in file.readlines()]
        return music_style_conf

    def load_lyric_style(self):
        lyric_style_conf_file = self.data_dir + "lyric_style_conf.txt"
        with open(lyric_style_conf_file, 'r') as file:
            lyric_style_conf = [line.strip() for line in file.readlines()]
        return lyric_style_conf

    @retry(Exception, tries=3, delay=2)
    def call_azure_openai(self, prompt, model="gpt-4", stream=False):
        openai.api_type = "azure"
        openai.api_base = API_BASE
        openai.api_key = API_KEY
        openai.api_version = "2023-05-15"

        print(prompt)
        completion = openai.ChatCompletion.create(
            #engine="gpt-35-turbo",
            engine=model,
            messages=prompt,
            stream=stream
        )

        if stream:
            return completion

        #client = OpenAI(api_key=API_KEY)
        #
        #response_data = client.chat.completions.create(
        #    model = "gpt-3.5-turbo",
        #    max_tokens=240,
        #    messages=prompt,
        #)

        print('------------')
        response_data = completion.to_dict_recursive()
        print(response_data)
        if "choices" in response_data and len(response_data["choices"]) > 0:
            generated_text = response_data["choices"][0]["message"]["content"]
            return generated_text
        else:
            #print(response_data)
            print("Error generating chat response")
            return None

    def generate_lyric(self, topic):
        music_style = random.sample(self.music_style_list, 1)[0]
        lyric_style = random.sample(self.lyric_style_list, 1)[0]
        
        prompt = PROMPT.format(topic=topic, music_style=music_style, lyric_style=lyric_style)

        messages = []
        messages.append({"role":"user", "content": prompt})
        r = self.call_azure_openai(messages) 
        return r




if __name__ == "__main__":
    #GenerateRole().generate_role_once()
    #GenerateRole().generate_role_all("role.txt")
    #GenerateRole().generate_description_once()
    #GenerateRole().generate_description_all(output_file="role_with_descripton.json")
    r = GenerateLyric().generate_lyric(sys.argv[1])
    print(r)
