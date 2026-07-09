# knowledge_base_0525

#### 介绍
knowledge_base_0525掌柜智库

#### 软件架构
软件架构说明
knowledge/
├── api/                              # API 路由层
│   ├── query_router.py              # 查询服务路由 (port 8001)
│   │   ├── POST /query              # 发起查询
│   │   ├── GET /stream/{session_id} # SSE 流式获取
│   │   ├── GET /history/{session_id}# 获取历史
│   │   └── DELETE /history/...      # 清除历史
│   └── import_router.py             # 导入服务路由 (port 8000)
│       ├── POST /upload             # 上传文件
│       └── GET /status/{task_id}    # 查询任务状态
│
├── core/                             # 核心配置
│   ├── deps.py                      # 依赖注入（单例管理）
│   └── paths.py                     # 路径常量配置
│
├── processor/                        # 业务处理流程（LangGraph）
│   ├── import_processor/               # 导入流程
│   │   ├── base.py           		 # 导入节点基类
│   │   ├── config.py           	  # 导入流程配置管理
│   │   ├── exceptions.py             # 导入流程自定义异常
│   │   ├── main_graph.py           # 导入流程图定义
│   │   ├── state.py                # 状态类型定义
│   │   └── nodes/                  # 处理节点
│   │       ├── node_entry.py            # 入口节点
│   │       ├── node_pdf_to_md.py        # PDF 转 MD
│   │       ├── node_md_img.py           # 图片处理
│   │       ├── node_document_split.py   # 文档切分
│   │       ├── node_item_name_recognition.py  # 商品识别
│   │       ├── node_bge_embedding.py    # 向量嵌入
│   │       └── node_import_milvus.py    # Milvus 存储
│   │
│   └── query_processor/              	# 查询流程
│       ├── base.py           		    # 查询节点基类
│       ├── config.py           	    # 查询流程配置管理
│       ├── exceptions.py               # 查询流程自定义异常
│       ├── main_graph.py           	# 查询流程图定义
│       ├── state.py                	# 状态类型定义
│       ├── prompt.py               	# 提示词模板
│       └── nodes/                  	# 处理节点
│           ├── node_item_name_confirm.py    # 商品确认
│           ├── node_vector_search.py        # 向量检索
│           ├── node_hyde_search.py          # HyDE 检索
│           ├── node_web_search_mcp.py       # Web 搜索
│           ├── node_rrf.py                  # RRF 融合
│           ├── node_rerank.py               # 重排序
│           └── node_answer_output.py        # 答案生成
│
├── schema/                          # 数据模型定义
│   ├── query_schema.py              # 查询请求/响应模型
│   ├── upload_schema.py             # 上传响应模型
│   └── task_schema.py               # 任务状态模型
│
├── services/                        # 业务服务层
│   ├── file_import_service.py       # 文件导入服务
│   └── task_service.py              # 任务管理服务
│
├── utils/                           # 工具函数库
│   ├── milvus_utils.py              # Milvus 向量库操作
│   ├── embedding_utils.py           # 向量嵌入工具
│   ├── llm_utils.py                 # LLM 客户端封装
│   ├── reranker_utils.py            # Reranker 模型
│   ├── mongo_history_utils.py       # MongoDB 历史记录
│   ├── sse_utils.py                 # SSE 流式推送
│   ├── task_utils.py                # 任务状态管理
│   └── minio_utils.py               # MinIO 对象存储
│
├── front/                           # 前端页面
│   ├── chat.html                    # 聊天界面
│   └── import.html                  # 导入界面
│
├── test/                             # 测试代码
├── docs/                             # 文档目录
├── temp_data/                        # 临时数据目录
├── .env                              # 环境配置文件
├── .env.example                      # 环境配置文件模板
├── pyproject.toml                    # Python 依赖声明
└── uv.locl							# uv版本锁定文件

#### 安装教程
直接拉取就行了

#### 使用说明


#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
