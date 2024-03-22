class GenerateUrl():
    def __init__(self):
        pass
        
    def generate_url_1(self, base_url, start_index, end_index, output_file):
        all_urls = []
    	
        for i in range(start_index, end_index+1):
            url = base_url.format(i)
            all_urls.append(url)
    	
        # 将所有URL写入文件
        with open(output_file, 'w') as file:
            for url in all_urls:
                file.write(url + '\n')
        
