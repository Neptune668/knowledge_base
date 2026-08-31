import json
import random

# ----- 随机数据池 -----
companies = ["XX科技", "云创智能", "华信集团", "数通网络", "恒达制造", "智远信息", "天工能源", "星辉医疗"]
policies = ["员工考勤管理制度", "差旅费用管理办法", "采购审批制度", "信息安全保密规定", "项目立项管理规范",
            "产品售后政策", "薪酬福利体系", "固定资产管理办法"]
cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
departments = ["人事部", "财务部", "技术部", "市场部", "运营部", "研发中心", "客服部"]


# ----- 4.1.1 行业术语与格式适配（修正版）-----
def gen_term_format(idx):
    # 随机选择类型
    if random.choice([True, False]):
        # 制度解释类型
        advance_days = random.choice(["3个", "5个"])
        approver = random.choice(["直属上级", "部门经理"])
        max_days = random.choice(["15", "20"])
        seg1 = f"《{random.choice(policies)}》规定：事假需提前{advance_days}工作日申请，经{approver}批准。"
        seg2 = f"事假全年累计不得超过{max_days}个工作日。"
        question = "员工请事假有什么规定？"
        answer = f"依据规定，请事假需提前{advance_days}工作日申请，经{approver}批准；全年累计不得超过{max_days}个工作日。"
    else:
        # 产品参数类型
        protocol = random.choice(["Wi-Fi 6", "5G NR", "千兆以太网"])
        rate = random.choice(["9.6Gbps", "2.5Gbps", "10Gbps"])
        port_num = random.choice(["4", "8"])
        port_type = random.choice(["千兆LAN", "万兆光"])
        feature = random.choice(["Mesh组网", "VLAN隔离", "堆叠"])
        seg1 = f"{random.choice(companies)}推出的{random.choice(['X系列网关', '智能终端', '高速交换机'])}，支持{protocol}，速率高达{rate}。"
        seg2 = f"设备配备{port_num}个{port_type}接口，支持{feature}功能。"
        question = "该设备的主要技术参数是什么？"
        answer = f"设备支持{protocol}协议，传输速率{rate}，接口配置为{port_num}个{port_type}，支持{feature}。"

    seg_text = "\n".join([f"【检索片段{i + 1}】{s}" for i, s in enumerate([seg1, seg2])])
    user_content = f"你是专业的业务助手，请使用规范术语和标准格式回答。\n{seg_text}\n问题：{question}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": answer, "role": "assistant"}]}


# ----- 其他四个维度（保持不变，已确保无 format 错位）-----
def gen_faithful(idx):
    if idx % 5 == 0:
        segs = [
            f"{random.choice(companies)}成立于{random.choice(['2010', '2015', '2008'])}年，主营{random.choice(['智能硬件', '软件开发'])}。",
            f"员工总数约{random.choice(['300', '500', '800'])}人。"
        ]
        q = "创始人是谁？"
        ans = "基于提供的检索片段，我无法找到关于创始人的信息。片段中仅包含成立时间和主营业务，缺少创始人姓名。"
    else:
        profit = random.randint(1, 5)
        segs = [
            f"Q3营收{random.randint(10, 50)}亿元，同比增长{random.randint(10, 30)}%。",
            f"净利润为{profit}亿元。"
        ]
        q = "Q3净利润是多少？"
        ans = f"根据检索片段，Q3净利润为{profit}亿元。"
    seg_text = "\n".join([f"【检索片段{i + 1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是精确回答助手，严格依据检索片段，禁止使用外部知识。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}


def gen_integrate(idx):
    city_level = random.choice(["一线", "二线", "三线"])
    limit = random.choice(["600", "400", "300"])
    breakfast = random.choice(["20", "30"])
    lunch_dinner = random.choice(["40", "50"])
    traffic = random.choice(["实报实销", "限额80元/天"])
    segs = [
        f"出差住宿标准：{city_level}城市限额{limit}元/天。",
        f"餐补标准：早餐{breakfast}元，午晚餐各{lunch_dinner}元，凭票报销。",
        f"交通补贴：市内{traffic}，长途需提前审批。"
    ]
    q = "请完整说明出差的住宿、餐饮及交通补贴标准。"
    ans = f"住宿：{city_level}城市{limit}元/天；餐补：早餐{breakfast}元，午晚餐各{lunch_dinner}元；交通：{traffic}。"
    seg_text = "\n".join([f"【检索片段{i + 1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是信息整合助手，请合并多个片段给出完整回复。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}


def gen_citation(idx):
    doc = random.choice(policies)
    clause1 = f"第{random.randint(2, 15)}条"
    clause2 = f"第{random.randint(1, 5)}条"
    min_len = random.choice(["8", "10"])
    change_days = random.choice(["60", "90"])
    segs = [
        f"《{doc}》{clause1}：密码长度至少{min_len}位，含大小写及特殊字符。",
        f"《{doc}》{clause2}：密码每{change_days}天更换一次。"
    ]
    q = "密码管理的要求是什么？"
    ans = f"1. 密码长度不少于{min_len}位，包含大小写和特殊字符【来源：《{doc}》{clause1}】；2. 每{change_days}天更换一次【来源：《{doc}》{clause2}】。"
    seg_text = "\n".join([f"【检索片段{i + 1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是知识库助手，回答必须标注【来源：文档+条款】。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}


def gen_reject(idx):
    mode = idx % 3
    if mode == 0:
        segs = [f"公司{random.choice(['获得高新认证', '新增15项专利', '搬迁至新园区'])}。"]
        q = "年度销售额是多少？"
        ans = "抱歉，检索片段中未包含年度销售额数据，无法回答此问题。"
    elif mode == 1:
        v1 = random.choice(["12", "24"])
        v2 = random.choice(["12", "24", "36"])
        while v2 == v1:
            v2 = random.choice(["12", "24", "36"])
        doc = random.choice(policies)
        segs = [
            f"《{doc}》V2.0：保修期为{v1}个月。",
            f"《{doc}》V3.0：保修期为{v2}个月。"
        ]
        q = "产品保修期是多久？"
        ans = f"抱歉，检索片段存在矛盾（{v1}个月 vs {v2}个月），请确认最新有效版本。"
    else:
        material = random.choice(["建议书+可行性报告", "预算表+风险分析"])
        flow = "项目经理→部门负责人→PMO"
        segs = [
            f"立项需提交{material}。",
            f"审批流程为：{flow}。"
        ]
        q = "立项材料、审批流程及审批时限分别是什么？"
        ans = f"材料：{material}；流程：{flow}。但检索片段中未提及审批时限，建议咨询PMO。"
    seg_text = "\n".join([f"【检索片段{i + 1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是知识库助手，若信息不足或矛盾请直接拒答。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}


# ----- 主循环生成 1000 条 -----
def generate_dataset(total=1000):
    data = []
    generators = [gen_term_format, gen_faithful, gen_integrate, gen_citation, gen_reject]
    for i in range(total):
        # 使用 i%5 确保五个维度数量均等（各200条）
        data.append(generators[i % 5](i))
    return data


if __name__ == "__main__":
    dataset = generate_dataset(1000)
    # 您可修改路径，例如 r"D:/data/knowledge_base_1000.json"
    with open("knowledge_base_1000.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print("✅ 已生成 1000 条数据，保存为 knowledge_base_1000.json")
    print(f"总样本数: {len(dataset)}")