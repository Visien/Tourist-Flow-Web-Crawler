import pandas as pd
import re


def step7_replace():
    spot_replace = pd.read_csv('result_总/有效景区名录.csv')[['景区名称', '城市']].copy()
    data = pd.read_csv('result_总/result4_data.csv').copy()

    key = spot_replace.to_dict('list')['景区名称']
    value = spot_replace.to_dict('list')['城市']
    replace_dic = dict(zip(key, value))
    # print(replace_dic)
    ls_route = data.to_dict('list')['route']
    data['f'] = '0'
    for i in range(len(ls_route)):
        ls_spot = ls_route[i].split('->')
        ls_spot = list(map(lambda x: replace_dic[x], ls_spot))

        ls_ = [ls_spot[0]]
        for j in range(1, len(ls_spot)):
            if ls_spot[j] != ls_spot[j - 1]:
                ls_.append(ls_spot[j])
        ls_route[i] = '->'.join(ls_)
        data.iloc[i, 5] = len(ls_)
        # print(ls_route[i])
    for i in range(len(data)):
        data.iloc[i, 4] = ls_route[i]
    data = data[data['f'] > 1].copy()[['年份', '文章标题', '发布时间', 'url', 'route']]
    data.sort_values('route', inplace=True)
    data.to_csv('result_总/result7_data.csv', header=True, index=False)


# 统计分析
def step8_count():
    data_all = pd.read_csv('result_总/result7_data.csv').copy()
    for year in range(2018, 2022):
        data = data_all[data_all['年份'] == year].copy()

        ls_route = data.to_dict('list')['route']
        data_name = pd.read_csv('result_总/区县经纬度.csv', encoding='gbk')[['城市', '经度', '纬度']].copy()
        data_name['出度'], data_name['入度'], data_name['度数'] = 0, 0, 0
        data_name = data_name[['城市', '出度', '入度', '度数', '经度', '纬度']]
        dic = dict(zip(data_name.to_dict('list')['城市'], list(range(len(data_name)))))
        print(dic)

        for i in range(len(ls_route)):
            # print(f'{year}：{i + 1} / {len(ls_route)}')
            ls_spot = ls_route[i].split('->')

            for j in range(len(ls_spot)):
                data_name.iloc[dic[ls_spot[j]], 1] += 1
                data_name.iloc[dic[ls_spot[j]], 2] += 1
            data_name.iloc[dic[ls_spot[0]], 1] -= 1
            data_name.iloc[dic[ls_spot[-1]], 2] -= 1

        for i in range(len(data_name)):
            data_name.iloc[i, 3] = data_name.iloc[i, 1] + data_name.iloc[i, 2]
        data_name = data_name[data_name['度数'] != 0].copy()
        # print(data_name)
        data_name.sort_values('度数', ascending=False, inplace=True, ignore_index=True)
        data_name.to_csv(f'result_总/result_8/{year}出入度去零.csv', header=True, index=False)


def step9_matrix():
    data_ = pd.read_csv('result_总/result7_data.csv').copy()

    for year in range(2018, 2022):
        data = data_[data_['年份'] == year].copy()
        ls_ = pd.read_csv(f'result_总/result_8/{year}出入度去零.csv').to_dict('list')['城市']
        dic_name = dict(zip(ls_, [i for i in range(len(ls_))]))

        # 初始化矩阵
        dic_ = {ls_[0]: [0 for i in range(len(ls_))]}
        data_matrix = pd.DataFrame(dic_)
        data_matrix.index = ls_
        for i in range(1, len(ls_)):
            data_matrix[ls_[i]] = 0
        # 写入
        ls_route = data.to_dict('list')['route']
        for i in range(len(ls_route)):
            print(f'{year}：{i + 1} / {len(ls_route)} \t{ls_route[i]}')
            ls_spot = ls_route[i].split('->')
            x = dic_name[ls_spot[0]]
            for j in range(1, len(ls_spot)):
                y = dic_name[ls_spot[j]]
                data_matrix.iloc[x, y] += 1
                x = y
        ls_1 = list(data_matrix.apply(lambda x: x.sum(), axis=1))
        ls_2 = list(data_matrix.apply(lambda x: x.sum()))
        # 输出出入度到表中
        # data_matrix['出度'] = data_matrix.apply(lambda x: x.sum(), axis=1)
        # data_matrix.loc['入度'] = data_matrix.apply(lambda x: x.sum())
        ls_drop = []
        for i in range(len(data_matrix) - 1, -1, -1):
            if (ls_1[i] + ls_2[i]) < 1:
                ls_drop.append(ls_[i])
                print(ls_[i])
        data_matrix.drop(ls_drop, axis=1, inplace=True)
        data_matrix.drop(ls_drop, inplace=True)

        for i in data_matrix.columns:
            data_matrix[i] = data_matrix[i].apply(lambda x: 1 if x > 0 else 0)

        data_matrix.to_csv(f'result_总/result_9/{year}.csv', header=True, index=True)


def step10_route():
    data_ll = pd.read_csv('result_总/区县经纬度.csv', encoding='gbk').copy()
    dic_j = {data_ll.iloc[i, 0]: data_ll.iloc[i, 4] for i in range(len(data_ll))}
    dic_w = {data_ll.iloc[i, 0]: data_ll.iloc[i, 5] for i in range(len(data_ll))}
    data_all = None
    for year in range(2018, 2022):
        data_m = pd.read_csv(f'result_总/result_9/{year}.csv').copy()
        data_m.rename(columns={'Unnamed: 0': '城市'}, inplace=True)
        ls_city = data_m.to_dict('list')['城市']
        data_m.set_index('城市', inplace=True)
        route_dic = {'start_city': [], 'end_city': [], 'count': []}
        for i in range(len(data_m)):
            ls = list(data_m.iloc[i, :])
            route_dic['start_city'].extend([ls_city[i] for x in range(len(ls)) if ls[x] > 0])
            route_dic['end_city'].extend([ls_city[x] for x in range(len(ls)) if ls[x] > 0])
            route_dic['count'].extend([ls[x] for x in range(len(ls)) if ls[x] > 0])

        data_route = pd.DataFrame(route_dic)
        data_route['经度1'] = data_route['start_city'].apply(lambda x: dic_j[x])
        data_route['纬度1'] = data_route['start_city'].apply(lambda x: dic_w[x])
        data_route['经度2'] = data_route['end_city'].apply(lambda x: dic_j[x])
        data_route['纬度2'] = data_route['end_city'].apply(lambda x: dic_w[x])
        data_route = data_route[['start_city', '经度1', '纬度1', 'end_city', '经度2', '纬度2', 'count']].copy()
        # print(data_route)
        data_route.to_csv(f'result_总/result_10/{year}.csv', header=True, index=False)

        data_route['经纬度'], data_route['路线_year'] = '', year
        for i in range(len(data_route)):
            x = data_route.iloc[i, :]
            data_route.iloc[i, 7] = str([[x[1], x[2]], [x[4], x[5]]])[1:-1].replace(' ', '')
        data_route = data_route[['路线_year', 'start_city', 'end_city', '经纬度', 'count']].copy()

        if data_all is None:
            data_all = data_route
        else:
            data_all = pd.concat([data_all, data_route], ignore_index=True)
        data_route.to_excel(f'高德绘制支持/路线_year/{year}.xls', header=True, index=False, encoding='gbk')
    data_all.to_excel(f'高德绘制支持/路线表.xls', header=True, index=False, encoding='gbk')


# step7_replace()
# step8_count()
step9_matrix()
# step10_route()
