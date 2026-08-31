import json
import random

# ===== 客服场景随机数据池 =====
order_ids = ["OD" + str(random.randint(100000, 999999)) for _ in range(50)]
phone_prefix = ["138", "159", "186", "137", "189", "136"]
product_names = ["智能手环", "蓝牙耳机", "家用摄像头", "无线路由器", "智能音箱", "扫地机器人", "充电宝"]
addresses = ["北京市朝阳区XX路1号", "上海市浦东新区YY街2号", "广州市天河区ZZ路3号", "深圳市南山区AA路4号"]
refund_reasons = ["商品有质量问题", "不想要了", "物流太慢", "颜色发错了", "尺寸不合适"]
complaint_reasons = ["客服态度差", "处理超时", "承诺未兑现", "反复转接"]
statuses = ["已下单", "已发货", "运输中", "已签收", "已退款", "已取消"]


# ===== 辅助函数 =====
def random_order():
    return random.choice(order_ids)


def random_phone():
    return random.choice(phone_prefix) + str(random.randint(10000000, 99999999))


def random_product():
    return random.choice(product_names)


def random_status():
    return random.choice(statuses)


# ===== 4.3.1 用户意图识别能力 =====
def gen_intent_recognition(idx):
    intents = [
        {"label": "查询订单", "q": f"我的订单{random_order()}到哪里了？",
         "a": "已识别您的意图为【查询订单】，正在为您查询订单状态。"},
        {"label": "申请退款", "q": f"我要退款，订单号{random_order()}",
         "a": "已识别您的意图为【申请退款】，请告知退款原因。"},
        {"label": "修改信息", "q": f"帮我改一下收货地址，订单{random_order()}",
         "a": "已识别您的意图为【修改信息】，请提供新的收货地址。"},
        {"label": "投诉升级", "q": f"我等了三天都没人处理，我要投诉！",
         "a": "已识别您的意图为【投诉升级】，非常抱歉给您带来不便，正在为您转接投诉专员。"},
        {"label": "转人工", "q": "转人工客服", "a": "已识别您的意图为【转人工】，正在为您连接人工客服，请稍候。"},
        {"label": "混合意图", "q": f"我要退货退款，顺便查一下另一个订单{random_order()}的物流",
         "a": "已识别您的意图为【申请退款】和【查询订单】两个。请问您优先处理哪个？"}
    ]
    sample = random.choice(intents)
    user_content = f"【客服场景】用户消息：{sample['q']}"
    return {
        "conversations": [
            {"content": user_content, "role": "user"},
            {"content": sample['a'], "role": "assistant"}
        ]
    }


# ===== 4.3.2 槽位信息抽取能力 =====
def gen_slot_extraction(idx):
    # 槽位抽取：从用户消息中提取关键信息，缺失时追问
    scenarios = [
        {
            "q": f"我要退货，订单{random_order()}，手机号{random_phone()}",
            "a": "已从您的消息中提取以下槽位：订单号、手机号。当前缺失【退货原因】，请补充。"
        },
        {
            "q": f"改地址，新地址：{random.choice(addresses)}",
            "a": "已提取【新地址】槽位，但缺少【订单号】，请提供要修改的订单号。"
        },
        {
            "q": f"投诉，订单{random_order()}，问题：{random.choice(complaint_reasons)}",
            "a": "已提取【订单号】和【投诉原因】。槽位完整，正在为您提交投诉工单。"
        },
        {
            "q": f"我买了个{random_product()}，有问题",
            "a": "已提取【商品名】，但缺少【订单号】和【具体问题】，请补充以便进一步处理。"
        }
    ]
    sample = random.choice(scenarios)
    user_content = f"【客服场景】用户消息：{sample['q']}"
    return {
        "conversations": [
            {"content": user_content, "role": "user"},
            {"content": sample['a'], "role": "assistant"}
        ]
    }


# ===== 4.3.3 澄清问题生成能力 =====
def gen_clarification(idx):
    # 用户消息模糊，需要生成具体澄清问题
    scenarios = [
        {"q": "我要退货", "a": "请问您的订单号是多少？只有确认订单号后才能为您办理退货。"},
        {"q": "我的东西坏了", "a": "请问是哪个商品出现了问题？能否提供订单号？"},
        {"q": "改一下", "a": "请问您需要修改什么信息？是收货地址、联系电话还是商品型号？"},
        {"q": "退款", "a": "请问您要退款的订单号是多少？另外告知一下退款原因。"},
        {"q": "投诉", "a": "请问您要投诉的是哪个订单？具体遇到了什么问题？"}
    ]
    sample = random.choice(scenarios)
    user_content = f"【客服场景】用户消息：{sample['q']}"
    return {
        "conversations": [
            {"content": user_content, "role": "user"},
            {"content": sample['a'], "role": "assistant"}
        ]
    }


# ===== 4.3.4 多轮流程状态管理能力 =====
def gen_state_management(idx):
    # 模拟 3~4 轮对话，体现上下文保持和状态推进
    order = random_order()
    phone = random_phone()
    product = random_product()
    address = random.choice(addresses)

    # 场景：完整退款流程
    if idx % 3 == 0:
        turns = [
            {"role": "user", "content": f"我要申请退款，订单{order}"},
            {"role": "assistant", "content": f"已收到订单号{order}，请告知退款原因。"},
            {"role": "user", "content": f"原因是{random.choice(refund_reasons)}"},
            {"role": "assistant", "content": f"好的，您已提供订单号和退款原因，正在为您提交退款申请，预计1-3个工作日到账。"}
        ]
    # 场景：修改地址（需验证身份）
    elif idx % 3 == 1:
        turns = [
            {"role": "user", "content": f"帮我改一下订单{order}的地址"},
            {"role": "assistant", "content": f"请提供新地址和您的手机号尾号4位以验证身份。"},
            {"role": "user", "content": f"新地址：{address}，手机尾号{phone[-4:]}"},
            {"role": "assistant", "content": f"验证通过，已将订单{order}的地址修改为：{address}，请确认。"}
        ]
    # 场景：复杂查询（状态未确认）
    else:
        turns = [
            {"role": "user", "content": f"我的订单{order}怎么还没到？"},
            {"role": "assistant", "content": f"正在查询订单{order}，当前状态为{random_status()}，请稍候。"},
            {"role": "user", "content": "具体什么时间能到？"},
            {"role": "assistant",
             "content": f"根据物流信息，预计{random.choice(['明天', '后天', '今天下午'])}送达，请您耐心等待。"}
        ]

    return {"conversations": turns}


# ===== 4.3.5 异常处理与人工升级能力 =====
def gen_escalation(idx):
    # 包含情绪识别、异常冲突、转人工，并保留上下文给人工
    order = random_order()
    mode = idx % 4

    if mode == 0:  # 情绪升级（愤怒）
        turns = [
            {"role": "user", "content": f"我订单{order}都一个礼拜了还没收到！你们是干什么吃的！"},
            {"role": "assistant",
             "content": f"非常理解您的急切心情，先别生气。我正在为您查看订单{order}，但系统显示该订单已签收。是否可能是家人代收了？如果确认未收到，我将为您转接人工专员处理，并将当前查询上下文一并移交给他们。"}
        ]
    elif mode == 1:  # 信息冲突（地址不一致）
        turns = [
            {"role": "user", "content": f"改地址，订单{order}，新地址是{random.choice(addresses)}"},
            {"role": "assistant",
             "content": f"检测到异常：该订单{order}已进入派送环节，无法在线修改地址。建议您直接联系快递员，或我为您转接人工客服协调。您当前提供的上下文（订单号、新地址）已记录。"}
        ]
    elif mode == 2:  # 规则不可处理（商品超出售后）
        turns = [
            {"role": "user", "content": f"我买了{random_product()}，用了两年现在坏了，能退吗？"},
            {"role": "assistant",
             "content": f"非常抱歉，您该订单已超出退换货期限（签收超过7天/15天），线上流程无法处理。为了避免您白费时间，我直接为您转接人工客服，您有权限申请特殊处理。请稍候。"}
        ]
    else:  # 用户坚持要求人工
        turns = [
            {"role": "user", "content": "不要跟我讲规则，我就要找人工！"},
            {"role": "assistant",
             "content": "好的，马上为您转接人工。为了让人工客服更快帮到您，我已将您本次对话的诉求（要求人工处理）和账号基本信息打包。正在转接，预计等待1分钟。"}
        ]

    return {"conversations": turns}


# ===== 生成主函数 =====
def generate_customer_service_dataset(total=1000):
    data = []
    generators = [
        gen_intent_recognition,  # 4.3.1
        gen_slot_extraction,  # 4.3.2
        gen_clarification,  # 4.3.3
        gen_state_management,  # 4.3.4
        gen_escalation  # 4.3.5
    ]

    for i in range(total):
        # 均匀分配五个维度，每个维度 200 条
        gen_func = generators[i % 5]
        data.append(gen_func(i))

    return data


if __name__ == "__main__":
    dataset = generate_customer_service_dataset(1000)

    # 以 JSON Lines 格式保存，每行一个 JSON 对象
    output_path = "keywords_data_sharegpt.jsonl"  # 建议使用 .jsonl 或 .ndjson 扩展名
    with open(output_path, "w", encoding="utf-8") as f:
        for item in dataset:
            line = json.dumps(item, ensure_ascii=False)  # 不转义中文，紧凑输出
            f.write(line + "\n")

    print(f"✅ 客服数据集生成完成！共 {len(dataset)} 条样本")
    print(f"📁 保存路径: {output_path}")
    print("📊 维度分布: 每个维度 200 条（意图识别、槽位抽取、澄清、多轮管理、异常升级）")