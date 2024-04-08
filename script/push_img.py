import requests
from urllib.parse import urlparse
import oss2
import json
import base64
import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI
import os,sys


GENERAL_CONF_FILE = os.path.abspath(os.path.dirname(__file__))+"/../conf/general_conf.json"
GENERAL_CONF = json.load(open(GENERAL_CONF_FILE, 'r'))
API_KEY = GENERAL_CONF["openai_api_key"]
client = OpenAI(api_key=API_KEY)
#custom_instructions4vision = """
#我是一个女生，我叫赵紫婷，我的相册里有一张我的照片，请帮我生成这张照片的简单描述，生成要求如下：
#1. 用不多于50个中文汉字给照片一个简单描述。
#2. 如果照片中有我，就描述我的穿着，姿态。如果没有我，就不要描述我的穿着和姿态。
#3. 发挥想象力想象这张照片的拍摄场景或故事，场景或故事只要合理就行。
#4. 不要用"似乎"，"可能"的语气，要确定，我相信你的想象力。
#5. 一定要描述出照片最大的特点。
#6.  用第一人称写。
#举例：
#    1. 我穿着印花连衣长裙，站在马六甲海峡清真寺旁边，去年和男友十一假期旅游时拍的。
#    2. 我穿着红色连衣裙，坐在酒吧吧台旁举着红酒杯，某天下班后去泡吧时拍的。
#    3. 我穿着白色无袖上衣，坐在餐厅桌旁正准备吃大披萨，庆祝过生日时拍的。
#    4. 我穿着一身白色紧身运动装，在街道上跑步，每天早上跑步健身时拍的。
#    5. 我穿着白色裹胸连衣裙，站在海边沙滩上，周末去海边玩时拍的。
#    6. 我穿着白色裹胸和超短裙，站在室内，发给男朋友的自拍照。
#
#生成照片描述时可以结合我的基本信息：
#出生地：上海
#学历：麻省理工学院商业分析硕士（Master of Business Analytics）
#年龄：29岁
#身高：172cm
#体重：52kg
#外貌特征：细腻的皮肤质感，高挑纤细的身材。喜欢穿无袖毛衫，展现出线条流畅的手臂，有着明显的健身房锻炼痕迹，拥有一头柔顺的长发。
#星座：天蝎座
#婚姻状况：未婚
#感情状况：单身
#职业：金融公司的高级分析师，工作能力强，对数据和市场分析有独到见解。
#副业：自媒体网络博主，内容涵盖生活方式、财经知识和音乐创作。
#兼职：在宠物领养店兼职，帮助流浪动物找到新家，体现了她对弱小生命的关爱。  独立唱作人，业余时间创作和演唱自己的歌曲，偶尔在小型音乐节和咖啡馆进行表演。
#兴趣爱好：热爱健身运动，尤其喜欢瑜伽和力量训练。热衷于音乐创作和吉他演奏，有一定的音乐天赋。喜欢独自旅行，探索不同的文化和自然美景。
#家庭背景：出生于知识分子家庭，受到良好的教育。父母都是大学教授，从小培养她独立思考和解决问题的能力。
#
#"""


custom_instructions4vision = """
我是一个女生，我叫赵紫婷，我的相册里有一张我平时用手机拍的照片，请帮我生成这张照片的简单描述，生成要求如下：
1. 描述要简单，不能多于50个中文汉字。
2. 发挥想象力想象这张照片的拍摄场景或故事，场景或故事只要合理就行。
3. 不要用"似乎"，"可能"的语气，要确定，我相信你的想象力。
4. 一定要描述出照片最大的特点。
5.  用第一人称写。
6. 这张照片一般都不是人物照片，而是风景、物品等照片。发挥想象力描述我拍这张照片的内容和当时的场景。
举例：
    1. 我在休假出去旅游时，拍的马六甲海峡清真寺。
    2. 我某天下班后去泡吧时，拍的酒吧吧台上的红酒杯。
    3. 我庆祝生日时，拍的餐厅桌上刚点的大披萨。
    4. 我早上在街道上跑步时，拍的同在锻炼的人们。
    7. 我寒假去长白山上玩拍的雄伟的大山。
    8. 我逛饰品店，拍的看上的一对漂亮耳钉。
    9. 我拍的新换的iphone手机壳，很可爱吧。

生成照片描述时可以结合我的基本信息：
出生地：上海
学历：麻省理工学院商业分析硕士（Master of Business Analytics）
年龄：29岁
身高：172cm
体重：52kg
外貌特征：细腻的皮肤质感，高挑纤细的身材。喜欢穿无袖毛衫，展现出线条流畅的手臂，有着明显的健身房锻炼痕迹，拥有一头柔顺的长发。
星座：天蝎座
婚姻状况：未婚
感情状况：单身
职业：金融公司的高级分析师，工作能力强，对数据和市场分析有独到见解。
副业：自媒体网络博主，内容涵盖生活方式、财经知识和音乐创作。
兼职：在宠物领养店兼职，帮助流浪动物找到新家，体现了她对弱小生命的关爱。  独立唱作人，业余时间创作和演唱自己的歌曲，偶尔在小型音乐节和咖啡馆进行表演。
兴趣爱好：热爱健身运动，尤其喜欢瑜伽和力量训练。热衷于音乐创作和吉他演奏，有一定的音乐天赋。喜欢独自旅行，探索不同的文化和自然美景。
家庭背景：出生于知识分子家庭，受到良好的教育。父母都是大学教授，从小培养她独立思考和解决问题的能力。

"""

class PushImg():
    def __init__(self, ):
        self.data_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/zhaoziting_img/"
        self.oss_access_key_id = GENERAL_CONF["oss_access_key_id"]
        self.oss_access_key_secret = GENERAL_CONF["oss_access_key_secret"]
        self.oss_endpoint = "http://oss-cn-shanghai.aliyuncs.com"
        self.oss_bucket_name = "masterai"
        self.oss_auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
        self.oss_bucket = oss2.Bucket(self.oss_auth, self.oss_endpoint, self.oss_bucket_name)

    def download_images(self, urls_file, output_folder):
        urls_file = self.data_dir + urls_file
        output_folder = self.data_dir + output_folder

        os.makedirs(output_folder, exist_ok=True)
    
        with open(urls_file, 'r') as file:
            image_urls = file.read().splitlines()
    
        for index, url in enumerate(image_urls, start=1):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # 从URL中提取文件名
                    url_path = urlparse(url).path
                    file_name = os.path.join(output_folder, os.path.basename(url_path))
    
                    # 保存文件到本地
                    with open(file_name, 'wb') as img_file:
                        img_file.write(response.content)
                    print(f"下载成功: {file_name}")
                else:
                    print(f"下载失败，状态码: {response.status_code}, URL: {url}")
    
            except Exception as e:
                print(f"下载失败，发生异常: {e}, URL: {url}")

    def list_img_url(self, prefix, output_file):
        output_file = self.data_dir + output_file
        result = self.oss_bucket.list_objects(prefix=prefix)
        with open(output_file, 'w') as f_out:
            index = 0
            for obj in oss2.ObjectIterator(bucket=self.oss_bucket, prefix=prefix):
                if obj.key.endswith(("jpg", "png")):
                    url = "https://cdn.deepvinci.tech/"+obj.key
                    f_out.write(url)
                    f_out.write('\n')
                    index +=1 
                    print(index)
                else:
                    print(obj.key)

    def url_to_base64(self, url):
        # Send a HTTP request to the URL of the image
        #response = requests.get(url+'?x-oss-process=image/format,jpeg')
        response = requests.get(url)
    
        # Raise an exception if the GET request was unsuccessful
        response.raise_for_status()
    
        # Open the image
        image = Image.open(BytesIO(response.content))
    
        # Convert the image to bytes
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        img_bytes = buffer.getvalue()
    
        # Convert the bytes to Base64
        base64_img = base64.b64encode(img_bytes)
    
        # Convert to string
        base64_string = base64_img.decode('utf-8')
    
        return base64_string
    
    
    def call_gpt4v(self, url):
        try:
            base64_image = self.url_to_base64(url)
        except Exception as e:
            print("Error,load image failed!")
            return None
        return self.call_gpt4v_base64(base64_image)
    
    def call_gpt4v_base64(self, base64_image):
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": custom_instructions4vision},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                    },
                ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content

    def generate_img_captions(self, input_file, output_file):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file

        output_list = []
        num = 1
        with open(input_file, 'r') as f_in:
            for url in f_in:
                url = url.strip()
                print("num:{}  url:{}".format(num, url))
                caption= "fail"
                try:
                    caption = self.call_gpt4v(url)
                    print("url={}  caption={}".format(url, caption))
                except:
                    print("fail:{}".format(url))
                
                item = {
                    "url": url,
                    "照片描述": caption
                }
                num += 1
                output_list.append(item)
        with open(output_file, 'a', encoding='utf-8') as file:
            file.write(json.dumps(output_list, ensure_ascii=False, indent=4))

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
    
    def get_embedding_for_img_list(self, input_file, output_file):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file
        
        img_list = []
        with open(input_file, 'r') as file:
            img_list = json.load(file)
    
        for item in img_list:
            #item["embedding"] = get_embedding(item["照片描述"])
            item["embedding"] = self.get_baai_embedding(item["照片描述"])
        
        with open(output_file, 'w') as file:
            file.write(json.dumps(img_list, ensure_ascii=False, indent=2))

    def merge_prompt_and_img_list(self, prompt_file, img_file_list, output_file):
        prompt_file = self.data_dir + prompt_file
        for i in range(len(img_file_list)):
            img_file_list[i] = self.data_dir + img_file_list[i]
        output_file = self.data_dir + output_file

        prompt = open(prompt_file, 'r').read()
        img_list = []
        
        for i in range(len(img_file_list)):
            with open(img_file_list[i], 'r') as file:
                img_list.extend(json.load(file))
        
        new_img_list = []
        for i in range(len(img_list)):
            if len(img_list[i]["embedding"]) == 0 or \
               img_list[i]["照片描述"].find("fail")>=0 or \
               img_list[i]["照片描述"].find("抱歉")>=0 or \
               img_list[i]["照片描述"].find("对不起")>=0 or \
               img_list[i]["照片描述"].find("无法")>=0 or \
               img_list[i]["照片描述"].find("null")>=0:
                continue
            img_list[i]["id"] = i+1
            new_img_list.append(img_list[i])

        output = {
            "zhaoziting": {
                "prompt": prompt,
                "img_list": new_img_list
            }
        }
            
        with open(output_file, 'w') as file:
            file.write(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    #PushImg().download_images(urls_file="people_photo_url_1.txt", output_folder="people_photo_1")
    #PushImg().download_images(urls_file="people_photo_url_2.txt", output_folder="people_photo_2")
    
    #PushImg().list_img_url(prefix="inc-core/fanxiaokun/zhaoziting/people_photo_1", output_file="people_photo_cdn_url_1.txt")
    #PushImg().list_img_url(prefix="inc-core/fanxiaokun/zhaoziting/people_photo_2", output_file="people_photo_cdn_url_2.txt")
    #PushImg().list_img_url(prefix="inc-core/fanxiaokun/zhaoziting/虚拟ip聊天场景", output_file="no_people_photo_cdn_url_1.txt")
    
    #url = sys.argv[1]
    #caption = PushImg().call_gpt4v(url)
    #print(caption)
    #PushImg().generate_img_captions(input_file="people_photo_cdn_url_1.txt", output_file="people_photo_with_caption_1.json")
    #PushImg().generate_img_captions(input_file="people_photo_cdn_url_2.txt", output_file="people_photo_with_caption_2.json")
    #PushImg().generate_img_captions(input_file="no_people_photo_cdn_url_1.txt", output_file="no_people_photo_with_caption_1.json")
    
    ##PushImg().get_embedding_for_img_list(input_file="people_photo_with_caption_1.json", output_file="people_photo_with_embedding_1.json")
    #PushImg().get_embedding_for_img_list(input_file="people_photo_with_caption_2.json", output_file="people_photo_with_embedding_2.json")
    #PushImg().get_embedding_for_img_list(input_file="no_people_photo_with_caption_1.json", output_file="no_people_photo_with_embedding_1.json")
    
    img_file_list = [
        "people_photo_with_embedding_1.json",
        "people_photo_with_embedding_2.json",
        "no_people_photo_with_embedding_1.json"
    ]
    #PushImg().merge_prompt_and_img_list("prompt.txt", img_file_list, "img_list_with_baai_embedding.json")
    PushImg().merge_prompt_and_img_list("history_teacher_prompt.txt", [], "gaoran_prompt.json")
