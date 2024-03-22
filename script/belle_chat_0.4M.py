import sys,os
import json
import requests
from retry import retry
from src.openai_api import OpenaiApi

class BELLE_CHAT_0_4M():
    def __init__(self, ):
        self.source = "https://huggingface.co/datasets/BelleGroup/generated_chat_0.4M"
        self.data_dir = os.path.abspath(os.path.dirname(__file__))+"/../data/belle_chat_0.4M/"

    def download(self, output_file):
        url = "https://huggingface.co/datasets/BelleGroup/generated_chat_0.4M/resolve/main/generated_chat_0.4M.json?download=true"
        output_file = self.data_dir + output_file

        response = requests.get(url)
        with open(output_file, 'wb') as file:
            file.write(response.content)

    def has_colon(self, string):
        a = string.split(":")
        if len(a) > 1 and a[0].strip() and a[1].strip():
            return True
        a = string.split("：")
        if len(a) > 1 and a[0].strip() and a[1].strip():
            return True
    
        return False
    
    def process_data(self, input_file, output_file):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file

        output_data = []
        with open(input_file, 'r') as f_in:
            for line in f_in:
                item = json.loads(line)
                chat_data = item['output'].split('\n')
                new_chat_data = []

                name_list = []
                for i in range(len(chat_data)):
                    #split_token = "：" if "：" in chat_data[i] else ":"
                    try: 
                        #new_chat_data.append(chat_data[i].split(split_token)[1].strip())
                        if self.has_colon(chat_data[i]):
                            new_chat_data.append(chat_data[i])
                            
                            a = chat_data[i].split(":")
                            if len(a) == 2:
                                name_list.append(a[0])
                            b = chat_data[i].split("：")
                            if len(b) == 2:
                                name_list.append(b[0])

                    except:
                        continue
                
                name_list = list(set(name_list))
                
                instruction_list = item.get("instruction", "").split('\n')
                for j in range(len(instruction_list)):
                    save = False
                    for k in name_list:
                        if k in instruction_list[j]:
                            save = True
                            break
                    if not save:
                        instruction_list[j] = ""
                roles = "\n".join(instruction_list)
                

               
                output_item = {}
                
                output_item["roles"] = roles.strip()
                output_item["instruction"] = item["instruction"]
                output_item["history"] = new_chat_data
                
                output_data.append(output_item)
   
        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(output_data, f_out, ensure_ascii=False, indent=4)

    def generate_role(self, role, history):
        TEMPLATE = '''
        {role}
        {history}
        请根据以上人物简介和对话，总结这两个人的人设，其中人物描述包括人物的性格，职业，背景，特点等方面。格式：
        [
          {{
              "姓名："",
              "性别": "",
              "身份"："",
              "人物描述": "",
              "人物关系": ""
          }},
          {{
              "姓名"："",
              "性别": "",
              "身份"："",
              "人物描述": "",
              "人物关系": ""
          }}
        ]
        '''
        prompt = TEMPLATE.format(role=role, history=history)
        messages = []
        messages.append({"role":"user", "content": prompt})
        data = OpenaiApi().call_openai_chat_api(messages)
        return data 
    
    def generate_role_from_file(self, input_file, output_file):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file

        with open(input_file, 'r') as f_in:
            input_data = json.load(f_in)
            for item in input_data:
                try:
                    r = self.generate_role(item.get("roles", ""), "\n".join(item.get("history",[])))
                    item["norm_instruction"] = json.loads(r)
                    with open(output_file, 'a') as f_out:
                        json_line = json.dumps(item, ensure_ascii=False, indent=2)
                        f_out.write(json_line + "\n")
                except:
                    continue

    def process(self, item, results):
	    try:
	        r = self.generate_role(item.get("roles", ""), "\n".join(item.get("history",[])))
	        item["norm_instruction"] = json.loads(r)
	        results.append(item)
	    except:
	        print("fail---------:{}".format(r))
	        pass
	
	
    def generate_role_from_file_mulithread(self, input_file, output_file, concurrency=1):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file
	    
        with open(input_file, "r", encoding="utf-8") as input_file:
	        input_data = json.load(input_file)
	        for i in range(0, len(input_data), concurrency):
	            threads = []
	            results = []
	            batch = input_data[i:i + concurrency]
	
	            for item in batch:
	                t = threading.Thread(target=self.process, args=(item, results))
	                threads.append(t)
	
	            for t in threads:
	                t.start()
	
	            for t in threads:
	                t.join()
	
	            with open(output_file, "a", encoding="utf-8") as json_file:
	                for result in results:
	                    json.dump(result, json_file, ensure_ascii=False, indent=2)
	                    json_file.write('\n')

    #def adjust_pair(self, p1, p2):
        

    def make_train_data(self, input_file, output_file, adjust_pair=False):
        input_file = self.data_dir + input_file
        output_file = self.data_dir + output_file
	    
        output_data = []
        input_list = json.load(open(input_file, 'r'))

        for input_item in input_list: 
            # A,B,A,B,A,B...
            output_item = {}
            output_item["system"] = "基于以下角色生成对话:{}".format(json.dumps(input_item.get("norm_instruction"), ensure_ascii=False))
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
            output_item["system"] = "基于以下角色生成对话:{}".format(json.dumps(input_item.get("norm_instruction"), ensure_ascii=False))
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
    belle_chat = BELLE_CHAT_0_4M()
    #belle_chat.download(output_file="generated_chat_0.4M.json")
    #belle_chat.process_data(input_file="generated_chat_0.4M.json", output_file="belle_chat_0.4M_with_instruction_norm.json")
	#belle_chat.generate_role_from_file_mulithread(input_file="belle_chat_0.4M_with_instruction_norm.json", "belle_chat_0.4M_with_description.json")
    belle_chat.make_train_data(input_file="belle_chat_0.4M_with_description.json", output_file="belle_chat_with_role_26w.json")
