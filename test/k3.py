import json
import random

# 定义所有主题和对应的检索片段、问答对
topics = {
    "基础语法": {
        "fragments": [
            "Python使用缩进来表示代码块，通常使用4个空格。",
            "变量不需要声明类型，直接赋值即可创建。",
            "Python支持多种数据类型：整数、浮点数、字符串、列表、元组、字典、集合。"
        ],
        "qa": [
            {
                "question": "Python中的缩进规则是什么？",
                "answer": "Python使用缩进来表示代码块，通常使用4个空格，缩进必须保持一致。"
            },
            {
                "question": "Python中如何声明变量？",
                "answer": "变量不需要声明类型，直接赋值即可创建，例如 `x = 10`。"
            }
        ]
    },
    "列表操作": {
        "fragments": [
            "列表使用 `append()` 方法在末尾添加元素。",
            "列表使用 `extend()` 方法合并另一个列表。",
            "列表推导式语法为 `[表达式 for 变量 in 可迭代对象 if 条件]`。"
        ],
        "qa": [
            {
                "question": "如何向Python列表中添加元素？",
                "answer": "使用 `append()` 方法在末尾添加单个元素，使用 `extend()` 方法合并另一个列表。"
            },
            {
                "question": "列表推导式的语法是什么？",
                "answer": "列表推导式语法为 `[表达式 for 变量 in 可迭代对象 if 条件]`，可以快速生成列表。"
            }
        ]
    },
    "字典操作": {
        "fragments": [
            "字典使用 `get()` 方法安全地获取值，键不存在时返回None或默认值。",
            "字典的 `keys()` 方法返回所有键，`values()` 返回所有值，`items()` 返回所有键值对。",
            "可以使用 `in` 关键字检查字典中是否存在某个键。"
        ],
        "qa": [
            {
                "question": "Python字典中如何安全地获取值？",
                "answer": "使用 `get()` 方法安全地获取值，键不存在时返回None或指定的默认值。"
            },
            {
                "question": "如何遍历Python字典的所有键值对？",
                "answer": "使用 `items()` 方法遍历所有键值对，例如 `for key, value in dict.items():`。"
            }
        ]
    },
    "函数定义": {
        "fragments": [
            "函数使用 `def` 关键字定义，后面跟函数名和参数列表。",
            "函数可以返回多个值，实际上返回的是一个元组。",
            "默认参数值在函数定义时计算，可变参数使用 `*args` 和 `**kwargs`。"
        ],
        "qa": [
            {
                "question": "Python中如何定义一个函数？",
                "answer": "使用 `def` 关键字定义函数，格式为 `def function_name(parameters):` 后跟函数体。"
            },
            {
                "question": "Python函数如何返回多个值？",
                "answer": "函数可以返回多个值，实际上返回的是一个元组，例如 `return a, b, c`。"
            }
        ]
    },
    "异常处理": {
        "fragments": [
            "使用 `try-except` 块捕获和处理异常。",
            "可以使用 `finally` 子句执行清理操作，无论是否发生异常都会执行。",
            "使用 `raise` 关键字主动抛出异常。"
        ],
        "qa": [
            {
                "question": "Python中如何处理异常？",
                "answer": "使用 `try-except` 块捕获和处理异常，可以指定多个异常类型。"
            },
            {
                "question": "`finally` 子句的作用是什么？",
                "answer": "`finally` 子句中的代码无论是否发生异常都会执行，通常用于资源清理。"
            }
        ]
    },
    "文件操作": {
        "fragments": [
            "使用 `open()` 函数打开文件，指定模式为 'r' 读取、'w' 写入、'a' 追加。",
            "推荐使用 `with` 语句管理文件上下文，自动处理文件关闭。",
            "使用 `read()` 读取全部内容，`readline()` 逐行读取，`readlines()` 读取所有行。"
        ],
        "qa": [
            {
                "question": "Python中如何安全地打开文件？",
                "answer": "推荐使用 `with` 语句管理文件上下文，例如 `with open('file.txt', 'r') as f:`，自动处理文件关闭。"
            },
            {
                "question": "如何读取文件的所有行？",
                "answer": "使用 `readlines()` 方法读取所有行，返回一个包含每行内容的列表。"
            }
        ]
    },
    "面向对象": {
        "fragments": [
            "类使用 `class` 关键字定义，`__init__` 方法用于初始化实例。",
            "实例方法第一个参数是 `self`，指向实例本身。",
            "类变量在所有实例之间共享，实例变量属于特定实例。"
        ],
        "qa": [
            {
                "question": "Python中如何定义一个类？",
                "answer": "使用 `class` 关键字定义类，`__init__` 方法用于初始化实例属性。"
            },
            {
                "question": "类变量和实例变量有什么区别？",
                "answer": "类变量在所有实例之间共享，定义在类级别；实例变量属于特定实例，在 `__init__` 中定义。"
            }
        ]
    },
    "装饰器": {
        "fragments": [
            "装饰器是一个函数，接受另一个函数作为参数并返回一个新函数。",
            "使用 `@decorator_name` 语法糖应用装饰器。",
            "`functools.wraps` 用于保留被装饰函数的元数据。"
        ],
        "qa": [
            {
                "question": "Python装饰器是什么？",
                "answer": "装饰器是一个函数，接受另一个函数作为参数并返回一个新函数，用于在不修改原函数代码的情况下增加功能。"
            },
            {
                "question": "如何使用 `functools.wraps`？",
                "answer": "`functools.wraps` 用于保留被装饰函数的元数据（如函数名、文档字符串），在装饰器内部使用。"
            }
        ]
    },
    "生成器": {
        "fragments": [
            "生成器通过 `yield` 关键字产生值，可以保存状态。",
            "生成器函数在每次 `next()` 调用时执行到下一个 `yield`。",
            "生成器适用于惰性计算，节省内存。"
        ],
        "qa": [
            {
                "question": "Python生成器的作用和用法是什么？",
                "answer": "生成器使用 `yield` 产生值，可保存状态，适用于惰性计算。每次调用 `next()` 继续执行。"
            },
            {
                "question": "生成器与普通函数有什么区别？",
                "answer": "生成器使用 `yield` 而不是 `return`，可以暂停和恢复执行，适用于处理大数据流。"
            }
        ]
    },
    "NumPy基础": {
        "fragments": [
            "NumPy是Python科学计算的基础库，提供多维数组对象 `ndarray`。",
            "使用 `np.array()` 创建数组，`np.zeros()` 创建全零数组，`np.ones()` 创建全一数组。",
            "NumPy支持向量化操作，可以对数组进行元素级运算而无需循环。"
        ],
        "qa": [
            {
                "question": "NumPy中如何创建多维数组？",
                "answer": "使用 `np.array()` 从列表创建，`np.zeros()` 创建全零数组，`np.ones()` 创建全一数组。"
            },
            {
                "question": "NumPy向量化操作的优势是什么？",
                "answer": "向量化操作可以对数组进行元素级运算而无需循环，执行效率高，代码简洁。"
            }
        ]
    },
    "Pandas数据处理": {
        "fragments": [
            "Pandas提供 `DataFrame` 和 `Series` 两种核心数据结构。",
            "使用 `pd.read_csv()` 读取CSV文件，`df.head()` 查看前几行数据。",
            "`groupby()` 方法用于分组聚合操作，`merge()` 用于合并多个DataFrame。"
        ],
        "qa": [
            {
                "question": "Pandas中如何读取CSV文件？",
                "answer": "使用 `pd.read_csv()` 读取CSV文件，返回一个DataFrame对象，可用 `df.head()` 查看前几行。"
            },
            {
                "question": "Pandas中如何进行分组聚合？",
                "answer": "使用 `groupby()` 方法进行分组，然后调用聚合函数如 `sum()`、`mean()`、`count()` 等。"
            }
        ]
    },
    "Matplotlib可视化": {
        "fragments": [
            "Matplotlib是Python常用的数据可视化库，提供 `pyplot` 模块。",
            "使用 `plt.plot()` 绘制折线图，`plt.scatter()` 绘制散点图。",
            "`plt.show()` 显示图形，`plt.savefig()` 保存图形到文件。"
        ],
        "qa": [
            {
                "question": "Matplotlib中如何绘制折线图？",
                "answer": "使用 `plt.plot(x, y)` 绘制折线图，调用 `plt.show()` 显示图形。"
            },
            {
                "question": "如何保存Matplotlib绘制的图形？",
                "answer": "使用 `plt.savefig('filename.png')` 在 `plt.show()` 之前保存图形到文件。"
            }
        ]
    },
    "Scikit-learn机器学习": {
        "fragments": [
            "Scikit-learn提供统一的API接口：`fit()` 训练模型，`predict()` 进行预测。",
            "数据预处理使用 `StandardScaler` 进行标准化，`train_test_split` 划分数据集。",
            "常用模型包括 `LinearRegression`、`RandomForestClassifier`、`SVM` 等。"
        ],
        "qa": [
            {
                "question": "Scikit-learn的统一API接口是什么？",
                "answer": "统一API接口为 `fit()` 训练模型，`predict()` 进行预测，`score()` 评估模型性能。"
            },
            {
                "question": "如何使用Scikit-learn划分训练集和测试集？",
                "answer": "使用 `train_test_split(X, y, test_size=0.2, random_state=42)` 划分数据集。"
            }
        ]
    },
    "Flask Web开发": {
        "fragments": [
            "Flask是Python轻量级Web框架，使用 `@app.route()` 定义路由。",
            "`request` 对象用于获取HTTP请求数据，`jsonify()` 返回JSON响应。",
            "Flask应用可以通过 `app.run()` 启动开发服务器。"
        ],
        "qa": [
            {
                "question": "Flask中如何定义一个路由？",
                "answer": "使用 `@app.route('/path')` 装饰器定义路由，绑定的函数处理该路径的请求。"
            },
            {
                "question": "Flask如何返回JSON响应？",
                "answer": "使用 `jsonify()` 函数将字典转换为JSON格式的HTTP响应。"
            }
        ]
    },
    "Django框架": {
        "fragments": [
            "Django是Python全栈Web框架，遵循MTV架构模式。",
            "使用 `python manage.py runserver` 启动开发服务器。",
            "Django ORM提供对象关系映射，支持多种数据库后端。"
        ],
        "qa": [
            {
                "question": "Django遵循什么架构模式？",
                "answer": "Django遵循MTV（Model-Template-View）架构模式，类似于MVC。"
            },
            {
                "question": "如何启动Django开发服务器？",
                "answer": "在项目根目录执行 `python manage.py runserver` 启动开发服务器。"
            }
        ]
    },
    "异步编程": {
        "fragments": [
            "`async def` 定义异步函数，`await` 等待协程完成。",
            "`asyncio.run()` 是运行异步程序的入口点。",
            "异步编程适合I/O密集型任务，可以提高并发性能。"
        ],
        "qa": [
            {
                "question": "Python中如何定义异步函数？",
                "answer": "使用 `async def` 定义异步函数，内部使用 `await` 等待协程完成。"
            },
            {
                "question": "异步编程适合什么场景？",
                "answer": "异步编程适合I/O密集型任务，如网络请求、文件读写，可以提高并发性能。"
            }
        ]
    },
    "多线程与多进程": {
        "fragments": [
            "`threading` 模块用于多线程编程，`multiprocessing` 用于多进程编程。",
            "由于GIL的存在，多线程适合I/O密集型任务，多进程适合CPU密集型任务。",
            "使用 `ThreadPoolExecutor` 和 `ProcessPoolExecutor` 可以方便地管理线程池和进程池。"
        ],
        "qa": [
            {
                "question": "Python中多线程和多进程分别适合什么场景？",
                "answer": "由于GIL的存在，多线程适合I/O密集型任务，多进程适合CPU密集型任务。"
            },
            {
                "question": "如何使用Python的线程池？",
                "answer": "使用 `concurrent.futures.ThreadPoolExecutor` 创建线程池，提交任务并获取结果。"
            }
        ]
    },
    "正则表达式": {
        "fragments": [
            "`re` 模块提供正则表达式支持，`re.search()` 搜索第一个匹配项。",
            "`re.findall()` 返回所有匹配项的列表，`re.sub()` 进行替换操作。",
            "常用元字符包括 `.`、`*`、`+`、`?`、`[]`、`()` 等。"
        ],
        "qa": [
            {
                "question": "Python中如何进行正则表达式匹配？",
                "answer": "使用 `re.search(pattern, string)` 搜索第一个匹配项，`re.findall()` 返回所有匹配项。"
            },
            {
                "question": "如何用正则表达式进行替换？",
                "answer": "使用 `re.sub(pattern, replacement, string)` 进行替换操作。"
            }
        ]
    },
    "数据库操作": {
        "fragments": [
            "`sqlite3` 模块是Python内置的SQLite数据库接口。",
            "使用 `sqlite3.connect()` 连接数据库，`cursor.execute()` 执行SQL语句。",
            "`fetchone()` 获取一行结果，`fetchall()` 获取所有结果。"
        ],
        "qa": [
            {
                "question": "Python如何连接SQLite数据库？",
                "answer": "使用 `sqlite3.connect('database.db')` 连接数据库，返回连接对象。"
            },
            {
                "question": "执行SQL查询后如何获取结果？",
                "answer": "使用 `fetchone()` 获取一行结果，`fetchall()` 获取所有结果。"
            }
        ]
    },
    "日志记录": {
        "fragments": [
            "`logging` 模块提供灵活的日志记录功能。",
            "使用 `logging.basicConfig()` 配置日志级别、格式和输出位置。",
            "日志级别包括 DEBUG、INFO、WARNING、ERROR、CRITICAL。"
        ],
        "qa": [
            {
                "question": "Python中如何配置日志记录？",
                "answer": "使用 `logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')` 配置日志。"
            },
            {
                "question": "Python支持哪些日志级别？",
                "answer": "支持 DEBUG、INFO、WARNING、ERROR、CRITICAL 五个级别。"
            }
        ]
    },
    "单元测试": {
        "fragments": [
            "`unittest` 模块提供单元测试框架，测试类继承 `TestCase`。",
            "测试方法以 `test_` 开头，使用 `assertEqual`、`assertTrue` 等断言方法。",
            "使用 `python -m unittest` 运行测试。"
        ],
        "qa": [
            {
                "question": "Python中如何编写单元测试？",
                "answer": "使用 `unittest` 模块，测试类继承 `TestCase`，测试方法以 `test_` 开头。"
            },
            {
                "question": "如何运行unittest测试？",
                "answer": "在命令行执行 `python -m unittest` 运行所有测试，或指定测试文件。"
            }
        ]
    },
    "类型注解": {
        "fragments": [
            "Python类型注解使用 `:` 和 `->` 语法，如 `def func(x: int) -> str:`。",
            "`typing` 模块提供 `List`、`Dict`、`Optional`、`Union` 等类型。",
            "类型注解不会影响运行时行为，主要用于静态类型检查和代码提示。"
        ],
        "qa": [
            {
                "question": "Python中如何进行类型注解？",
                "answer": "使用 `:` 注解参数类型，`->` 注解返回值类型，例如 `def func(x: int) -> str:`。"
            },
            {
                "question": "`typing` 模块提供哪些常用类型？",
                "answer": "提供 `List`、`Dict`、`Tuple`、`Optional`、`Union`、`Any` 等类型。"
            }
        ]
    },
    "包管理": {
        "fragments": [
            "`pip` 是Python的包管理工具，用于安装和卸载第三方库。",
            "`requirements.txt` 文件列出项目依赖，使用 `pip install -r requirements.txt` 批量安装。",
            "`venv` 模块用于创建虚拟环境，隔离项目依赖。"
        ],
        "qa": [
            {
                "question": "Python中如何批量安装依赖包？",
                "answer": "将依赖包列出在 `requirements.txt` 文件中，使用 `pip install -r requirements.txt` 批量安装。"
            },
            {
                "question": "如何创建Python虚拟环境？",
                "answer": "使用 `python -m venv venv` 创建虚拟环境，激活后安装的包与全局环境隔离。"
            }
        ]
    },
    "JSON处理": {
        "fragments": [
            "`json` 模块提供JSON数据的编码和解码功能。",
            "`json.dumps()` 将Python对象转换为JSON字符串，`json.loads()` 将JSON字符串转换为Python对象。",
            "`json.dump()` 写入文件，`json.load()` 从文件读取。"
        ],
        "qa": [
            {
                "question": "Python中如何将字典转换为JSON字符串？",
                "answer": "使用 `json.dumps(dict)` 将Python字典转换为JSON字符串。"
            },
            {
                "question": "如何从JSON字符串解析为Python对象？",
                "answer": "使用 `json.loads(json_string)` 将JSON字符串解析为Python对象。"
            }
        ]
    },
    "迭代器": {
        "fragments": [
            "迭代器实现了 `__iter__()` 和 `__next__()` 方法。",
            "使用 `iter()` 获取迭代器，`next()` 获取下一个元素。",
            "当没有更多元素时，`next()` 抛出 `StopIteration` 异常。"
        ],
        "qa": [
            {
                "question": "Python中什么是迭代器？",
                "answer": "迭代器是实现了 `__iter__()` 和 `__next__()` 方法的对象，使用 `next()` 逐个获取元素。"
            },
            {
                "question": "迭代器耗尽时会怎样？",
                "answer": "当没有更多元素时，调用 `next()` 会抛出 `StopIteration` 异常。"
            }
        ]
    },
    "上下文管理器": {
        "fragments": [
            "上下文管理器使用 `with` 语句，实现了 `__enter__()` 和 `__exit__()` 方法。",
            "`contextlib.contextmanager` 装饰器可以简化上下文管理器的创建。",
            "上下文管理器用于资源管理，如文件、网络连接、锁等。"
        ],
        "qa": [
            {
                "question": "Python中上下文管理器的作用是什么？",
                "answer": "上下文管理器用于资源管理，确保资源在使用后被正确释放，如文件、网络连接、锁等。"
            },
            {
                "question": "如何使用 `contextlib` 创建上下文管理器？",
                "answer": "使用 `@contextlib.contextmanager` 装饰器，在 `yield` 前后分别执行进入和退出逻辑。"
            }
        ]
    },
    "数据类": {
        "fragments": [
            "`dataclasses` 模块提供 `@dataclass` 装饰器，自动生成 `__init__`、`__repr__` 等方法。",
            "数据类适合存储结构化数据，减少样板代码。",
            "字段可以使用 `field()` 指定默认值和元数据。"
        ],
        "qa": [
            {
                "question": "Python中数据类的作用是什么？",
                "answer": "数据类使用 `@dataclass` 装饰器，自动生成 `__init__`、`__repr__`、`__eq__` 等方法，减少样板代码。"
            },
            {
                "question": "数据类适合什么场景？",
                "answer": "数据类适合存储结构化数据，作为简单的数据容器使用。"
            }
        ]
    },
    "枚举类型": {
        "fragments": [
            "`enum` 模块提供 `Enum` 类用于定义枚举类型。",
            "枚举成员是常量，具有名称和值。",
            "枚举支持迭代和比较操作。"
        ],
        "qa": [
            {
                "question": "Python中如何定义枚举类型？",
                "answer": "继承 `enum.Enum` 类定义枚举，成员为类属性，如 `class Color(Enum): RED = 1, GREEN = 2`。"
            },
            {
                "question": "枚举成员有什么特点？",
                "answer": "枚举成员是常量，具有名称和值，支持迭代和比较操作。"
            }
        ]
    },
    "性能优化": {
        "fragments": [
            "使用 `timeit` 模块测量代码执行时间。",
            "`cProfile` 模块用于性能分析，找出代码瓶颈。",
            "列表推导和生成器表达式通常比普通循环更快。"
        ],
        "qa": [
            {
                "question": "Python中如何测量代码执行时间？",
                "answer": "使用 `timeit` 模块测量代码执行时间，或使用 `time.perf_counter()` 手动计时。"
            },
            {
                "question": "如何进行性能分析？",
                "answer": "使用 `cProfile` 模块进行性能分析，找出代码中的性能瓶颈。"
            }
        ]
    },
    "设计模式": {
        "fragments": [
            "单例模式确保一个类只有一个实例，可通过 `__new__` 或元类实现。",
            "工厂模式使用工厂方法创建对象，隐藏具体实现。",
            "观察者模式允许对象之间建立一对多的依赖关系。"
        ],
        "qa": [
            {
                "question": "Python中如何实现单例模式？",
                "answer": "可以通过重写 `__new__` 方法或使用元类实现单例模式，确保类只有一个实例。"
            },
            {
                "question": "观察者模式的作用是什么？",
                "answer": "观察者模式允许对象之间建立一对多的依赖关系，当一个对象状态变化时，所有依赖者自动收到通知。"
            }
        ]
    },
    "异步上下文管理器": {
        "fragments": [
            "异步上下文管理器实现 `__aenter__()` 和 `__aexit__()` 方法。",
            "使用 `async with` 语句管理异步上下文。",
            "`contextlib` 提供 `asynccontextmanager` 装饰器。"
        ],
        "qa": [
            {
                "question": "Python中异步上下文管理器是什么？",
                "answer": "异步上下文管理器实现了 `__aenter__()` 和 `__aexit__()` 方法，使用 `async with` 语句管理。"
            },
            {
                "question": "如何简化异步上下文管理器的创建？",
                "answer": "使用 `contextlib.asynccontextmanager` 装饰器简化异步上下文管理器的创建。"
            }
        ]
    },
    "元类": {
        "fragments": [
            "元类是类的类，控制类的创建过程。",
            "默认元类是 `type`，可以通过继承 `type` 自定义元类。",
            "元类可以修改类属性、方法，实现ORM、单例等功能。"
        ],
        "qa": [
            {
                "question": "Python中什么是元类？",
                "answer": "元类是类的类，控制类的创建过程。默认元类是 `type`，可以通过继承 `type` 自定义元类。"
            },
            {
                "question": "元类的应用场景有哪些？",
                "answer": "元类可以修改类属性、方法，实现ORM、单例模式、注册表等功能。"
            }
        ]
    },
    "描述器": {
        "fragments": [
            "描述器是实现了 `__get__`、`__set__`、`__delete__` 方法的对象。",
            "描述器用于管理属性访问，实现属性验证、延迟计算等。",
            "`property` 装饰器是描述器的内置实现。"
        ],
        "qa": [
            {
                "question": "Python中什么是描述器？",
                "answer": "描述器是实现了 `__get__`、`__set__`、`__delete__` 方法的对象，用于管理属性访问。"
            },
            {
                "question": "描述器有哪些应用场景？",
                "answer": "描述器用于实现属性验证、类型检查、延迟计算等，`property` 就是描述器的内置实现。"
            }
        ]
    },
    "信号与槽": {
        "fragments": [
            "`signal` 模块处理系统信号，如 SIGINT、SIGTERM。",
            "使用 `signal.signal()` 注册信号处理函数。",
            "信号处理函数应在主线程中注册。"
        ],
        "qa": [
            {
                "question": "Python中如何处理系统信号？",
                "answer": "使用 `signal.signal(signal.SIGINT, handler_function)` 注册信号处理函数。"
            },
            {
                "question": "信号处理函数有什么限制？",
                "answer": "信号处理函数应在主线程中注册，处理函数中应避免执行复杂操作。"
            }
        ]
    },
    "命令行参数": {
        "fragments": [
            "`sys.argv` 获取命令行参数列表。",
            "`argparse` 模块提供更强大的参数解析功能。",
            "`argparse.ArgumentParser` 支持添加位置参数、可选参数、子命令等。"
        ],
        "qa": [
            {
                "question": "Python中如何解析命令行参数？",
                "answer": "使用 `argparse` 模块创建 ArgumentParser，添加参数并调用 `parse_args()` 解析。"
            },
            {
                "question": "`sys.argv` 和 `argparse` 有什么区别？",
                "answer": "`sys.argv` 是简单的参数列表，`argparse` 提供更强大的参数解析和帮助信息生成功能。"
            }
        ]
    },
    "环境变量": {
        "fragments": [
            "`os.environ` 字典保存环境变量。",
            "使用 `os.getenv(key, default)` 安全获取环境变量。",
            "`python-dotenv` 从 `.env` 文件加载环境变量。"
        ],
        "qa": [
            {
                "question": "Python中如何获取环境变量？",
                "answer": "使用 `os.getenv(key, default)` 安全获取环境变量，或直接访问 `os.environ[key]`。"
            },
            {
                "question": "如何从文件加载环境变量？",
                "answer": "使用 `python-dotenv` 库的 `load_dotenv()` 方法从 `.env` 文件加载环境变量。"
            }
        ]
    },
    "加密与哈希": {
        "fragments": [
            "`hashlib` 模块提供 MD5、SHA1、SHA256 等哈希算法。",
            "`secrets` 模块用于生成安全随机数。",
            "`cryptography` 库提供更高级的加密功能。"
        ],
        "qa": [
            {
                "question": "Python中如何计算字符串的MD5哈希？",
                "answer": "使用 `hashlib.md5(string.encode()).hexdigest()` 计算MD5哈希值。"
            },
            {
                "question": "如何生成安全的随机数？",
                "answer": "使用 `secrets` 模块，如 `secrets.token_bytes()`、`secrets.token_hex()` 生成安全的随机数。"
            }
        ]
    },
    "网络请求": {
        "fragments": [
            "`requests` 库是发送HTTP请求的常用选择。",
            "使用 `requests.get(url)` 发送GET请求，`requests.post(url, data=data)` 发送POST请求。",
            "响应对象包含 `status_code`、`text`、`json()` 等属性和方法。"
        ],
        "qa": [
            {
                "question": "Python中如何发送HTTP GET请求？",
                "answer": "使用 `requests.get(url)` 发送GET请求，获取响应对象后调用 `response.json()` 解析JSON数据。"
            },
            {
                "question": "如何处理请求异常？",
                "answer": "使用 `try-except` 捕获 `requests.exceptions.RequestException` 处理网络异常。"
            }
        ]
    },
    "WebSocket": {
        "fragments": [
            "`websockets` 库支持WebSocket客户端和服务器。",
            "使用 `websockets.connect()` 连接WebSocket服务器。",
            "`websocket.send()` 发送消息，`websocket.recv()` 接收消息。"
        ],
        "qa": [
            {
                "question": "Python中如何连接WebSocket服务器？",
                "answer": "使用 `websockets.connect('ws://host:port')` 创建连接，然后使用 `send()` 和 `recv()` 通信。"
            },
            {
                "question": "WebSocket与HTTP有什么区别？",
                "answer": "WebSocket是双向通信协议，支持全双工通信，而HTTP是单向请求-响应协议。"
            }
        ]
    },
    "数据序列化": {
        "fragments": [
            "`pickle` 模块用于Python对象的序列化和反序列化。",
            "使用 `pickle.dump(obj, file)` 序列化到文件，`pickle.load(file)` 从文件反序列化。",
            "`pickle` 不适合跨语言传输，建议使用 JSON 或 Protocol Buffers。"
        ],
        "qa": [
            {
                "question": "Python中如何序列化对象？",
                "answer": "使用 `pickle.dump(obj, file)` 将对象序列化到文件，使用 `pickle.load(file)` 反序列化。"
            },
            {
                "question": "`pickle` 有什么局限性？",
                "answer": "`pickle` 不适合跨语言传输，存在安全风险，建议使用 JSON 或 Protocol Buffers 替代。"
            }
        ]
    },
    "时间处理": {
        "fragments": [
            "`datetime` 模块提供日期和时间处理功能。",
            "`datetime.now()` 获取当前时间，`datetime.strptime()` 解析字符串为日期对象。",
            "`datetime.strftime()` 将日期对象格式化为字符串。"
        ],
        "qa": [
            {
                "question": "Python中如何获取当前时间？",
                "answer": "使用 `datetime.datetime.now()` 获取当前日期时间对象。"
            },
            {
                "question": "如何解析日期字符串？",
                "answer": "使用 `datetime.strptime(date_string, format)` 将字符串解析为日期对象。"
            }
        ]
    },
    "数学计算": {
        "fragments": [
            "`math` 模块提供基本的数学函数，如三角函数、对数、指数等。",
            "`random` 模块用于生成随机数，如 `random.random()`、`random.randint()`。",
            "`statistics` 模块提供均值、中位数、方差等统计函数。"
        ],
        "qa": [
            {
                "question": "Python中如何生成随机整数？",
                "answer": "使用 `random.randint(a, b)` 生成 a 到 b 之间的随机整数（包含两端）。"
            },
            {
                "question": "如何计算列表的平均值？",
                "answer": "使用 `statistics.mean(list)` 或手动计算 `sum(list) / len(list)`。"
            }
        ]
    },
    "字符串处理": {
        "fragments": [
            "字符串方法包括 `split()`、`join()`、`strip()`、`replace()`、`lower()`、`upper()` 等。",
            "f-string 语法 `f\"Hello {name}\"` 用于字符串格式化。",
            "`format()` 方法支持复杂的字符串格式化。"
        ],
        "qa": [
            {
                "question": "Python中如何分割字符串？",
                "answer": "使用 `split(separator)` 方法分割字符串，返回分割后的列表。"
            },
            {
                "question": "f-string 是什么？",
                "answer": "f-string 是Python 3.6引入的字符串格式化方式，以 `f` 开头，在大括号中嵌入表达式。"
            }
        ]
    },
    "集合操作": {
        "fragments": [
            "集合是元素唯一、无序的数据结构。",
            "集合支持交集 `&`、并集 `|`、差集 `-`、对称差集 `^` 等操作。",
            "使用 `add()` 添加元素，`remove()` 删除元素。"
        ],
        "qa": [
            {
                "question": "Python中如何计算两个集合的交集？",
                "answer": "使用 `set1 & set2` 或 `set1.intersection(set2)` 计算交集。"
            },
            {
                "question": "集合和列表有什么区别？",
                "answer": "集合元素唯一且无序，列表元素可重复且有序。集合适合成员测试和去重。"
            }
        ]
    },
    "元组操作": {
        "fragments": [
            "元组是不可变的序列，使用圆括号定义。",
            "元组支持索引访问和切片操作，但不能修改元素。",
            "元组可以作为字典的键，列表不能。"
        ],
        "qa": [
            {
                "question": "Python元组和列表有什么区别？",
                "answer": "元组是不可变的，列表是可变的。元组可以作为字典的键，列表不能。"
            },
            {
                "question": "如何创建只有一个元素的元组？",
                "answer": "使用 `(element,)` 创建单元素元组，注意逗号是必需的。"
            }
        ]
    },
    "深浅拷贝": {
        "fragments": [
            "浅拷贝使用 `copy.copy()`，只复制最外层对象。",
            "深拷贝使用 `copy.deepcopy()`，递归复制所有层级。",
            "赋值操作不复制，只是引用传递。"
        ],
        "qa": [
            {
                "question": "Python中浅拷贝和深拷贝有什么区别？",
                "answer": "浅拷贝只复制最外层对象，内部元素仍是引用；深拷贝递归复制所有层级，是完全独立的对象。"
            },
            {
                "question": "如何实现浅拷贝？",
                "answer": "使用 `copy.copy(obj)` 或调用对象的 `copy()` 方法（如果存在）。"
            }
        ]
    },
    "属性管理": {
        "fragments": [
            "`@property` 装饰器将方法变为属性，支持 getter 逻辑。",
            "`@setter` 装饰器定义属性 setter 方法。",
            "`@deleter` 装饰器定义属性 deleter 方法。"
        ],
        "qa": [
            {
                "question": "Python中 `@property` 的作用是什么？",
                "answer": "`@property` 将方法变为属性，允许在访问属性时执行逻辑，支持 getter、setter、deleter。"
            },
            {
                "question": "如何定义一个只读属性？",
                "answer": "使用 `@property` 装饰器定义 getter 方法，不定义 setter 方法即可实现只读属性。"
            }
        ]
    },
    "混入类": {
        "fragments": [
            "混入类是一种多重继承的设计模式，提供可复用的功能。",
            "混入类通常以 `Mixin` 命名，不独立使用。",
            "混入类可以添加方法，但不能添加实例变量（通常）。"
        ],
        "qa": [
            {
                "question": "Python中什么是混入类？",
                "answer": "混入类是一种多重继承的设计模式，提供可复用的功能，通常以 `Mixin` 命名，不独立使用。"
            },
            {
                "question": "混入类有哪些特点？",
                "answer": "混入类提供方法复用，通常不包含实例变量，通过多重继承组合到主类中。"
            }
        ]
    },
    "抽象基类": {
        "fragments": [
            "`abc` 模块提供抽象基类支持，使用 `@abstractmethod` 定义抽象方法。",
            "抽象基类不能实例化，子类必须实现所有抽象方法。",
            "抽象基类用于定义接口规范。"
        ],
        "qa": [
            {
                "question": "Python中如何定义抽象基类？",
                "answer": "继承 `abc.ABC` 并使用 `@abc.abstractmethod` 装饰抽象方法，子类必须实现所有抽象方法。"
            },
            {
                "question": "抽象基类的作用是什么？",
                "answer": "抽象基类用于定义接口规范，确保子类实现特定的方法，不能实例化。"
            }
        ]
    },
    "泛型与类型变量": {
        "fragments": [
            "`typing.TypeVar` 定义类型变量，支持泛型编程。",
            "泛型类使用 `Generic[T]` 标记，其中 T 是类型变量。",
            "泛型函数可以接受多种类型的参数。"
        ],
        "qa": [
            {
                "question": "Python中如何定义泛型函数？",
                "answer": "使用 `typing.TypeVar` 定义类型变量，在函数参数和返回值中使用该类型变量。"
            },
            {
                "question": "泛型类如何定义？",
                "answer": "类继承 `Generic[T]`，其中 T 是类型变量，支持多种类型的实例化。"
            }
        ]
    }
}

# 扩展主题列表（重复主题变体，保证500条）
expanded_topics = []
for _ in range(5):  # 每个主题重复5次，产生不同变体
    for topic_name, topic_data in topics.items():
        # 为每个QA生成多个变体
        for qa in topic_data["qa"]:
            # 生成3个不同的检索片段组合
            fragments_variants = [
                topic_data["fragments"],
                [f"{f} (重要)" for f in topic_data["fragments"]],
                [f"关键点：{f}" for f in topic_data["fragments"]]
            ]
            for fragments in fragments_variants:
                expanded_topics.append({
                    "name": topic_name,
                    "fragments": fragments,
                    "question": qa["question"],
                    "answer": qa["answer"]
                })

# 去重并限制到500条
seen = set()
unique_items = []
for item in expanded_topics:
    key = (item["question"], tuple(item["fragments"]))
    if key not in seen and len(unique_items) < 500:
        seen.add(key)
        unique_items.append(item)

# 生成最终JSONL数据
def generate_conversation(item):
    system_prompts = [
        f"你是{random.choice(['Python技术助手', '精确回答助手', '专业Python顾问', '代码专家'])}，请使用专业术语和规范格式回答。",
        f"你是{random.choice(['严谨的Python技术专家', '代码优化顾问', 'Python教学助手'])}，严格依据检索片段回答。"
    ]
    return {
        "conversations": [
            {
                "content": f"{random.choice(system_prompts)}\n【检索片段1】{item['fragments'][0]}\n【检索片段2】{item['fragments'][1]}\n【检索片段3】{item['fragments'][2]}\n问题：{item['question']}",
                "role": "user"
            },
            {
                "content": item['answer'],
                "role": "assistant"
            }
        ]
    }

# 输出JSONL数据
with open('training_data.jsonl', 'w', encoding='utf-8') as f:
    for item in unique_items[:500]:
        json.dump(generate_conversation(item), f, ensure_ascii=False)
        f.write('\n')

print(f"已生成 {len(unique_items[:500])} 条训练数据，保存到 training_data.jsonl")