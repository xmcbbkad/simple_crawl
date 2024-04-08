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

PROMPT_IDENTITY = """
生成100个包含两个两个人物的关系对。要求如下：
1. 每对关系中是一男一女。这对关系有相关性，比如老师和学生，医生和病人，丈夫和妻子，男朋友和女朋友，上级和下属等。
2. 一定要生成100对, 多样性要好，不能雷同，不能少，不能重复。
3. 生成的关系中的身份要有一定特殊性，不要太泛指。比如身份可以是"宁波二中数学老师"，而不是"数学老师"或"老师"
4. 输出格式为一行是一个关系对，其中女性在前, 男性在后，用###分隔。
以下是例子:
高中数学老师###高中男生",
喜欢肌肉男的女生###爱健身的男生
刑警女警官###在逃强奸犯
医院小护士###昨晚手术的病人
家庭主妇###丈夫的上司
"""

PROMPT_DESCRIPTION = """
以上是两个人物的身份和性格特点，请生成这两个人物的姓名、性别和人物描述。要求如下：
1. 这两个人物会发生情感相关的故事。为了使故事更有特点，所以人物描述要侧重于描述人物的背景、性格、特点、两人的关系等。
4. 生成的人物信息以json格式输出，不要有多余的字符，这样我可以用json.loads()函数直接解析，格式如下：
[
    {
        "姓名": "",
        "性别": "",
        "身份": "",
        "人物描述": ""
    },
    {
        "姓名": "",
        "性别": "",
        "身份": "",
        "人物描述": ""
    }
]

以下是两个例子:
例1:
[
    {
        "姓名": "张丽敏",
        "性别": "女",
        "身份": "数学老师",
        "人物描述": "张丽敏是刚刚分配进市一中的新老师，从她来报到的第一天起，她的美色就让学校的男生“昂首期盼”了，天生丽质的她，一头飘逸的秀发，俏丽的面容，配合着她那凹凸有致的魔鬼身材，一副清纯可人相, 平时她总是把口红涂得很艳丽,不管是穿窄裙还是套装挺拔的胸脯总是使人心荡神弛，加上她一幅风韵有如空姐的模样,美丽中透着伶俐，温顺中又偶尔显现出顽皮。"
    },
    {
        "姓名": "王宇",
        "性别": "男",
        "身份": "高中男生",
        "人物描述": "王宇是一位青涩而内向的年轻人，他刚刚踏入大学校园，对人生充满好奇和期待。他拥有一头乌黑的头发，戴着一副略微厚重的眼镜，使他看起来更加书卷气十足。王宇身材略显瘦弱，总是在不经意间流露出一种害羞的笑容。王宇对于爱情和人际关系相当天真，他很少与异性交往，对恋爱的事情感到略显手足无措。他总是过分拘谨，很容易因为一点小事而羞涩不已。王宇是一个热爱学术研究的人，对于自己感兴趣的领域有着极大的热情，但一旦谈及感情，就显得有些拘谨。"
    }
]

例2:
[
    {
        "姓名": "白洁",
        "性别": "女",
        "身份": "美女健身教练",
        "人物描述": "白洁是一位性感且充满活力的美女健身教练，身材很棒，凹凸有致，贴身的瑜伽服把身体包裹出完美的曲线，身高有165cm，胸围裸有c罩杯，大长腿笔直，样貌清秀像刘诗诗，普通话标准，声音清脆，看年纪差不多22岁左右，应该刚出社会没多久。白洁是阿呆的健身教练，喜欢调戏阿呆，对阿呆非常热情，内心很喜欢阿呆的，但没有表现得很直接。"
    },
    {
        "姓名": "阿呆",
        "性别": "男",
        "身份": "青涩木讷的大学男生",
        "人物描述": "阿呆有点丑，小小的眼睛透露出好奇和青涩的神采。对于爱情比较害羞，但心中渴望真挚的感情。阿呆是白洁的客户，他暗恋白洁，被白洁的性感吸引。"
    }
]
"""

PROMPT_CHAT = """
根据以上两个人物的信息，生成两人的对话，要求如下:
1. 对话不少于20轮，每轮两人一人说一句。
2. 对话要非常口语化，像真实的聊天。
3. 对话要重点考虑人物描述信息中的人物背景，性格特点和关系程度。
4. 对话要围绕一个生活情感相关的主题。比如“你喜欢什么样的男生？”，“你单身吗？”等。
5. 输出格式为 姓名: XXXXX，举例如下：
许晨: 你今天怎么这么好看~
林珊珊: 谢谢夸奖啊，搞得我有点不好意思，哈哈
许晨: 美女就要自信~ 你的身材是怎么保持这么好的？前凸后翘~
林珊珊: (害羞) 别说啦，人家脸都红了呢。
...
"""


class GenerateRole():
    def __init__(self, ):
        self.data_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/xxx_role/"
        self.role_list = self.load_role()
        self.character_list = self.load_character()
        self.relation_degree_list = self.load_relation_degree()


    def load_role(self):
        role_file = self.data_dir + "role.txt"
        role_list = []
        with open(role_file, 'r') as file:
            for line in file.readlines():
                try:
                    tmp = line.split("###")
                    if len(tmp) == 2:
                        role_list.append([tmp[0].strip(), tmp[1].strip()])
                except:
                    continue
        
        return role_list

    def load_character(self):
        character_file = self.data_dir + "character_conf.txt"
        character_list = []
        with open(character_file, 'r') as file:
            for line in file.readlines():
                try:
                    tmp = line.split("/")
                    if len(tmp) == 2:
                        character_list.append([tmp[0].strip(), tmp[1].strip()])
                except:
                    continue
        
        return character_list

    def load_relation_degree(self):
        relation_degree_file = self.data_dir + 'relation_degree_conf.txt'
        with open(relation_degree_file, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
        return lines

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

    def generate_role_once(self):
        messages = []
        messages.append({"role":"user", "content": PROMPT_IDENTITY})
        r = self.call_azure_openai(messages) 
        return r

    def generate_role_all(self, output_file):
        output_file = self.data_dir + output_file
        for i in range(30):
            r = self.generate_role_once()
            with open(output_file, 'a') as f_out:
                f_out.write(r)

    def generate_description_once(self, prompt):
        messages = []
        messages.append({"role":"user", "content": prompt})
        r = self.call_azure_openai(messages) 
        matches = re.findall(r'\[.*?\]', r, re.DOTALL)
        
        r = json.loads(matches[0])
        return r

    def generate_description_all(self, output_file):
        output_file = self.data_dir + output_file

        for i in range(len(self.role_list)):
            a, b = self.role_list[i][0], self.role_list[i][1]
            tmp_character_list = random.sample(self.character_list, 5)
            a_character = ""
            b_character = ""

            random_index = random.choice([[0, 1], [1, 0]])
            for j in range(len(tmp_character_list)):
                a_character += tmp_character_list[j][random_index[0]]+' '
                b_character += tmp_character_list[j][random_index[1]]+' '

            relation_degree = random.sample(self.relation_degree_list, 1)

            PROMPT_BEFORE = "{}, 性别女, 性格特点:{}\n{}, 性别男，性格特点:{}\n两人关系状态:{}\n".format(a, a_character, b, b_character, relation_degree[0])
            prompt = PROMPT_BEFORE + PROMPT_DESCRIPTION
            try :
                json_dict = self.generate_description_once(prompt)
            
                with open(output_file, 'a') as f_out:
                    json_line = json.dumps(json_dict, ensure_ascii=False, indent=2)
                    f_out.write(json_line + "\n")
            except:
                print("fail json load")
                continue

    def generate_chat_once(self, prompt):
        messages = []
        messages.append({"role":"user", "content": prompt})
        r = self.call_azure_openai(messages) 
        return r

    def generate_chat_all(self, input_file, output_file):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file
        with open(input_file, 'r') as file:
            role_list = json.load(file)

        for item in role_list:
            role_string = json.dumps(item, ensure_ascii=False, indent=2) 
            prompt = role_string + '\n' + PROMPT_CHAT
            r = self.generate_chat_once(prompt)
       
            json_dict = {}
            json_dict["role"] = item
            json_dict["history"] = r.split('\n')
            with open(output_file, 'a') as f_out:
                json_line = json.dumps(json_dict, ensure_ascii=False, indent=2)
                f_out.write(json_line + "\n")

    def make_train_data(self, input_file, output_file):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file
	    
        output_data = []
        input_list = json.load(open(input_file, 'r'))

        for input_item in input_list: 
            # A,B,A,B,A,B...
            output_item = {}
            output_item["system"] = "基于以下角色生成对话:{}".format(json.dumps(input_item.get("role"), ensure_ascii=False))
            round_num = len(input_item["history"]) // 2
            if round_num == 0:
                continue
            output_item["prompt"] = input_item["history"][round_num*2-2] + '\n\n'		
            output_item["response"] = input_item["history"][round_num*2-1]
            output_item["history"] = []
            for i in range(round_num-1):
                output_item["history"].append([input_item["history"][i*2] + '\n\n', input_item["history"][i*2+1]])
            output_data.append(output_item)

            # B,A,B,A,B,A...
            output_item = {}
            output_item["system"] = "基于以下角色生成对话:{}".format(json.dumps(input_item.get("role"), ensure_ascii=False))
            input_item["history"] = input_item["history"][1:]
            round_num = len(input_item["history"]) // 2
            if round_num == 0:
                continue
            output_item["prompt"] = input_item["history"][round_num*2-2] + '\n\n'	
            output_item["response"] = input_item["history"][round_num*2-1]
            output_item["history"] = []
            for i in range(round_num-1):
                output_item["history"].append([input_item["history"][i*2] + '\n\n', input_item["history"][i*2+1]])
            output_data.append(output_item)


        with open(output_file, 'w', encoding="utf-8") as f_out:
	        json.dump(output_data, f_out, ensure_ascii=False, indent=4)		




if __name__ == "__main__":
    #GenerateRole().generate_role_once()
    #GenerateRole().generate_role_all("role.txt")
    #GenerateRole().generate_description_once()
    #GenerateRole().generate_description_all(output_file="role_with_descripton.json")
    #GenerateRole().generate_chat_all(input_file="role_with_descripton.json", output_file="chat_with_role.json")
    GenerateRole().make_train_data("chat_with_role.json", "gpt4_role_chat.json")
