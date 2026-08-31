import json
import random

# ===== Python 知识库随机数据池 =====
python_topics = [
    "列表推导式", "字典合并", "装饰器", "生成器", "上下文管理器",
    "类与对象", "异常处理", "文件读写", "正则表达式", "多线程",
    "异步编程", "类型注解", "虚拟环境", "pip包管理"
]
python_libs = ["Pandas", "NumPy", "Django", "Flask", "Requests", "BeautifulSoup", "Scrapy", "PyTorch", "TensorFlow"]
pep_docs = ["PEP 8", "PEP 257", "PEP 484", "PEP 585", "PEP 604"]
python_versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# ===== 五个维度的生成函数 =====

# 4.1.1 行业术语与格式适配 —— Python 术语、规范、格式
def gen_term_format(idx):
    if random.choice([True, False]):
        pep = random.choice(pep_docs)
        rule = random.choice([
            ("每行最大字符数", "79", "文档字符串", "三重引号"),
            ("缩进", "4个空格", "空格与括号", "不得混用制表符"),
        ])
        topic, detail1, detail2, detail3 = rule
        seg1 = f"《{pep}》规定：{topic}应为{detail1}。"
        seg2 = f"同时，{pep}建议{detail2}使用{detail3}。"
        question = f"请解释{pep}中关于{topic}和{detail2}的规范。"
        answer = f"根据{pep}，{topic}应使用{detail1}，{detail2}应使用{detail3}。这是Python官方编码规范。"
    else:
        lib = random.choice(python_libs)
        if lib == "Pandas":
            seg1 = "Pandas读取CSV文件使用`pd.read_csv()`，常用参数包括`sep`、`encoding`、`header`。"
            seg2 = "数据清洗时，`dropna()`用于删除缺失值，`fillna()`用于填充。"
            question = "Pandas如何读取CSV并处理缺失值？"
            answer = "使用`pd.read_csv()`读取CSV，可指定分隔符、编码等；缺失值可用`dropna()`删除或`fillna()`填充。"
        elif lib == "Django":
            seg1 = "Django的ORM通过模型类映射数据库表，使用`objects`管理器进行查询。"
            seg2 = "视图函数需返回`HttpResponse`或使用`render()`渲染模板。"
            question = "Django中模型和视图的基本用法是什么？"
            answer = "模型继承`models.Model`，通过`objects`进行数据库操作；视图接收请求，返回`HttpResponse`或渲染模板。"
        else:
            seg1 = f"{lib}是一个流行的Python库，常用于{random.choice(['数据科学','Web开发','网络爬虫'])}。"
            seg2 = f"安装{lib}使用`pip install {lib}`，导入时使用`import {lib}`。"
            question = f"如何安装和使用{lib}？"
            answer = f"使用`pip install {lib}`安装，然后在代码中用`import {lib}`导入即可使用。"
    segs = [seg1, seg2]
    seg_text = "\n".join([f"【检索片段{i+1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是Python技术助手，请使用专业术语和规范格式回答。\n{seg_text}\n问题：{question}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": answer, "role": "assistant"}]}

# 4.1.2 忠实回答（严格基于片段，含拒答）
def gen_faithful(idx):
    if idx % 5 == 0:  # 20% 拒答（无相关信息）
        segs = [
            f"Python由Guido van Rossum于{random.choice(['1991','1990'])}年创建。",
            "Python的设计哲学强调代码可读性，语法简洁。"
        ]
        q = "Python中如何实现多线程？"
        ans = "抱歉，提供的检索片段未包含关于多线程实现的信息，仅介绍了Python的创建年份和设计哲学。"
    else:
        feature = random.choice(["列表推导式", "装饰器", "生成器"])
        if feature == "列表推导式":
            seg1 = "列表推导式语法为 `[表达式 for 变量 in 可迭代对象 if 条件]`。"
            seg2 = "例如 `[x**2 for x in range(10) if x%2==0]` 生成0到8的偶数平方列表。"
            q = "请给出列表推导式的语法和示例。"
            ans = "列表推导式语法为 `[表达式 for 变量 in 可迭代对象 if 条件]`。示例：`[x**2 for x in range(10) if x%2==0]` 生成偶数平方列表。"
        elif feature == "装饰器":
            seg1 = "装饰器是一个可调用对象，用于修改函数或类的行为。"
            seg2 = "使用 `@decorator_name` 语法应用在函数定义前。"
            q = "Python装饰器是什么？如何使用？"
            ans = "装饰器是修改函数行为的可调用对象，使用 `@decorator_name` 语法放在函数定义上方。"
        else:  # 生成器
            seg1 = "生成器通过 `yield` 关键字产生值，可以保存状态。"
            seg2 = "生成器函数在每次 `next()` 调用时执行到下一个 `yield`。"
            q = "Python生成器的作用和用法是什么？"
            ans = "生成器使用 `yield` 产生值，可保存状态，适用于惰性计算。每次调用 `next()` 继续执行。"
        segs = [seg1, seg2]   # 修复：必须组合成列表
    seg_text = "\n".join([f"【检索片段{i+1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是精确回答助手，严格依据检索片段，禁止使用外部知识。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}

# 4.1.3 多片段信息整合
def gen_integrate(idx):
    seg1 = "Python使用 `try...except` 结构捕获异常。"
    seg2 = "`else` 子句在无异常时执行，`finally` 无论是否异常都会执行。"
    seg3 = "常见的内置异常有 `ValueError`、`TypeError`、`IndexError` 等。"
    segs = [seg1, seg2, seg3]
    q = "请详细说明Python异常处理的完整结构和常见异常类型。"
    ans = "异常处理使用 `try...except` 捕获异常，`else` 子句在无异常时执行，`finally` 总会执行。常见异常包括 `ValueError`（值错误）、`TypeError`（类型错误）、`IndexError`（索引错误）等。"
    seg_text = "\n".join([f"【检索片段{i+1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是信息整合助手，请合并多个片段给出完整回复。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}

# 4.1.4 证据引用与出处标注
def gen_citation(idx):
    doc = random.choice(["Python官方文档", "PEP 8", "PEP 257", "Python教程"])
    clause = random.choice(["第3章", "第4节", "附录A"])
    topic = random.choice(["命名规范", "类型注解", "虚拟环境"])
    if topic == "命名规范":
        seg1 = f"《{doc}》{clause}：函数名应使用小写字母和下划线组合（snake_case）。"
        seg2 = f"《{doc}》{clause}：类名应使用首字母大写的驼峰命名（CamelCase）。"
        q = "Python的命名规范是什么？"
        ans = f"根据《{doc}》，函数名使用snake_case，类名使用CamelCase。【来源：《{doc}》{clause}】"
    elif topic == "类型注解":
        seg1 = f"《{doc}》{clause}：类型注解使用 `变量: 类型` 语法，如 `name: str`。"
        seg2 = f"《{doc}》{clause}：函数返回值注解使用 `-> 类型`。"
        q = "Python类型注解的语法是怎样的？"
        ans = f"变量注解为 `变量: 类型`，函数返回值注解为 `-> 类型`。【来源：《{doc}》{clause}】"
    else:
        seg1 = f"《{doc}》{clause}：创建虚拟环境使用 `python -m venv venv`。"
        seg2 = f"《{doc}》{clause}：激活虚拟环境（Windows）为 `venv\\Scripts\\activate`。"
        q = "如何创建和激活Python虚拟环境？"
        ans = f"创建使用 `python -m venv venv`，激活（Windows）使用 `venv\\Scripts\\activate`。【来源：《{doc}》{clause}】"
    segs = [seg1, seg2]
    seg_text = "\n".join([f"【检索片段{i+1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是知识库助手，回答必须标注【来源：文档+条款】。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}

# 4.1.5 拒答能力（不足、冲突、部分缺失）
def gen_reject(idx):
    mode = idx % 3
    if mode == 0:  # 完全无关
        segs = ["Python是一种解释型、面向对象的编程语言。"]
        q = "Python的GIL是什么？"
        ans = "抱歉，检索片段中未提及GIL（全局解释器锁），无法回答此问题。"
    elif mode == 1:  # 信息冲突
        v1 = random.choice(["3.9", "3.10"])
        v2 = random.choice(["3.9", "3.10", "3.11"])
        while v2 == v1:
            v2 = random.choice(["3.9", "3.10", "3.11"])
        segs = [
            f"《某文档》称Python 3.10中新增了match语句。",
            f"《另一文档》称Python {v1}中已包含match语句，而{v2}未提及。"
        ]
        q = "Python哪个版本引入了match语句？"
        ans = f"检索片段存在矛盾：一说3.10引入，另一说版本{v1}已有，且{v2}未提及。请确认官方文档。"
    else:  # 部分可答
        seg1 = "使用`pip install`安装第三方包。"
        seg2 = "使用`pip freeze`列出已安装包。"
        segs = [seg1, seg2]
        q = "如何安装和卸载Python包？"
        ans = "安装使用`pip install 包名`，列出已安装包使用`pip freeze`。但检索片段未包含卸载命令，建议使用`pip uninstall`。"
    seg_text = "\n".join([f"【检索片段{i+1}】{s}" for i, s in enumerate(segs)])
    user_content = f"你是知识库助手，若信息不足或矛盾请直接拒答。\n{seg_text}\n问题：{q}"
    return {"conversations": [{"content": user_content, "role": "user"}, {"content": ans, "role": "assistant"}]}

# ===== 生成数据集（1000条，五个维度各200条）=====
def generate_dataset(total=1000):
    data = []
    generators = [gen_term_format, gen_faithful, gen_integrate, gen_citation, gen_reject]
    for i in range(total):
        data.append(generators[i % 5](i))
    return data

if __name__ == "__main__":
    dataset = generate_dataset(1000)

    # 保存为 JSON Lines 格式（每行一个 JSON 对象，不带缩进）
    with open("keywords_data_sharegpt2.jsonl", "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("✅ 已生成 1000 条 Python 知识库数据，保存为 keywords_data_sharegpt2.jsonl")
    print(f"总样本数: {len(dataset)}")