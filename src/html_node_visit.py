from bs4 import BeautifulSoup, NavigableString

VISIT_ERROR = -1
VISIT_NORMAL = 1
VISIT_FINISH = 2
VISIT_SKIP_CHILD = 3

def html_node_visit(html_node, start_visit, finish_visit, result):
    ret = VISIT_NORMAL
    
    node = html_node

    while(node):
        local_ret = VISIT_NORMAL
        if start_visit:
            local_ret = start_visit(node, result)
            if local_ret == VISIT_ERROR or local_ret == VISIT_FINISH:
                ret = local_ret
                return ret

        if isinstance(node, NavigableString):
            first_child = None
        else:
            first_child = next(node.children, None)
        if first_child and local_ret != VISIT_SKIP_CHILD:
            node = first_child
            continue

        if finish_visit:
            local_ret = finish_visit(node, result)
            if local_ret == VISIT_ERROR or local_ret == VISIT_FINISH:
                ret = local_ret
                return ret

        if node == html_node:
            return ret

        if node.nextSibling:
            node = node.nextSibling
            continue

        while(True):
            node = node.parent
            if not node:
                break

            if finish_visit:
                local_ret = finish_visit(node, result)
                if local_ret == VISIT_ERROR or local_ret == VISIT_FINISH:
                    ret = local_ret
                    return ret

            if node == html_node:
                return ret

            if node.nextSibling:
                node = node.nextSibling
                break




if __name__ == "__main__":
    #html_content = "<html><body><div><p>Example</p></div></body></html>"
    html_content = open('3164.html', 'r').read()
   
    #html_content = "<aaa><ccc>333</ccc>111<bbb>222</bbb></aaa>"
    soup = BeautifulSoup(html_content, 'html.parser')
    #soup = BeautifulSoup(html_content, 'lxml')
    result_data = None
    
    def start_visit(node, result):
        #if node.name in ["script", "style"]:
        #    return VISIT_SKIP_CHILD

        if isinstance(node, NavigableString):
            print("Visiting start--:", node.name)
            print("Visiting text:{}--".format(node))
            if node == "==记住==":
                print("33333")
                return VISIT_FINISH
        else:
            print("Visiting start:", node.name)
        return VISIT_NORMAL

    def finish_visit(node, result):
        print("Visiting finish:", node.name)
        return VISIT_NORMAL
  

    #start_node = soup.select("//div[@class='articleList'][2]/div[1]")
    start_node = soup
    start_node = soup.select("div.articleList:nth-of-type(2) > div:nth-of-type(1)")
    start_node = start_node[0]

    html_node_visit(start_node, start_visit, finish_visit, result_data)

