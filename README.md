This project provides support for article ‘Research on spatial pattern evolution and influencing factors of tourism flow in Chengdu-Chongqing economic circle in China’, realizes online crawling and analysis of Ctrip 's travel diary, and completes the data preprocessing required for the research.



## 执行顺序

爬虫部分

* xccq_1_get_url.py
* xccq_2.py
* xcsc_1_get_url.py
* xcsc_2.py

数据预处理部分

* 景区名录.py【手动调整】
* 样本筛选及预处理.py
* 按区聚合.py









样本筛选：①年份 ②重复  （处理景点名单：统计游记中标示，3A级景区名单）  ③不在双城经济圈(手动)  ④单个景点(在下①中处理)

样本预处理：①分析游记路线 ②构建有向线段

数据处理与分析（可视化）：①旅游流网络构建   ②旅游节点指标评价    ③“核心-边缘”模型   ④凝聚子群