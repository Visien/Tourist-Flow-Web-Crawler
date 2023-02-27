import pandas as pd
import re


def year_dis(address, year_i):
    _data = pd.read_csv('result_' + address + '/携程' + str(year_i) + '.csv')
    _data = _data[['文章标题', '发布时间', 'url', '正文']].copy()
    _data['年份'] = '0'
    for i in range(len(_data)):
        # 格式化日期
        _data.iloc[i, 1] = _data.iloc[i][1].replace('.', '-')
        if _data.iloc[i, 1] != -1:
            _data.iloc[i, 4] = _data.iloc[i][1].split('-')[0]
        # 格式化正文
        _data.iloc[i, 3] = re.sub(r'\s\s+', '。', _data.iloc[i][3])

    _ls = []
    for i in range(2015, 2022):
        _ls.append(_data[_data['年份'] == str(i)])
    return _ls


def step1_year(address):
    print('address：{}'.format(address))
    ls_data = year_dis(address, 1)
    for i in range(2, 6):
        ls_temp = year_dis(address, i)
        for j in range(len(ls_data)):
            ls_data[j] = pd.concat([ls_data[j], ls_temp[j]], ignore_index=True).copy()

    result_data = ls_data[0]
    print('年份：{}    记录数量：{}'.format(2015, len(ls_data[0])))
    for i in range(1, len(ls_data)):
        print('年份：{}    记录数量：{}'.format(2015 + i, len(ls_data[i])))
        result_data = pd.concat([result_data, ls_data[i]], ignore_index=True).copy()
    result_data = result_data[['年份', '文章标题', '发布时间', 'url', '正文']]
    result_data.to_csv('result_' + address + '/result1_data.csv', header=True, index=False)
    print()


def step2_repeat(address):
    print('address：{}'.format(address))
    data = pd.read_csv('result_' + address + '/result1_data.csv')
    print('去重前数量：{}'.format(len(data)))
    data = data.sort_values('正文', ignore_index=True)
    data['重复'] = 0
    for i in range(1, len(data)):
        if data.iloc[i, 4] == data.iloc[i - 1, 4]:
            data.iloc[i, 5] = 1
    result_data = data[data['重复'] == 0]
    result_data = result_data[['年份', '文章标题', '发布时间', 'url', '正文']]
    print('去重后数量：{}'.format(len(result_data)))
    result_data.to_csv('result_' + address + '/result2_data.csv', header=True, index=False)
    print()


def step3_route():
    # 年份, 文章标题, 发布时间, url, 正文
    data = pd.read_csv('result_重庆/result2_data.csv').copy()
    data = pd.concat([data, pd.read_csv('result_四川/result2_data.csv')], ignore_index=True).copy()
    # 合并去重
    data = data.sort_values('正文', ignore_index=True)
    data['重复'] = 0
    for i in range(1, len(data)):
        if data.iloc[i, 4] == data.iloc[i - 1, 4]:
            data.iloc[i, 5] = 1
    result_data = data[data['重复'] == 0]
    data = result_data[['年份', '文章标题', '发布时间', 'url', '正文']]
    # 划分路线
    data['route'], data['有效'] = '', 0
    data['文章标题'] = data['文章标题'].apply(lambda x: x.replace(' ', ''))
    data = data.sort_values('文章标题', ignore_index=True).copy()
    data_name = pd.read_csv('result_总/result_名录.csv')[['景区名']].copy()
    data_name['标记'] = 0
    for i in range(len(data)):
        for j in range(len(data_name)):
            # 标记位置，无则为-1
            data_name.iloc[j, 1] = data.iloc[i, 4].find(data_name.iloc[j, 0])
        data_ = data_name[data_name['标记'] != -1].copy()
        if len(data_) > 1:
            # 景点数量大于1，有效 = 1
            data.iloc[i, 6] = 1
            data_ = data_.sort_values('标记', ignore_index=True).copy()
            route_ls = data_.to_dict('list')['景区名']
            mark_ls = data_.to_dict('list')['标记']
            for j in range(len(route_ls)):
                if j == len(route_ls) - 1:
                    data.iloc[i, 5] += route_ls[j] + f'({mark_ls[j]})'
                else:
                    data.iloc[i, 5] += route_ls[j] + f'({mark_ls[j]})->'
        print(f'{i} / {len(data)}   {data.iloc[i, 6]}   route:{data.iloc[i, 5]}')
    data = data[data['有效'] == 1].copy()[['年份', '文章标题', '发布时间', 'url', 'route']]
    data.to_csv('result_总/result3_data.csv', header=True, index=False)


# 景点替换（预处理）
def step4_reroute():
    data = pd.read_csv('result_总/result3_data.csv').copy()
    data_replace = pd.read_csv('result_总/spotname_replace(填充使用).csv').copy()
    ls_route = data.to_dict('list')['route']
    ls_name_except = ['成都吃客', '几何书店', '炒作大师', '嘉陵江', '解放路', '班花麻辣烫(太古里总店)', '人民大会堂',
                      '重庆钟书阁', '重庆好吃街', '玉林串串香', '水煮青春', '纯阳老酒馆', '南充市龙门古镇', '成都钟书阁',
                      '中天楼', '步行街', '草海', '瓜串串', '缘贡自贡菜·川菜馆(春熙路店)', '洞子口张老二凉粉',
                      '严太婆锅魁', '不站花胶鸡(春熙店)', '澜沧江', '通天河', '钟书阁', '蜜多商店',
                      '大院河鲜', '时代广场', '钟书阁(重庆店)', '红军桥', '长江大桥', '嘉陵江大桥', '滨江路', '重庆市博物馆', '昭化文庙']
    for i in range(len(ls_route)):
        ls_, ls_spot = ls_route[i].split('->'), []
        ls_route[i] = ''
        for j in range(len(ls_)):  # ls_[j] = 解放碑(111)
            # mark = re.findall(r'(\(\d*\))', ls_[j])[0]
            # spot = ls_[j].replace(f'{mark}', '')
            spot = re.sub(r'(\(\d*\))', '', ls_[j])
            data_replace_ = data_replace[data_replace['景区名'] == spot].copy()
            if len(data_replace_) != 0:
                spot = data_replace_.iloc[0, 1]
            # 景区在此前未出现过
            # 严格方案（考虑后续景点很有可能是前者的简写，故弃用：'观音桥步行街->步行街'）
            # if spot not in ls_spot:
            #     ls_route[i] += spot + mark + '->'
            # ls_spot.append(spot)
            # 容错方案
            if ls_route[i].find(spot) == -1 and spot not in ls_name_except:  # 严格来讲应该校对标准名录
                ls_route[i] += spot + '->'

        if ls_route[i][-2:] == '->':
            ls_route[i] = ls_route[i][:-2]
        print(f'{i + 1} / {len(data)}   现:{ls_route[i]}')
    for i in range(len(data)):
        data.iloc[i, 4] = ls_route[i]
    # 去重 去单
    # 目改后要求不去重复
    # data = data.sort_values('route', ignore_index=True).copy()
    data['重复'], data['单景点'] = 0, 0
    for i in range(1, len(data)):
        # 目改后要求不去重复
        # if data.iloc[i, 4] == data.iloc[i-1, 4]:
        #     data.iloc[i, 5] = 1
        if len(data.iloc[i, 4].split('->')) == 1:
            data.iloc[i, 6] = 1
        print(f'{i + 1} / {len(data)}   现:{data.iloc[i, 4]}')
    data = data[data['重复'] == 0][['年份', '文章标题', '发布时间', 'url', 'route', '单景点']]
    data = data[data['单景点'] == 0][['年份', '文章标题', '发布时间', 'url', 'route']]
    data.sort_values('route', inplace=True, ignore_index=True)
    print(f'去重去单后长度: {len(data)}')
    data.to_csv('result_总/result4_data.csv', header=True, index=False)


# 统计分析
def step5_count():
    data_all = pd.read_csv('result_总/result4_data.csv').copy()
    for year in range(2018, 2022):
        data = data_all[data_all['年份'] == year].copy()

        ls_route = data.to_dict('list')['route']
        # 有效景区名录中包含所有存在出入度的节点
        # data_name = pd.read_csv('result_总/result_标准景区名录.csv').copy()
        data_name = pd.read_csv('result_总/有效景区名录.csv')[['景区名称', '城市']].copy()
        data_name['入度'], data_name['出度'], data_name['度数'] = 0, 0, 0
        loss, loss_ = [], []
        for i in range(len(data)):
            ls_spot = ls_route[i].split('->')
            for j in range(len(ls_spot)):  # ls_[j] = 解放碑(111)
                ls_spot[j] = re.sub(r'(\(\d*\))', '', ls_spot[j])  # 删除括号，不做判断(调)
                for k in range(len(data_name)):
                    if data_name.iloc[k, 0] == ls_spot[j]:
                        if j == 0:
                            data_name.iloc[k, 3] += 1
                        elif j == len(ls_spot) - 1:
                            data_name.iloc[k, 2] += 1
                        else:
                            data_name.iloc[k, 3] += 1
                            data_name.iloc[k, 2] += 1
                        break
                    if k == len(data_name) - 1 and ls_spot[j] not in loss_:
                        loss_.append(ls_spot[j])
                        loss.append(str(i + 1) + ls_spot[j])
                        print(f'{i + 1} --------- {ls_spot[j]}')
            print(f'{year}\t{i + 1} / {len(data)}   {ls_route[i]}')

        for i in range(len(data_name)):
            data_name.iloc[i, 4] = data_name.iloc[i, 2] + data_name.iloc[i, 3]
        print(f'缺失：{loss}')
        data_name = data_name[data_name['度数'] != 0].copy()
        data_name.sort_values('度数', ascending=False, inplace=True, ignore_index=True)
        data_name.to_csv(f'result_总/result_5/{year}出入度去零.csv', header=True, index=False)


# 矩阵
def step6_matrix():
    data_ = pd.read_csv('result_总/result4_data.csv').copy()
    spot_name = pd.read_csv('result_总/有效景区名录.csv').copy()
    ls_ = spot_name.to_dict('list')['景区名称']
    dic_name = dict(zip(ls_, [i for i in range(len(ls_))]))
    for f in range(2018, 2022):
        data = data_[data_['年份'] == f].copy()
        # 初始化矩阵
        data_matrix = pd.DataFrame([[0 for i in ls_] for j in ls_])
        data_matrix.columns = ls_
        data_matrix.index = ls_
        # print(data_matrix)
        # 写入
        ls_route = data.to_dict('list')['route']
        for i in ls_route:
            ls_spot = i.split('->')
            x = dic_name[ls_spot[0]]
            for j in range(1, len(ls_spot)):
                y = dic_name[ls_spot[j]]
                data_matrix.iloc[x, y] += 1
                x = y
        ls_1 = list(data_matrix.apply(lambda x: x.sum(), axis=1))
        ls_2 = list(data_matrix.apply(lambda x: x.sum()))
        # # 输出出入度到表中
        # data_matrix['出度'] = data_matrix.apply(lambda x: x.sum(), axis=1)
        # data_matrix.loc['入度'] = data_matrix.apply(lambda x: x.sum())

        ls_drop = []
        for i in range(len(data_matrix) - 1, -1, -1):
            # 筛选出入度
            if (ls_1[i] + ls_2[i]) < 1:
                ls_drop.append(ls_[i])
                print(ls_[i])
        data_matrix.drop(ls_drop, axis=1, inplace=True)
        data_matrix.drop(ls_drop, inplace=True)

        for i in data_matrix.columns:
            data_matrix[i] = data_matrix[i].apply(lambda x: 1 if x > 0 else 0)

        data_matrix.to_csv(f'result_总/result_6/{f}.csv', header=True, index=True)


# step1_year('重庆')
# step1_year('四川')
# step2_repeat('重庆')
# step2_repeat('四川')
# step3_route()
# step4_reroute()
# step5_count()
step6_matrix()
