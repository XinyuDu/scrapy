import time

import requests
import json
import json5
import pandas as pd
from datetime import datetime
from markdownify import markdownify as md

def get_toutiao():
    data_toutiao = {"request_type": "general"}
    res_toutiao = requests.post(url="http://localhost:8080/rest/api/toutiao", data=json.dumps(data_toutiao))
    articles = res_toutiao.json()['response']
    return articles

def get_relevance(articles):
    prompt = json.dumps(articles,ensure_ascii=False) + """
    请根据列表中的文章标题判断是否跟A股有关系，以json格式输出，如{"index":3, "title": "【何以中国·黄河安澜】河声丨安澜之变：答案藏在那份坚定的承诺里",
      "url": "/article/7550940140194071086/", "source": "上观新闻", "pub_time": "昨天10:12", "relevance": False, "explain": "社会新闻与股市无关"}, 其中title和url保持与列表中一致不要修改。"""

    data_yuanbao = {"prompt": prompt,"model_name": "v3", "is_search": False}
    res_yuanbao = requests.post(url="http://localhost:8080/rest/api/yuanbao", data=json.dumps(data_yuanbao))

    start_pos = res_yuanbao.json()['answer'].index('[')
    result = res_yuanbao.json()['answer'][start_pos:].replace('\n', '').replace('`', '').replace('\\', '')
    # print('='*20)
    # print(result)
    # print('='*20)
    result = json5.loads(result)
    return result

def get_page(url):
    data = {"url": url}
    res = requests.post(url="http://localhost:8080/rest/api/scrape", data=json.dumps(data))
    return res.json()

def main():
    articles = get_toutiao()
    relevance_list = get_relevance(articles)
    # time.sleep(20)
    try:
        df = pd.read_excel('toutiao.xlsx')
    except:
        df = pd.DataFrame(columns=['title', 'url', 'source', 'pub_time', 'scrape_time', 'explain'])

    ##以articles为基准结合LLM返回relevance_list构建pandas数据
    scrape_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    final_result = []
    for index, item in enumerate(relevance_list):
        if item['relevance'] and item['url']==articles[index]['url']:
            temp = articles[index]
            temp['scrape_time'] = scrape_time
            temp['explain'] = item['explain']
            final_result.append(temp)

    for item in final_result:
        url = item['url']
        if url not in df['url'].values:
            # res = get_page("https://www.toutiao.com"+item['url'])
            # print(res)
            # html_content = res['content']
            # markdown_text = md(html_content)
            # item['page_content'] = markdown_text
            new_row_df = pd.DataFrame([item])
            df = pd.concat([df, new_row_df], ignore_index=True)
    # print(df)
    df = df.drop(columns=['index'])
    df.to_excel('toutiao.xlsx', index=False)

if __name__ == "__main__":
    main()


##todo list
#1. get context of true page
#2. save to file in pandas mode