import pandas as pd
import re
import requests
import json

key = 'IHGqLBCIlvDNmry5jacufMRgPoY4Vt1a'


# <i class=""sight""></i>景区<i class=""decoration_arr""></i>
# <em class=""name"">景区。
def fun(address):
    dic = {}
    data = pd.read_csv('result_' + address + '/result2_data.csv')
    for i in range(len(data)):
        ls = re.findall(r'<i class="sight"></i>(.*?)<i class="decoration_arr"></i>', data.iloc[i, 4]) \
             + re.findall(r'<em class="name">(.*?)。', data.iloc[i, 4])
        ls = list(set(ls))
        for j in ls:
            if j in dic:
                dic[j] += 1
            else:
                dic[j] = 1
    dic_ = {'景区名': [], '标记次数': []}
    for i in dic.keys():
        dic_['景区名'].append(i)
        dic_['标记次数'].append(dic[i])
    data = pd.DataFrame(dic_).sort_values('标记次数', ignore_index=True, ascending=False)
    data.to_csv('result_' + address + '/' + address + '景区名录参考.csv', header=True, index=False)


def request_get(url):
    try:
        r = requests.get(url=url, timeout=400)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        print('请求url返回错误异常')


def get_ll(address):
    data = pd.read_csv('result_' + address + '/' + address + '景区名录参考.csv')
    data['经度'], data['纬度'] = '', ''
    data['F'] = 0
    for i in range(len(data)):
        data.iloc[i, 0] = f'{address}市' + data.iloc[i, 0]
        url = 'https://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}'.format(data.iloc[i, 0], key)
        print(f'sum:{len(data)}   i:{i}   url: {url}')
        try:
            dic = json.loads(request_get(url))
            ll = dic['result']['location']
            data.iloc[i, 2], data.iloc[i, 3] = str(ll['lng']), str(ll['lat'])
            data.iloc[i, 4] = 1
        except:
            print(f'{data.iloc[i, 0]}  False')

    data = data[data['F'] == 1].copy()[['景区名', '标记次数', '经度', '纬度']]
    data.to_csv('result_' + address + '/' + address + '景区名录参考2.csv', header=True, index=False)


def result_list():
    data = pd.read_csv('result_重庆/重庆景区名录参考2.csv').copy()
    data = pd.concat([data, pd.read_csv('result_四川/四川景区名录参考2.csv')], ignore_index=True).copy()
    ls_del = pd.read_excel('result_总/规避字.xls').copy().to_dict('list')['规避词']
    for i in range(len(data)):
        for j in ls_del:
            data.iloc[i, 0] = data.iloc[i, 0].replace(j, '')
    # 补上 重庆大学 四川大学
    data.to_csv('result_名录.csv', header=True, index=False)


# fun('重庆')
# fun('四川')
# get_ll('重庆')
# get_ll('四川')
result_list()
