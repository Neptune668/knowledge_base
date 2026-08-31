import json
import random

# ---------- 主题库（包含40+主题，每个主题3-5个QA，共约200个原始QA） ----------
TOPICS = {
    "基础语法": {
        "frag": ["Python使用4个空格缩进", "变量无需声明类型", "支持数字、字符串、列表、元组、字典、集合"],
        "qa": [
            {"q": "Python的缩进规则是什么？", "a": "使用4个空格表示代码块，必须一致"},
            {"q": "如何声明变量？", "a": "直接赋值即可，如 x=10"},
            {"q": "Python有哪些基本数据类型？", "a": "整数、浮点、字符串、列表、元组、字典、集合"}
        ]
    },
    "列表操作": {
        "frag": ["append()添加元素", "extend()合并列表", "列表推导式 [expr for x in iterable if cond]"],
        "qa": [
            {"q": "如何添加元素到列表？", "a": "使用 append() 单个，extend() 合并另一个列表"},
            {"q": "列表推导式的语法？", "a": "[表达式 for 变量 in 可迭代对象 if 条件]"},
            {"q": "如何合并两个列表？", "a": "使用 extend() 或 + 运算"}
        ]
    },
    "字典操作": {
        "frag": ["get()安全获取值", "keys(), values(), items()", "in 检查键是否存在"],
        "qa": [
            {"q": "如何安全获取字典值？", "a": "使用 get(key, default)，不存在返回None或默认值"},
            {"q": "如何遍历键值对？", "a": "使用 items()，如 for k,v in dict.items()"},
            {"q": "如何检查键存在？", "a": "使用 in 关键字，如 if key in dict"}
        ]
    },
    "函数定义": {
        "frag": ["def定义函数", "可返回多个值（元组）", "默认参数和 *args/**kwargs"],
        "qa": [
            {"q": "如何定义函数？", "a": "def func(params): 后跟函数体"},
            {"q": "如何返回多个值？", "a": "直接 return a,b,c，返回元组"},
            {"q": "*args和**kwargs是什么？", "a": "*args接收位置参数，**kwargs接收关键字参数"}
        ]
    },
    "异常处理": {
        "frag": ["try-except捕获异常", "finally清理", "raise抛出异常"],
        "qa": [
            {"q": "如何处理异常？", "a": "使用 try-except 捕获，可指定异常类型"},
            {"q": "finally的作用？", "a": "无论是否异常都会执行，用于资源释放"},
            {"q": "如何抛出异常？", "a": "使用 raise Exception('msg')"}
        ]
    },
    "文件操作": {
        "frag": ["open()模式 r/w/a", "with语句自动关闭", "read/readline/readlines"],
        "qa": [
            {"q": "如何安全打开文件？", "a": "使用 with open('f','r') as f:"},
            {"q": "如何读取所有行？", "a": "使用 readlines() 返回列表"},
            {"q": "如何逐行读取大文件？", "a": "使用 for line in f: 迭代"}
        ]
    },
    "面向对象": {
        "frag": ["class定义类", "__init__初始化", "self指实例", "类变量与实例变量"],
        "qa": [
            {"q": "如何定义一个类？", "a": "class MyClass: 及 __init__ 方法"},
            {"q": "类变量和实例变量区别？", "a": "类变量共享，实例变量属于对象"},
            {"q": "self参数是什么？", "a": "指向实例自身，访问属性和方法"}
        ]
    },
    "装饰器": {
        "frag": ["装饰器是函数，接收函数返回函数", "@语法糖", "functools.wraps保留元数据"],
        "qa": [
            {"q": "装饰器是什么？", "a": "在不修改原函数下增加功能，返回新函数"},
            {"q": "@decorator的作用？", "a": "等价于 func = decorator(func)"},
            {"q": "如何保留原函数名称？", "a": "使用 @wraps(func) 装饰内部函数"}
        ]
    },
    "生成器": {
        "frag": ["yield产生值", "next()继续执行", "惰性计算"],
        "qa": [
            {"q": "生成器的用法？", "a": "使用 yield，每次 next() 继续执行"},
            {"q": "生成器与普通函数区别？", "a": "生成器使用 yield，可暂停，适合大数据"},
            {"q": "如何创建生成器？", "a": "函数内含 yield 或生成器表达式 (x for x in range(10))"}
        ]
    },
    "NumPy": {
        "frag": ["ndarray多维数组", "np.array(), np.zeros(), np.ones()", "向量化操作"],
        "qa": [
            {"q": "如何创建NumPy数组？", "a": "np.array([1,2,3]) 或 np.zeros((2,3))"},
            {"q": "向量化操作的优势？", "a": "无需循环，高效简洁"},
            {"q": "如何获取数组形状？", "a": "使用 .shape 属性"}
        ]
    },
    "Pandas": {
        "frag": ["DataFrame和Series", "pd.read_csv()", "groupby()和merge()"],
        "qa": [
            {"q": "如何读取CSV？", "a": "pd.read_csv('file.csv')"},
            {"q": "如何进行分组聚合？", "a": "df.groupby('col').sum()"},
            {"q": "如何合并DataFrame？", "a": "pd.merge(df1, df2, on='key')"}
        ]
    },
    "Matplotlib": {
        "frag": ["pyplot模块", "plot()折线, scatter()散点", "show()和savefig()"],
        "qa": [
            {"q": "如何绘制折线图？", "a": "plt.plot(x,y); plt.show()"},
            {"q": "如何保存图片？", "a": "plt.savefig('plot.png') 在show之前"},
            {"q": "如何绘制散点图？", "a": "plt.scatter(x,y)"}
        ]
    },
    "Scikit-learn": {
        "frag": ["fit()训练, predict()预测", "train_test_split划分", "StandardScaler标准化"],
        "qa": [
            {"q": "统一API是什么？", "a": "fit训练，predict预测，score评估"},
            {"q": "如何划分训练测试集？", "a": "train_test_split(X, y, test_size=0.2)"},
            {"q": "如何标准化数据？", "a": "使用 StandardScaler().fit_transform(X)"}
        ]
    },
    "Flask": {
        "frag": ["@app.route()路由", "request获取请求", "jsonify返回JSON"],
        "qa": [
            {"q": "如何定义路由？", "a": "@app.route('/path') 装饰函数"},
            {"q": "如何返回JSON？", "a": "使用 jsonify({'key':'value'})"},
            {"q": "如何获取POST数据？", "a": "使用 request.json 或 request.form"}
        ]
    },
    "Django": {
        "frag": ["MTV架构", "manage.py runserver", "ORM映射"],
        "qa": [
            {"q": "Django的架构模式？", "a": "MTV（Model-Template-View）"},
            {"q": "如何启动开发服务器？", "a": "python manage.py runserver"},
            {"q": "Django ORM的作用？", "a": "对象关系映射，操作数据库无需SQL"}
        ]
    },
    "异步编程": {
        "frag": ["async def定义", "await等待", "asyncio.run()入口"],
        "qa": [
            {"q": "如何定义异步函数？", "a": "async def func():"},
            {"q": "如何运行异步程序？", "a": "asyncio.run(main())"},
            {"q": "异步适合什么场景？", "a": "I/O密集型任务，提高并发"}
        ]
    },
    "多线程/多进程": {
        "frag": ["threading多线程", "multiprocessing多进程", "GIL限制"],
        "qa": [
            {"q": "多线程和多进程适用场景？", "a": "多线程I/O密集型，多进程CPU密集型"},
            {"q": "如何创建线程池？", "a": "ThreadPoolExecutor(max_workers=4)"},
            {"q": "GIL是什么？", "a": "全局解释器锁，限制同一时刻只能执行一个线程"}
        ]
    },
    "正则表达式": {
        "frag": ["re模块", "search() findall() sub()", "元字符 . * + ? [] ()"],
        "qa": [
            {"q": "如何搜索匹配？", "a": "re.search(pattern, string)"},
            {"q": "如何找到所有匹配？", "a": "re.findall(pattern, string)"},
            {"q": "如何进行替换？", "a": "re.sub(pattern, repl, string)"}
        ]
    },
    "数据库(sqlite3)": {
        "frag": ["sqlite3.connect()", "cursor.execute()", "fetchone/fetchall"],
        "qa": [
            {"q": "如何连接SQLite？", "a": "sqlite3.connect('db.db')"},
            {"q": "如何执行查询？", "a": "cursor.execute('SELECT *')"},
            {"q": "如何获取一行结果？", "a": "fetchone() 或 fetchall()"}
        ]
    },
    "日志(logging)": {
        "frag": ["logging.basicConfig()", "级别 DEBUG INFO WARNING ERROR CRITICAL", "格式配置"],
        "qa": [
            {"q": "如何配置日志？", "a": "logging.basicConfig(level=logging.INFO)"},
            {"q": "有哪些日志级别？", "a": "DEBUG, INFO, WARNING, ERROR, CRITICAL"},
            {"q": "如何输出日志到文件？", "a": "filename参数指定文件"}
        ]
    },
    "单元测试(unittest)": {
        "frag": ["unittest.TestCase", "test_开头方法", "assertEqual/assertTrue"],
        "qa": [
            {"q": "如何编写单元测试？", "a": "继承TestCase，方法以test_开头"},
            {"q": "如何运行测试？", "a": "python -m unittest 文件名"},
            {"q": "断言方法有哪些？", "a": "assertEqual, assertTrue, assertRaises 等"}
        ]
    },
    "类型注解": {
        "frag": ["参数:类型, ->返回类型", "typing.List, Dict, Optional, Union", "不影响运行"],
        "qa": [
            {"q": "如何添加类型注解？", "a": "def func(x:int)->str:"},
            {"q": "typing提供哪些类型？", "a": "List, Dict, Optional, Union, Any"},
            {"q": "类型注解会影响性能吗？", "a": "不会，仅用于静态检查"}
        ]
    },
    "包管理(pip/venv)": {
        "frag": ["pip install", "requirements.txt", "venv虚拟环境"],
        "qa": [
            {"q": "如何批量安装依赖？", "a": "pip install -r requirements.txt"},
            {"q": "如何创建虚拟环境？", "a": "python -m venv venv"},
            {"q": "如何导出依赖列表？", "a": "pip freeze > requirements.txt"}
        ]
    },
    "JSON处理": {
        "frag": ["json.dumps()/loads()", "json.dump()/load()", "处理文件"],
        "qa": [
            {"q": "如何将字典转JSON字符串？", "a": "json.dumps(dict)"},
            {"q": "如何解析JSON字符串？", "a": "json.loads(json_str)"},
            {"q": "如何读写JSON文件？", "a": "json.dump(obj, file) 和 json.load(file)"}
        ]
    },
    "迭代器": {
        "frag": ["__iter__和__next__", "iter()和next()", "StopIteration"],
        "qa": [
            {"q": "什么是迭代器？", "a": "实现__iter__和__next__的对象"},
            {"q": "如何获取迭代器？", "a": "使用 iter(可迭代对象)"},
            {"q": "迭代完成时发生什么？", "a": "抛出 StopIteration 异常"}
        ]
    },
    "上下文管理器": {
        "frag": ["with语句", "__enter__和__exit__", "contextlib.contextmanager"],
        "qa": [
            {"q": "上下文管理器的作用？", "a": "资源管理，确保释放"},
            {"q": "如何用contextlib简化？", "a": "用 @contextmanager 装饰，yield前后写逻辑"},
            {"q": "with语句如何工作？", "a": "进入时调用__enter__，退出调用__exit__"}
        ]
    },
    "数据类(dataclasses)": {
        "frag": ["@dataclass自动生成__init__等", "减少样板代码", "field()指定默认值"],
        "qa": [
            {"q": "数据类的作用？", "a": "自动生成__init__, __repr__, __eq__等"},
            {"q": "如何使用？", "a": "from dataclasses import dataclass; @dataclass class C:"},
            {"q": "如何设置默认值？", "a": "在字段后直接赋值或使用 field(default=...)"}
        ]
    },
    "枚举(enum)": {
        "frag": ["Enum类", "成员常量", "支持迭代"],
        "qa": [
            {"q": "如何定义枚举？", "a": "class Color(Enum): RED=1, GREEN=2"},
            {"q": "枚举成员有什么特点？", "a": "是常量，有名和值"},
            {"q": "如何遍历枚举？", "a": "for member in Color: 迭代"}
        ]
    },
    "性能优化": {
        "frag": ["timeit测量时间", "cProfile性能分析", "列表推导比循环快"],
        "qa": [
            {"q": "如何测量代码执行时间？", "a": "使用 timeit.timeit('code')"},
            {"q": "如何找到性能瓶颈？", "a": "使用 cProfile.run('func()')"},
            {"q": "为什么列表推导更快？", "a": "内部优化，减少Python字节码执行"}
        ]
    },
    "设计模式(单例)": {
        "frag": ["单例模式", "__new__控制实例", "元类实现"],
        "qa": [
            {"q": "如何实现单例？", "a": "重写__new__或使用元类"},
            {"q": "单例的好处？", "a": "确保全局只有一个实例"},
            {"q": "工厂模式是什么？", "a": "通过工厂方法创建对象，隐藏具体类"}
        ]
    },
    "异步上下文管理器": {
        "frag": ["__aenter__和__aexit__", "async with", "asynccontextmanager"],
        "qa": [
            {"q": "异步上下文管理器是什么？", "a": "实现__aenter__和__aexit__的对象"},
            {"q": "如何使用？", "a": "async with 语句"},
            {"q": "如何简化创建？", "a": "使用 @asynccontextmanager 装饰"}
        ]
    },
    "元类": {
        "frag": ["元类是类的类", "type是默认元类", "可修改类创建"],
        "qa": [
            {"q": "什么是元类？", "a": "类的类，控制类创建过程"},
            {"q": "如何自定义元类？", "a": "继承 type 并重写 __new__"},
            {"q": "元类的应用？", "a": "ORM、单例、注册表等"}
        ]
    },
    "描述器": {
        "frag": ["__get__, __set__, __delete__", "管理属性访问", "property是描述器"],
        "qa": [
            {"q": "什么是描述器？", "a": "实现上述三个方法的对象，用于属性管理"},
            {"q": "描述器应用场景？", "a": "属性验证、延迟计算、类型检查"},
            {"q": "property如何实现？", "a": "它是内置的描述器，提供getter/setter"}
        ]
    },
    "命令行参数": {
        "frag": ["sys.argv列表", "argparse模块", "添加位置/可选参数"],
        "qa": [
            {"q": "如何解析命令行参数？", "a": "使用 argparse.ArgumentParser"},
            {"q": "如何获取所有参数？", "a": "args = parser.parse_args()"},
            {"q": "sys.argv和argparse区别？", "a": "sys.argv简单，argparse功能强大"}
        ]
    },
    "环境变量": {
        "frag": ["os.environ", "os.getenv()", "python-dotenv加载.env"],
        "qa": [
            {"q": "如何获取环境变量？", "a": "os.getenv('KEY', default)"},
            {"q": "如何加载.env文件？", "a": "使用 load_dotenv() 从 python-dotenv"},
            {"q": "如何设置环境变量？", "a": "os.environ['KEY']='value'"}
        ]
    },
    "哈希(hashlib)": {
        "frag": ["hashlib.md5/sha256", "hexdigest()", "secrets安全随机"],
        "qa": [
            {"q": "如何计算MD5？", "a": "hashlib.md5(s.encode()).hexdigest()"},
            {"q": "如何生成安全随机数？", "a": "secrets.token_hex(16)"},
            {"q": "SHA256用法？", "a": "hashlib.sha256(s.encode()).hexdigest()"}
        ]
    },
    "网络请求(requests)": {
        "frag": ["requests.get()/post()", "响应对象有status_code, text, json()", "捕获异常"],
        "qa": [
            {"q": "如何发送GET请求？", "a": "requests.get(url)"},
            {"q": "如何处理响应JSON？", "a": "response.json()"},
            {"q": "如何处理异常？", "a": "try-except requests.exceptions.RequestException"}
        ]
    },
    "WebSocket": {
        "frag": ["websockets.connect()", "send()和recv()", "双向通信"],
        "qa": [
            {"q": "如何连接WebSocket？", "a": "websockets.connect('ws://host')"},
            {"q": "如何发送消息？", "a": "使用 send(message)"},
            {"q": "WebSocket与HTTP不同？", "a": "WebSocket是全双工长连接，HTTP是单向请求"}
        ]
    },
    "序列化(pickle)": {
        "frag": ["pickle.dump/load", "对象序列化", "不安全，不适合跨语言"],
        "qa": [
            {"q": "如何序列化对象？", "a": "pickle.dump(obj, file)"},
            {"q": "如何反序列化？", "a": "pickle.load(file)"},
            {"q": "pickle有什么缺点？", "a": "不安全，且不能跨语言"}
        ]
    },
    "时间处理(datetime)": {
        "frag": ["datetime.now()", "strptime解析", "strftime格式化"],
        "qa": [
            {"q": "如何获取当前时间？", "a": "datetime.datetime.now()"},
            {"q": "如何解析日期字符串？", "a": "datetime.strptime('2023-01-01','%Y-%m-%d')"},
            {"q": "如何格式化输出？", "a": "dt.strftime('%Y-%m-%d')"}
        ]
    },
    "数学(math/random)": {
        "frag": ["math三角函数", "random.randint()", "statistics.mean()"],
        "qa": [
            {"q": "如何生成随机整数？", "a": "random.randint(1,10)"},
            {"q": "如何计算平均值？", "a": "statistics.mean(list) 或 sum/list"},
            {"q": "math模块常用函数？", "a": "sin, cos, log, exp, sqrt等"}
        ]
    },
    "字符串处理": {
        "frag": ["split, join, strip, replace", "f-string格式化", "format()方法"],
        "qa": [
            {"q": "如何分割字符串？", "a": "s.split(',') 返回列表"},
            {"q": "f-string如何使用？", "a": "f'Hello {name}'"},
            {"q": "如何去除首尾空格？", "a": "strip() 方法"}
        ]
    },
    "集合操作": {
        "frag": ["集合无序唯一", "交集& 并集| 差集-", "add()和remove()"],
        "qa": [
            {"q": "如何求交集？", "a": "set1 & set2 或 intersection()"},
            {"q": "集合与列表区别？", "a": "集合唯一无序，列表可重复有序"},
            {"q": "如何添加元素？", "a": "使用 add() 方法"}
        ]
    },
    "元组操作": {
        "frag": ["元组不可变", "索引和切片", "可作为字典键"],
        "qa": [
            {"q": "元组和列表区别？", "a": "元组不可变，列表可变；元组可作键"},
            {"q": "如何创建单元素元组？", "a": "(1,) 注意逗号"},
            {"q": "元组支持哪些操作？", "a": "索引、切片、相加、乘"}
        ]
    },
    "深浅拷贝": {
        "frag": ["copy.copy()浅拷贝", "copy.deepcopy()深拷贝", "赋值是引用"],
        "qa": [
            {"q": "浅拷贝和深拷贝区别？", "a": "浅拷贝只复制外层，深拷贝递归复制所有"},
            {"q": "如何实现深拷贝？", "a": "copy.deepcopy(obj)"},
            {"q": "赋值操作是拷贝吗？", "a": "不是，只是引用传递"}
        ]
    },
    "属性管理(property)": {
        "frag": ["@property getter", "@setter设置", "@deleter删除"],
        "qa": [
            {"q": "@property的作用？", "a": "将方法变为属性，可加入逻辑"},
            {"q": "如何创建只读属性？", "a": "只定义getter，不定义setter"},
            {"q": "如何定义setter？", "a": "@属性名.setter 装饰方法"}
        ]
    },
    "混入类(Mixin)": {
        "frag": ["Mixin提供复用功能", "多重继承", "不独立实例化"],
        "qa": [
            {"q": "什么是Mixin？", "a": "混入类，通过多重继承提供功能复用"},
            {"q": "Mixin命名惯例？", "a": "以Mixin结尾，如 LoggingMixin"},
            {"q": "Mixin可以包含实例变量吗？", "a": "通常不包含，只提供方法"}
        ]
    },
    "抽象基类(abc)": {
        "frag": ["ABC和abstractmethod", "不能实例化", "定义接口"],
        "qa": [
            {"q": "如何定义抽象基类？", "a": "继承abc.ABC，用@abstractmethod装饰方法"},
            {"q": "抽象基类的作用？", "a": "强制子类实现特定方法，定义接口"},
            {"q": "抽象类可以实例化吗？", "a": "不能，必须由子类实现全部抽象方法"}
        ]
    },
    "泛型(TypeVar)": {
        "frag": ["TypeVar定义类型变量", "Generic[T]", "泛型函数"],
        "qa": [
            {"q": "如何定义泛型函数？", "a": "使用 TypeVar 定义类型变量，用于参数和返回"},
            {"q": "如何定义泛型类？", "a": "class MyClass(Generic[T]):"},
            {"q": "泛型的好处？", "a": "提高类型安全，支持多种类型"}
        ]
    }
}

# ---------- 生成样本的函数 ----------
def make_sample(topic, qa_item, system_prompt):
    frags = topic["frag"]
    return {
        "conversations": [
            {
                "content": f"{system_prompt}\n【检索片段1】{frags[0]}\n【检索片段2】{frags[1]}\n【检索片段3】{frags[2]}\n问题：{qa_item['q']}",
                "role": "user"
            },
            {"content": qa_item['a'], "role": "assistant"}
        ]
    }

# 系统提示（随机选用，增加多样性）
PROMPTS = [
    "你是Python技术助手，请使用专业术语和规范格式回答。",
    "你是精确回答助手，严格依据检索片段，禁止使用外部知识。",
    "你是严谨的Python技术专家，请基于检索片段给出准确解答。",
    "你是代码专家，用简洁专业的语言回答Python问题。"
]

# ---------- 收集所有样本 ----------
all_samples = []
for topic_name, topic_data in TOPICS.items():
    for qa in topic_data["qa"]:
        # 每个QA搭配2种不同提示（共4种，但取2种以减少重复，可选更多）
        for sp in PROMPTS[:2]:
            all_samples.append(make_sample(topic_data, qa, sp))

# 随机打乱
random.seed(2026)
random.shuffle(all_samples)

# 划分训练集（70%）和测试集（30%）
split = int(len(all_samples) * 0.7)
train_set = all_samples[:split]
test_set = all_samples[split:]

# 保存为JSONL
with open("train.jsonl", "w", encoding="utf-8") as f:
    for s in train_set:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

with open("test.jsonl", "w", encoding="utf-8") as f:
    for s in test_set:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

print(f"✅ 训练集：{len(train_set)} 条，测试集：{len(test_set)} 条")
print(f"📁 文件已保存：train.jsonl 和 test.jsonl")