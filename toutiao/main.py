import time
import requests
import json
import json5
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def get_toutiao():
    data_toutiao = {"request_type": "general"}
    res_toutiao = requests.post(url="http://localhost:8080/rest/api/toutiao", data=json.dumps(data_toutiao))
    try:
        articles = res_toutiao.json()['response']
        print('get_toutiao api articles')
        print(articles)
        return articles
    except Exception as e:
        print('get toutiao api error')
        print(e)
        print(res_toutiao.json())


def get_relevance(articles):
    prompt = json.dumps(articles,ensure_ascii=False) + """
    请根据列表中的文章标题判断是否跟A股有关系，以json格式输出，如{"index":3, "title": "【何以中国·黄河安澜】河声丨安澜之变：答案藏在那份坚定的承诺里",
      "url": "/article/7550940140194071086/", "source": "上观新闻", "pub_time": "昨天10:12", "relevance": False, "explain": "社会新闻与股市无关"}, 其中title和url保持与列表中一致不要修改。"""

    data_yuanbao = {"prompt": prompt,"model_name": "v3", "is_search": False}
    res_yuanbao = requests.post(url="http://localhost:8080/rest/api/yuanbao", data=json.dumps(data_yuanbao))

    start_pos = res_yuanbao.json()['answer'].index('[')
    result = res_yuanbao.json()['answer'][start_pos:].replace('\n', '').replace('`', '').replace('\\', '')#.replace('“', '').replace('”', '')
    # print('='*20)
    # print(result)
    # print('='*20)
    try:
        result = json5.loads(result)
    except Exception as e:
        print('get yuanbao api error')
        print(e)
        print(res_yuanbao.json())
        print('='*20)
        print(result)
        print('='*20)
    return result


def get_page(url):
    data = {"url": url}
    res = requests.post(url="http://localhost:8080/rest/api/scrape", data=json.dumps(data))
    return res.json()

def parse_relative_time(rel_str, scrape_time):
    """将相对时间字符串转换为绝对时间"""
    print("parse_relative_time api")
    print(rel_str, scrape_time)
    print("parse_relative_time api")
    try:
        # 处理空值
        if pd.isna(rel_str):
            return np.nan

        rel_str = rel_str.strip()

        # 处理“刚刚”的情况
        if rel_str == "刚刚":
            return scrape_time

        # 解析数字和单位
        print('parse_relative_time==')
        print(rel_str)
        print('parse_relative_time==')
        if "分钟" in rel_str:
            num = int(''.join(filter(str.isdigit, rel_str)))
            delta = timedelta(minutes=num)
            print("minute")
        elif "小时" in rel_str:
            num = int(''.join(filter(str.isdigit, rel_str)))
            delta = timedelta(hours=num)
            print("hour")
        elif "天" in rel_str:
            num = int(''.join(filter(str.isdigit, rel_str)))
            delta = timedelta(days=num)
            print("day")
        else:
            print("else")
            return np.nan  # 未知格式

        return pd.to_datetime(scrape_time) - delta
    except Exception as e:
        print("except:", str(e))
        return np.nan  # 解析失败

def main():
    articles = get_toutiao()
    for article in articles:
        article['title'] = article['title'].strip().replace('“', '').replace('”', '')

    time.sleep(1)
    relevance_list = get_relevance(articles)
    # time.sleep(20)
    try:
        df = pd.read_excel('toutiao.xlsx')
    except:
        df = pd.DataFrame(columns=['title', 'url', 'source', 'pub_time', 'scrape_time', 'explain', 'abs_pub_time'])

    ##以articles为基准结合LLM返回relevance_list构建pandas数据
    scrape_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    final_result = []
    for index, item in enumerate(relevance_list):
        if item['relevance'] and item['url']==articles[index]['url'] and "天" not in articles[index]['pub_time'] and "月" not in articles[index]['pub_time']: ##相关且llm生成的url与原始url一致且发布时间不含‘天’字
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
            item['abs_pub_time'] = parse_relative_time(item["pub_time"], item["scrape_time"])
            print("main print item====")
            print(item)
            print("main print item====")
            new_row_df = pd.DataFrame([item])
            df = pd.concat([df, new_row_df], ignore_index=True)
    # print(df)
    try:
        df = df.drop(columns=['index'])
    except:
        pass

    df.to_excel('toutiao.xlsx', index=False)
    ##过滤，留下最近7天的数据
    # df['scrape_time'] = pd.to_datetime(df['scrape_time'])
    # now = pd.Timestamp.now()
    # seven_days_ago = now - pd.Timedelta(days=7)
    # filtered_df = df[df['scrape_time'] > seven_days_ago]
    # filtered_df.to_excel('toutiao.xlsx', index=False)

if __name__ == "__main__":
    main()
