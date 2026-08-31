# -*- coding: utf-8 -*-
"""
知识库问答微调数据生成器

对齐 trimming.md 的 5 项目标能力：
  1) 行业术语与回答格式适配   -> 参数/清单/安全/保养/认证 等格式化回答
  2) 检索内容忠实回答         -> 故障排查逐条来自资料；部分问题明确"资料未提及"
  3) 多片段信息整合           -> 部署条件整合、跨型号对比、条款 + 保修政策联合判断
  4) 证据引用与出处标注       -> 所有可回答样本均带 [n] 引用与【参考依据】
  5) 资料不足时的拒答         -> 无召回 / 弱相关 / 冲突召回 / 型号不明

用户侧 prompt 完全复用线上 ANSWER_PROMPT 模板，上下文格式与
g_node_answer_output._format_reranked_docs 的输出保持一致，保证训练与推理同构。

用法： python generate.py [--out kb_finetune_1000.jsonl] [--seed 20250831]
"""

import argparse
import hashlib
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import corpus as KB  # noqa: E402

# 与线上保持一致的提示词模板（导入失败时回退为同内容副本）
try:
    from processor.query_processor.prompt.answer_prompt import ANSWER_PROMPT
except Exception:  # pragma: no cover
    ANSWER_PROMPT = """你是一个智能助手，请根据参考内容回答用户的问题。
要求：
1 尽量基于【参考内容】和【用户问题】 作答，不要编造不存在的事实。
2 如果用户的问题需要通过图片来辅助说明（例如：外观、结构、接线、示意图等）,图片只能来自于本地切片文本中的图片，请在答案最后追加一个独立的图片区块，格式严格如下：
【图片】
<图片URL1>
<图片URL2>
（每行一个URL；如果没有合适图片则不要输出【图片】区块）

【参考内容】
{context}

【历史对话】
{history}

【相关商品/实体】
{item_names}

【用户问题】
{question}

请回答："""


# ==================================================================== 基础工具
_CJK_SPACE = re.compile(r"(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])")


def tidy(text):
    """去掉中文之间因模板占位符残留的多余空格"""
    return _CJK_SPACE.sub("", text).strip()


def pick(rng, seq):
    return rng.choice(list(seq))


def pick_n(rng, seq, n):
    seq = list(seq)
    rng.shuffle(seq)
    return seq[:n]


def _content(chunk):
    text = "【%s】\n%s" % (chunk["sec"], chunk["text"])
    if chunk["img_url"]:
        text += "\n![%s示意图](%s)" % (chunk["sec"], chunk["img_url"])
    return text


def make_doc(chunk, score, source="local", url=None, chunk_id=None, title=None):
    return {
        "chunk_id": chunk_id or chunk["chunk_id"],
        "source": source,
        "url": url,
        "title": title or chunk["doc"],
        "score": score,
        "content": _content(chunk) if chunk.get("text") else chunk["content"],
        "doc": chunk["doc"],
        "sec": chunk["sec"],
        "img_url": chunk["img_url"] if chunk.get("text") else None,
    }


def render_context(docs):
    """与 g_node_answer_output._format_reranked_docs 输出格式一致"""
    blocks = []
    for idx, d in enumerate(docs, start=1):
        tags = [
            "[%d]" % idx,
            "[source=%s]" % d["source"],
            "[chunk_id=%s]" % d["chunk_id"],
            "[url=%s]" % d["url"],
            "[title=%s]" % d["title"],
            "[score=%.4f]" % float(d["score"]),
        ]
        blocks.append(" ".join(tags) + "\n" + d["content"])
    return "\n\n".join(blocks)


def render_history(history):
    label = {"user": "用户", "assistant": "助手"}
    return "\n".join("%s: %s" % (label[m["role"]], m["text"]) for m in history)


def build(question, docs, lines, capability, item_names=None, history=None, citations=True):
    context = render_context(docs) if docs else "无参考内容"
    history_str = render_history(history) if history else "暂无历史对话"
    item_str = "、".join(item_names) if item_names else "无指定商品"

    # 仅对正文做空白整理，引用与图片区块保持原样，避免破坏条款名等措辞
    answer = tidy("\n".join(lines).strip())
    if citations and docs:
        cites = "\n".join("[%d]《%s》· %s" % (i, d["doc"], d["sec"])
                          for i, d in enumerate(docs, 1))
        answer += "\n\n【参考依据】\n" + cites
    # 拒答类样本不输出图片区块（未依据资料作答，不应附资料图片）
    images = [d["img_url"] for d in docs if d.get("img_url")] if citations else []
    if images:
        answer += "\n\n【图片】\n" + "\n".join(images)

    question = tidy(question)
    user = ANSWER_PROMPT.format(context=context, history=history_str,
                                item_names=item_str, question=question)
    return {
        "capability": capability,
        "question": question,
        "item": item_names or [],
        "record": {"conversations": [
            {"content": user, "role": "user"},
            {"content": answer, "role": "assistant"},
        ]},
    }


# ================================================================= 问题模板
# 数值/规格型参数用"是多少"
PARAM_Q_NUM = [
    "{short} 的{key}是多少？",
    "{short} 的{key}参数是多少？",
    "请告诉我{short}的{key}",
    "麻烦查一下{short}的{key}",
    "请问{short}的{key}是多少？",
    "我想确认一下{short}的{key}",
    "{short} 的{key}能说明一下吗？",
    "客户问：{short}的{key}是多少？",
    "帮忙查{short}的{key}",
    "{short} 的{key}能到多少？",
]

# 部件/条款型参数用"是什么"，避免出现"处理器是多少"这类不通顺的问法
PARAM_Q_TEXT = [
    "{short} 的{key}是什么？",
    "{short} 用的是什么{key}？",
    "{short} 的{key}是什么规格？",
    "请说明{short}的{key}",
    "麻烦查一下{short}的{key}",
    "客户问：{short}的{key}是什么？",
    "我想确认一下{short}的{key}",
    "{short} 的{key}能说明一下吗？",
    "帮忙查{short}的{key}",
    "{short} 的{key}具体怎么规定的？",
]

COMPONENT_KEYS = {
    "处理器", "显示屏", "摄像头", "电源", "电源适配器", "类型", "显示技术", "光源类型",
    "碎纸方式", "控制方式", "打印方式", "面板", "外壳材质", "散热方式", "预装系统",
    "内存插槽", "电池配置", "支持接口", "可粉碎物", "适用材料", "内存规格要求",
    "是否支持 ECC", "禁止安装位置", "禁止使用场所", "禁止事项", "扩展注意事项",
    "服务覆盖说明", "不属于免费保修的情形", "保修期起算", "无发票处理", "整机保修",
    "上门服务", "现场服务", "通风要求", "水平度要求", "安装间距", "推荐负载率",
    "进风温度告警", "其他接口", "机身按键", "显示区", "调节键", "功能键", "模式切换",
    "开机默认档位", "主界面显示", "参数设置路径", "配方管理", "手动调试", "急停与回零",
    "面板布局", "温度设定方法", "进入参数菜单", "专用入口", "进纸口位置", "纸屑桶位置",
    "功能开关", "状态指示灯", "电源开关位置", "前面板", "显示屏可查看内容", "输出插座",
    "通信接口", "存储扩展位", "前置接口", "后置接口", "电源接口位置", "机身左侧",
    "机身背面", "机身底部", "视频输入", "视频输出", "控制接口", "打印自检页方法",
    "易损件", "其他耗材", "常备易损件", "换新政策", "增值服务", "延保政策",
    "商用保养建议", "选型建议", "碳带规格", "碳带宽度要求", "卷芯内径",
    "打印头保修", "主要部件保修", "易损件保修", "伺服电机与控制系统保修", "加热管保修",
    "液晶面板保修", "电源适配器保修", "微晶面板保修", "刀具组件保修", "蓄电池保修",
    "服务时效", "退换货", "禁止安装场所", "搬运要求", "机房要求",
}

PARAM_Q2 = [
    "{short} 的{k1}和{k2}分别是多少？",
    "请说明{short}的{k1}与{k2}",
    "{short} 的{k1}、{k2}这两个参数是多少？",
    "客户想了解{short}的{k1}和{k2}，怎么答复？",
    "{short}的{k1}和{k2}各是多少？",
]

STEP_Q = [
    "{short} {topic}的操作步骤是什么？",
    "请说明{short}的{topic}操作步骤",
    "{short} 的{topic}要怎么做？",
    "{short} 的{topic}具体怎么操作？",
    "如何完成{short}的{topic}？",
    "{short} 的{topic}流程是怎样的？",
    "麻烦给一份{short} 的{topic}操作指引",
    "客户问{short}的{topic}怎么做，怎么回答？",
]

FAULT_Q = [
    "{short} {symptom}怎么办？",
    "{short} 出现{symptom}的情况，怎么排查？",
    "{short} {symptom}，可能是什么原因？",
    "客户反馈{short} {symptom}，怎么处理？",
    "{short} {symptom}要怎么解决？",
    "{short} {symptom}的排查步骤是什么？",
]

SAFETY_Q = [
    "{short} 有哪些安全注意事项？",
    "操作 {short} 需要注意哪些安全事项？",
    "{short} 的安全规范是什么？",
    "使用 {short} 时怎样避免安全事故？",
    "客户问{short}有什么安全注意事项？",
    "{short} 作业前需要了解哪些安全要求？",
    "{short} 的安全操作要求有哪些？",
    "给一份{short}的安全提示",
]

MAINT_Q = [
    "{short} 怎么保养？",
    "{short} 的维护保养要求是什么？",
    "{short} 的保养周期是多久？",
    "{short} 日常如何维护？",
    "客户问{short}平时的保养怎么做？",
    "{short} 需要定期做哪些维护工作？",
]

PACKING_Q = [
    "{short} 包装箱里有哪些东西？",
    "{short} 标配包含哪些配件？",
    "{short} 的开箱清单是什么？",
    "{short} 随机附带的配件有哪些？",
    "买 {short} 都会给哪些东西？",
    "{short} 到货后应核对哪些物品？",
]

CONSUMABLE_Q = [
    "{short} 推荐使用什么耗材？",
    "{short} 的耗材规格是什么？",
    "{short} 适用的{key}是多少？",
    "{short} 需要配什么规格的耗材？",
    "客户问{short}用什么耗材合适？",
    "{short} 的易损件有哪些？",
]

ENV_Q = [
    "{short} 的安装环境有什么要求？",
    "{short} 对温度和湿度有什么要求？",
    "{short} 的使用环境要求是什么？",
    "安装 {short} 需要注意哪些环境条件？",
    "{short} 能不能放在普通办公室使用？",
    "客户场地要装{short}，环境条件怎么确认？",
]

CERT_Q = [
    "{short} 有哪些认证？",
    "{short} 通过了什么认证？",
    "{short} 是否符合节能与环保要求？",
    "{short} 的合规认证情况是什么？",
    "客户要认证资料，{short}有哪些？",
]

INTEGRATION_Q = [
    "部署 {short} 需要满足哪些条件？",
    "安装 {short} 前要做哪些准备？",
    "{short} 的上架条件有哪些？",
    "客户准备安装 {short}，需要确认哪些供电和环境条件？",
    "{short} 安装前需要检查哪些事项？",
]

INTEGRATION_Q2 = [
    "{short} 对供电和环境有什么要求？",
    "给 {short} 准备机房/场地，需要看哪些参数？",
    "{short} 的安装环境与用电条件是什么？",
    "部署 {short} 时供电和环境分别要达到什么标准？",
]

COMPARE_Q = [
    "{a} 和 {b} 的{key}有什么区别？",
    "对比一下 {a} 与 {b} 的{key}",
    "{a} 和 {b} 在{key}上有什么不同？",
    "客户在 {a} 和 {b} 之间选型，{key}怎么比？",
    "{a} 与 {b} 的{key}各是多少？",
]

NO_CTX_Q = [
    "{q}",
    "请问{q}",
    "客户问：{q}",
    "想确认一下：{q}",
]

WEAK_Q = [
    "{q}",
    "请问{q}",
    "客户问：{q}",
    "帮忙查一下{q}",
    "想确认一下：{q}",
]

CLARIFY_Q = [
    "{q}",
    "请问{q}",
    "客户问：{q}",
]

POLICY_Q = [
    "{q}",
    "请问{q}",
    "客户问：{q}",
    "想确认一下：{q}",
]

SCORE_SETS = {
    "strong": [0.9512, 0.8836, 0.8124, 0.7403, 0.6891],
    "weak": [0.4127, 0.3365],
    "conflict": [0.8914, 0.8702],
}

HISTORY_OPENERS = [
    ("你好，我想咨询一下设备的问题", "您好，请提供具体的设备型号与故障现象，我为您查询资料。"),
    ("在吗？想问个设备的事", "在的，请说明设备型号和您想了解的内容。"),
    ("帮我查一下资料", "好的，请问需要查询哪一款设备的什么内容？"),
]


# ================================================================= 参数型样本
def _param_items():
    """(product, chunk, key) 三元组全集"""
    items = []
    for p in KB.NORMALIZED_PRODUCTS:
        for c in p["chunks"]:
            if c["kind"] in ("spec", "iface", "env", "consumable", "warranty"):
                for k in c["raw"]["params"]:
                    items.append((p, c, k))
    return items


def build_param_single(rng, item):
    p, c, key = item
    value = c["raw"]["params"][key]
    is_text = key in COMPONENT_KEYS
    tpl = pick(rng, PARAM_Q_TEXT if is_text else PARAM_Q_NUM)
    question = tpl.format(short=p["short"], key=key)
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    if is_text:
        lead = pick(rng, ["根据资料，{short} 的{key}是：{value}[1]。",
                          "{short} 的{key}为：{value}[1]。",
                          "资料中{short}的{key}为 {value}[1]。"])
    else:
        lead = pick(rng, ["根据资料，{short} 的{key}为：{value}[1]。",
                          "{short} 的{key}是 {value}[1]。",
                          "资料中{short}的{key}为 {value}[1]。",
                          "{short} 的{key}参数为 {value}[1]。"])
    return build(question, docs, [lead.format(short=p["short"], key=key, value=value)],
                 "format", item_names=[p["name"]])


def build_param_double(rng, item):
    p, c, _ = item
    keys = list(c["raw"]["params"].keys())
    if len(keys) < 2:
        return None
    k1, k2 = pick_n(rng, keys, 2)
    question = pick(rng, PARAM_Q2).format(short=p["short"], k1=k1, k2=k2)
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    lines = ["%s 的两项参数如下[1]：" % p["short"], "",
             "- %s：%s" % (k1, c["raw"]["params"][k1]),
             "- %s：%s" % (k2, c["raw"]["params"][k2])]
    return build(question, docs, lines, "format", item_names=[p["name"]])


# ================================================================= 步骤型样本
def build_step(rng, item):
    p, c = item
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    lines = ["%s「%s」的操作步骤如下[1]：" % (p["short"], c["raw"]["topic"]), ""]
    for i, s in enumerate(c["raw"]["steps"], 1):
        lines.append("%d. %s" % (i, s))
    lines.append("")
    lines.append("以上步骤均依据《%s》的「%s」章节[1]。" % (c["doc"], c["sec"]))

    # 50% 概率追加一条安全/维护提示，训练"多片段整合 + 引用"
    extra = KB.chunks_of(p, ("safety", "maint"))
    if extra and rng.random() < 0.5:
        ex = pick(rng, extra)
        docs.append(make_doc(ex, SCORE_SETS["strong"][1]))
        note = pick(rng, ex["raw"]["notes"])
        lines += ["", "注意：%s[2]" % note.rstrip("。")]
    if c["raw"].get("tail"):
        lines += ["", c["raw"]["tail"]]

    question = pick(rng, STEP_Q).format(short=p["short"], topic=c["raw"]["topic"])
    return build(question, docs, lines, "step", item_names=[p["name"]])


# ================================================================= 故障型样本
def build_fault(rng, item):
    p, c, fault = item
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    lines = ["%s 出现「%s」时，可按以下顺序排查[1]：" % (p["short"], fault["symptom"]), ""]
    for i, fix in enumerate(fault["fixes"], 1):
        lines.append("%d. %s" % (i, fix))
    fixes_text = "".join(fault["fixes"])
    if any(w in fixes_text for w in ("售后", "送修", "专业人员")):
        lines += ["", "若按以上步骤仍无法排除，请联系售后或授权服务商进一步检测。"]
    question = pick(rng, FAULT_Q).format(short=p["short"], symptom=fault["symptom"])
    return build(question, docs, lines, "faithful", item_names=[p["name"]])


# ============================================================== 条目型样本
def build_notes(rng, item, kind, templates, header, capability="format"):
    p, c = item
    notes = c["raw"]["notes"]
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    lines = ["%s 的%s如下[1]：" % (p["short"], header), ""]
    for i, n in enumerate(notes, 1):
        lines.append("%d. %s" % (i, n))
    if kind == "safety":
        question = pick(rng, SAFETY_Q).format(short=p["short"])
    elif kind == "maint":
        question = pick(rng, MAINT_Q).format(short=p["short"])
    else:
        question = pick(rng, CERT_Q).format(short=p["short"])
    return build(question, docs, lines, capability, item_names=[p["name"]])


def build_packing(rng, item):
    p, c = item
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    lines = ["%s 的包装清单如下[1]：" % p["short"], ""]
    for it in c["raw"]["items"]:
        lines.append("- %s" % it)
    if c["raw"].get("note"):
        lines += ["", "说明：%s" % c["raw"]["note"].rstrip("。")]
    question = pick(rng, PACKING_Q).format(short=p["short"])
    return build(question, docs, lines, "format", item_names=[p["name"]])


def build_consumable(rng, item):
    p, c = item
    params = c["raw"]["params"]
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    tpl = pick(rng, CONSUMABLE_Q)
    if "{key}" in tpl:
        key = pick(rng, list(params))
        question = tpl.format(short=p["short"], key=key)
        lines = ["%s 的%s为：%s[1]。" % (p["short"], key, params[key])]
    else:
        question = tpl.format(short=p["short"])
        lines = ["%s 的耗材与配件规格如下[1]：" % p["short"], ""]
        for k, v in params.items():
            lines.append("- %s：%s" % (k, v))
    return build(question, docs, lines, "format", item_names=[p["name"]])


def build_env(rng, item):
    p, c = item
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    lines = ["%s 的安装与使用环境要求如下[1]：" % p["short"], ""]
    for k, v in c["raw"]["params"].items():
        lines.append("- %s：%s" % (k, v))
    question = pick(rng, ENV_Q).format(short=p["short"])
    return build(question, docs, lines, "format", item_names=[p["name"]])


# ============================================================== 多片段整合样本
def _find_param(product, keywords, kinds=("spec", "iface", "env", "consumable", "warranty")):
    for c in product["chunks"]:
        if c["kind"] not in kinds:
            continue
        for k, v in c["raw"]["params"].items():
            if any(w in k for w in keywords):
                return c, k, v
    return None


def build_integration(rng, item):
    """整合 供电 + 环境 + 接口 + 安全 四个片段"""
    p, mode = item
    power = _find_param(p, ["电源", "电压", "功率", "功耗", "输入"])
    env_c = KB.chunks_of(p, "env")
    iface_c = KB.chunks_of(p, "iface")
    safety_c = KB.chunks_of(p, "safety")
    if not (power and env_c and iface_c and safety_c):
        return None

    env = pick(rng, env_c)
    iface = pick(rng, iface_c)
    safety = pick(rng, safety_c)
    env_params = env["raw"]["params"]
    iface_key = pick(rng, list(iface["raw"]["params"]))

    if mode == 0:
        docs = [make_doc(power[0], SCORE_SETS["strong"][0]),
                make_doc(env, SCORE_SETS["strong"][1]),
                make_doc(iface, SCORE_SETS["strong"][2]),
                make_doc(safety, SCORE_SETS["strong"][3])]
        lines = ["部署 %s 前，需要同时满足以下几方面条件：" % p["short"], "",
                 "1. 供电：%s：%s[1]" % (power[1], power[2])]
        env_line = "、".join("%s %s" % (k, v) for k, v in list(env_params.items())[:2])
        lines.append("2. 环境：%s[2]" % env_line)
        lines.append("3. 接口与连接：%s：%s[3]" % (iface_key, iface["raw"]["params"][iface_key]))
        lines.append("4. 安全：%s[4]" % pick(rng, safety["raw"]["notes"]).rstrip("。"))
        lines += ["", "以上条件需同时满足，任一不满足都可能造成设备无法正常工作或影响保修。"]
        question = pick(rng, INTEGRATION_Q).format(short=p["short"])
    else:
        docs = [make_doc(power[0], SCORE_SETS["strong"][0]),
                make_doc(env, SCORE_SETS["strong"][1]),
                make_doc(safety, SCORE_SETS["strong"][2])]
        lines = ["%s 在供电与环境方面的要求如下：" % p["short"], "",
                 "1. 供电：%s：%s[1]" % (power[1], power[2])]
        env_lines = ["- %s：%s" % (k, v) for k, v in env_params.items()]
        lines += ["2. 环境要求如下[2]：", ""] + ["   " + x for x in env_lines]
        lines += ["", "3. 安全：%s[3]" % pick(rng, safety["raw"]["notes"]).rstrip("。")]
        question = pick(rng, INTEGRATION_Q2).format(short=p["short"])
    return build(question, docs, lines, "integration", item_names=[p["name"]])


COMPARE_KEYS = ["整机保修", "净重", "电源", "功率", "工作温度", "外形尺寸"]
# 跨品类选型时只比较通用属性，避免出现"电磁炉与一体机比幅面"这类不合理对比
CROSS_CATEGORY_KEYS = ["整机保修", "工作温度", "净重"]


def build_compare(rng, item):
    a, b = item
    candidates = COMPARE_KEYS if a["category"] == b["category"] else CROSS_CATEGORY_KEYS
    keys = []
    for key in candidates:
        pa = _find_param(a, [key])
        pb = _find_param(b, [key])
        if pa and pb:
            keys.append((key, pa, pb))
    if not keys:
        return None
    key, pa, pb = pick(rng, keys)
    docs = [make_doc(pa[0], SCORE_SETS["strong"][0]),
            make_doc(pb[0], SCORE_SETS["strong"][1])]
    lines = ["两款机型在「%s」上的对比如下：" % key, "",
             "| 机型 | %s |" % key, "| --- | --- |",
             "| %s | %s[1] |" % (a["short"], pa[2]),
             "| %s | %s[2] |" % (b["short"], pb[2]), "",
             "选型时请以实际使用场景为准，如需进一步对比其他参数，请说明具体项目。"]
    question = pick(rng, COMPARE_Q).format(a=a["short"], b=b["short"], key=key)
    return build(question, docs, lines, "integration",
                 item_names=[a["name"], b["name"]])


# ============================================================== 制度条款样本
def build_clause(rng, item):
    c, qa = item
    question = pick(rng, POLICY_Q).format(q=qa[0])
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    lines = ["%s[1]" % qa[1], "", "依据："]
    for point in qa[2]:
        lines.append("- %s[1]" % point)
    return build(question, docs, lines, "integration", item_names=[])


# ============================================================== 保修判定样本
# 各产品保修条款中对应的"主要部件"
MAIN_PARTS = {
    "启明 X300 商用台式机": "硬盘",
    "启明 B530 商用一体机": "液晶面板",
    "启明 G740 图形工作站": "电源模块",
    "博印 HAK180 烫金机": "加热管",
    "博印 HAK181 数码烫金机": "伺服电机与控制系统",
    "朗行 D530 标签打印机": "打印头",
    "厨霸 IH-5000 商用电磁炉": "微晶面板",
    "视界 P200 商务投影仪": "灯泡",
    "安盾 S80 碎纸机": "刀具组件",
    "恒电 UPS-3000 不间断电源": "蓄电池",
}

# 人为或免责类故障
HUMAN_CAUSES = [
    ("不小心摔到地上导致外壳破裂", "人为损坏"),
    ("自己拆机清灰后无法开机", "未经授权的拆机"),
    ("进水后无法开机", "进液"),
    ("被雷击后无法开机", "不可抗力"),
]


def _causes_for(product):
    """按产品生成候选故障场景：通用故障 + 主要部件故障 + 人为/免责故障"""
    part = MAIN_PARTS.get(product["name"])
    causes = [("出现非人为的性能故障，无法正常使用", True, None, "")]
    if part:
        causes.append(("%s出现非人为的性能故障，无法继续使用" % part, True,
                       "主要部件", "%s属于主要部件" % part))
    for cause, reason in HUMAN_CAUSES:
        causes.append((cause, False, None, reason))
    return causes

INVOICE_NOTE = ("无有效发票时，保修期按机身序列号对应的出厂日期顺延 90 日计算，"
                "实际起算时间可能延后，建议提供发票或机身 SN 以便核对[2]")


def build_warranty_scenario(rng, item):
    """结合产品保修条款与三包实施细则做条件判断（多片段 + 主次区分）"""
    p, wchunk = item
    cause, covered, part, reason = pick(rng, _causes_for(p))
    month_choices = [3, 8, 11, 14, 20, 28, 40]
    whole_months = wchunk["raw"]["months"]
    part_months = max(wchunk["raw"]["parts_months"], 24) \
        if p["category"] == "商用计算机" else wchunk["raw"]["parts_months"]
    if part:
        # 保证覆盖"整机与部件都在保 / 整机过保但部件在保 / 均已过保 / 整机在保但部件过保"四类边界
        groups = [
            [m for m in month_choices if m < min(whole_months, part_months)],
            [m for m in month_choices if whole_months <= m < part_months],
            [m for m in month_choices if m >= max(whole_months, part_months)],
            [m for m in month_choices if part_months <= m < whole_months],
        ]
        groups = [g for g in groups if g]
        months_used = pick(rng, pick(rng, groups))
    else:
        months_used = pick(rng, month_choices)
    has_invoice = rng.random() < 0.6
    clause_exclude = KB.find_clause("第五条", "三包")
    clause_period = KB.find_clause("第一条", "三包")
    docs = [make_doc(wchunk, SCORE_SETS["strong"][0])]

    question = "{short} 买了 {m} 个月，{cause}，还能免费保修吗？".format(
        short=p["short"], m=months_used, cause=cause)
    if not has_invoice:
        question += "（发票找不到了）"

    whole = wchunk["raw"]["months"]
    # 计算机类产品的主要部件同时适用三包 24 个月的规定
    parts = max(wchunk["raw"]["parts_months"], 24) if p["category"] == "商用计算机" \
        else wchunk["raw"]["parts_months"]
    warranty_line = wchunk["raw"]["params"].get("整机保修", "")

    if not covered:
        docs.append(make_doc(clause_exclude, SCORE_SETS["strong"][1]))
        lines = ["结论：不属于免费保修范围，需按收费维修处理。", "", "原因与依据：",
                 "- 该情况属于%s，属于产品保修条款中的免责情形[1]" % reason,
                 "- 按三包规定，未按说明书要求使用、保管造成损坏，或非授权拆机、"
                 "不可抗力造成损坏的，均不属于三包范围[2]",
                 "- 收费维修前服务商须出示《维修报价单》，经确认后方可实施[2]"]
        if not has_invoice:
            lines.append("- " + INVOICE_NOTE)
        return build(question, docs, lines, "integration", item_names=[p["name"]])

    # 非人为性能故障：先判整机，再判具体部件
    if months_used < whole:
        docs.append(make_doc(clause_period, SCORE_SETS["strong"][1]))
        if part and months_used >= parts:
            # 整机在保，但故障部件属于短保部件/易损件，已单独过保
            lines = ["结论：整机仍在保修期，但故障部件需收费更换。", "", "依据：",
                     "- %s 整机保修 %s，已使用 %d 个月，整机保修期尚未届满[1]"
                     % (p["short"], warranty_line, months_used),
                     "- %s，保修期为 %d 个月，已使用 %d 个月，该部件保修期已届满[1]"
                     % (reason, parts, months_used),
                     "- 该部件按短保部件/易损件单独约定保修期，与整机保修期不一致，"
                     "因此整机范围内的其他非人为故障仍可免费修理，本部件需收费[2]"]
            if not has_invoice:
                lines.append("- " + INVOICE_NOTE)
            lines += ["", "建议先由服务商检测确认故障部件，再确认报价后维修。"]
            return build(question, docs, lines, "integration", item_names=[p["name"]])
        lines = ["结论：可以享受免费保修。", "", "依据：",
                 "- %s 整机保修 %s，当前已使用 %d 个月，仍在保修期内[1]"
                 % (p["short"], warranty_line, months_used),
                 "- 故障为非人为性能故障，三包有效期内由授权服务商提供免费修理[2]"]
        if part:
            lines.append("- %s，保修期 %d 个月，同样在有效期内[1]" % (reason, parts))
        if not has_invoice:
            lines.append("- " + INVOICE_NOTE)
        lines += ["", "建议联系授权服务商并出示购机凭证，由服务商出具《维修服务单》。"]
        return build(question, docs, lines, "integration", item_names=[p["name"]])

    if part and months_used < parts:
        docs.append(make_doc(clause_period, SCORE_SETS["strong"][1]))
        lines = ["结论：整机保修期已过，但%s仍可免费保修。" % reason, "", "依据：",
                 "- %s 整机保修 %s，已使用 %d 个月，整机保修期已届满[1]"
                 % (p["short"], warranty_line, months_used),
                 "- %s，保修期 %d 个月，仍在有效期内[1]" % (reason, parts)]
        if p["category"] == "商用计算机":
            lines.append("- 三包规定主要部件（主板、CPU、内存、硬盘、电源、显示器）"
                         "三包有效期为 24 个月[2]")
        if not has_invoice:
            lines.append("- " + INVOICE_NOTE)
        return build(question, docs, lines, "integration", item_names=[p["name"]])

    docs.append(make_doc(clause_exclude, SCORE_SETS["strong"][1]))
    lines = ["结论：已超出保修期限，需按收费维修处理。", "", "依据：",
             "- %s 整机保修 %s，已使用 %d 个月，保修期已届满[1]"
             % (p["short"], warranty_line, months_used)]
    if part:
        lines.append("- %s 保修 %d 个月，同样已超出期限[1]" % (reason, parts))
    lines.append("- 超过三包有效期的，实行收费维修，费用包括配件费、维修工时费与上门费[2]")
    if not has_invoice:
        lines.append("- " + INVOICE_NOTE)
    return build(question, docs, lines, "integration", item_names=[p["name"]])


# ============================================================== 部分不可答样本
def build_partial(rng, item):
    """问题包含两部分：一部分资料中有，一部分资料中没有，训练知之为知之"""
    p, c, key, unknown = item
    value = c["raw"]["params"][key]
    docs = [make_doc(c, SCORE_SETS["strong"][0])]
    # 未知话题若是名词短语则补全为完整问句，若已是"是否…"则直接使用
    if unknown.startswith("是否") or unknown.startswith("能否") or unknown.startswith("可以"):
        unknown_q = "{short} {unknown}？".format(short=p["short"], unknown=unknown)
    else:
        unknown_q = "{short} 的{unknown}是多少？".format(short=p["short"], unknown=unknown)
    if key in COMPONENT_KEYS:
        known_q = "{short} 的{key}是什么？".format(short=p["short"], key=key)
    else:
        known_q = "{short} 的{key}是多少？".format(short=p["short"], key=key)
    question = pick(rng, [
        "{known}另外，{unknown}",
        "{known}顺便问一下{unknown}",
        "我想了解{short}的{key}，另外{unknown}",
        "{known}另外能不能告诉我，{unknown}",
    ]).format(known=known_q, unknown=unknown_q, short=p["short"], key=key)
    lead = "%s 的%s是：%s[1]。" if key in COMPONENT_KEYS else "%s 的%s为：%s[1]。"
    lines = [lead % (p["short"], key, value), "",
             "关于「%s」，当前检索到的资料中没有相关记载，我无法确认，为避免误导不做推测。"
             % unknown_q.rstrip("？"), "",
             "建议补充以下信息以便进一步核实：",
             "1. 提供该机型的完整版规格书或厂商正式参数表；",
             "2. 确认具体出厂批次（机身铭牌可查看）；",
             "3. 或联系厂商技术支持核对后，我再为您整理答复。"]
    return build(question, docs, lines, "faithful", item_names=[p["name"]])


# ============================================================== 拒答类样本
def build_no_context(rng, item):
    q = pick(rng, NO_CTX_Q).format(q=item)
    with_item = rng.random() < 0.45
    product = pick(rng, KB.NORMALIZED_PRODUCTS) if with_item else None
    lines = ["很抱歉，当前知识库中没有检索到与「%s」相关的资料，我无法给出可靠答复，"
             "为避免误导不做推测。" % item, "",
             "建议补充以下信息，以便进一步确认：",
             "1. 明确问题所属的业务领域与具体场景；",
             "2. 提供相关的制度文件、产品型号或文档名称；",
             "3. 或联系对应业务负责人核实后，我再为您查找依据。"]
    return build(q, [], lines, "refusal",
                 item_names=[product["name"]] if product else None, citations=False)


def build_weak(rng, item):
    pname, q, sec_kw, need = item
    p = KB.PRODUCT_BY_NAME[pname]
    candidates = [c for c in p["chunks"] if any(k in c["sec"] for k in sec_kw)]
    if not candidates:
        return None
    c = pick(rng, candidates)
    docs = [make_doc(c, SCORE_SETS["weak"][0])]
    question = pick(rng, WEAK_Q).format(q=q)
    lines = ["很抱歉，当前检索到的资料不足以回答「%s」。" % q, "",
             "已召回的内容仅涉及《%s》的「%s」章节，其中并未包含%s[1]。" % (c["doc"], c["sec"], need), "",
             "建议补充以下信息：",
             "1. %s；" % need,
             "2. 提供该机型的完整版说明书或规格书；",
             "3. 或联系厂商技术支持确认后，我再为您整理答复。"]
    return build(question, docs, lines, "refusal", item_names=[p["name"]], citations=False)


def build_conflict(rng, item):
    topic = item
    a, b = topic["a"], topic["b"]
    src_b, url_b = "local", None
    if "官网" in b["doc"]:
        src_b = "web"
        url_b = "https://kb.example-service.com/policy/" + hashlib.md5(
            b["doc"].encode("utf-8")).hexdigest()[:10]
    docs = [
        {"chunk_id": a["chunk_id"], "source": "local", "url": None, "title": a["doc"],
         "score": SCORE_SETS["conflict"][0], "content": "【%s】\n%s" % (a["sec"], a["text"]),
         "doc": a["doc"], "sec": a["sec"], "img_url": None},
        {"chunk_id": b["chunk_id"], "source": src_b, "url": url_b, "title": b["doc"],
         "score": SCORE_SETS["conflict"][1], "content": "【%s】\n%s" % (b["sec"], b["text"]),
         "doc": b["doc"], "sec": b["sec"], "img_url": None},
    ]
    question = pick(rng, topic["questions"])
    lines = ["关于「%s」，当前检索到的两份资料表述不一致，暂不能给出确定结论：" % topic["topic"], "",
             "- 资料[1]《%s》· %s：%s" % (a["doc"], a["sec"], a["text"]),
             "- 资料[2]《%s》· %s：%s" % (b["doc"], b["sec"], b["text"]), "",
             topic["hint"], "",
             "为避免给出错误参数，请您补充：%s。提供后我可以按对应批次或工况重新核算，"
             "并给出明确结论。" % topic["need"]]
    return build(question, docs, lines, "refusal", item_names=[topic["item"]], citations=False)


def build_clarify(rng, item):
    category, names, q = item
    products = [KB.PRODUCT_BY_NAME[n] for n in names]
    docs = []
    for i, p in enumerate(products):
        c = pick(rng, KB.chunks_of(p, ("spec", "iface")))
        docs.append(make_doc(c, SCORE_SETS["strong"][i]))
    lines = ["您好，知识库中「%s」涉及多个型号，为保证答复准确，请先确认您咨询的具体型号：" % category, ""]
    for i, p in enumerate(products, 1):
        lines.append("%d. %s" % (i, p["name"]))
    lines += ["", "请回复型号，或提供设备铭牌照片，我再依据该型号的说明书为您解答。"]
    question = pick(rng, CLARIFY_Q).format(q=q)
    return build(question, docs, lines, "refusal", item_names=None, citations=False)


# ==================================================================== 主流程
def _materials():
    """预生成各构造器可用的素材池"""
    mats = {}

    params = _param_items()
    mats["param_single"] = params
    mats["param_double"] = params
    mats["step"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS for c in KB.chunks_of(p, "step")]
    mats["fault"] = [(p, c, f) for p in KB.NORMALIZED_PRODUCTS
                     for c in KB.chunks_of(p, "fault") for f in c["raw"]["faults"]]
    mats["safety"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS for c in KB.chunks_of(p, "safety")]
    mats["maint"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS for c in KB.chunks_of(p, "maint")]
    mats["cert"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS for c in KB.chunks_of(p, "cert")]
    mats["packing"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS for c in KB.chunks_of(p, "packing")]
    mats["consumable"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS for c in KB.chunks_of(p, "consumable")]
    mats["env"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS for c in KB.chunks_of(p, "env")]
    mats["integration"] = [(p, m) for p in KB.NORMALIZED_PRODUCTS for m in (0, 1)]
    mats["compare"] = [(a, b) for i, a in enumerate(KB.NORMALIZED_PRODUCTS)
                       for b in KB.NORMALIZED_PRODUCTS[i + 1:]]
    mats["clause"] = [(c, qa) for c in KB.POLICY_CHUNKS for qa in c["raw"]["qa"]]
    mats["warranty_scenario"] = [(p, c) for p in KB.NORMALIZED_PRODUCTS
                                 for c in KB.chunks_of(p, "warranty")]
    mats["partial"] = [(p, c, k, u)
                       for p in KB.NORMALIZED_PRODUCTS
                       for c in KB.chunks_of(p, ("spec", "iface", "env", "consumable"))
                       for k in list(c["raw"]["params"])[:2]
                       for u in p["unknown"]]
    mats["no_ctx"] = list(KB.NO_CONTEXT)
    mats["weak"] = list(KB.WEAK)
    mats["conflict"] = list(KB.CONFLICTS)
    mats["clarify"] = [(cat, names, q) for cat, names, qs in KB.CLARIFY for q in qs]
    return mats


# (构造器名, 构造函数, 目标条数)
PLAN = [
    ("param_single", build_param_single, 108),
    ("param_double", build_param_double, 40),
    ("env", build_env, 20),
    ("packing", build_packing, 18),
    ("cert", lambda r, i: build_notes(r, i, "cert", CERT_Q, "认证与合规情况"), 14),
    ("consumable", build_consumable, 20),
    ("safety", lambda r, i: build_notes(r, i, "safety", SAFETY_Q, "安全注意事项"), 45),
    ("maint", lambda r, i: build_notes(r, i, "maint", MAINT_Q, "维护保养要求"), 35),
    ("step", build_step, 80),
    ("fault", build_fault, 115),
    ("partial", build_partial, 50),
    ("integration", build_integration, 70),
    ("compare", build_compare, 45),
    ("clause", build_clause, 75),
    ("warranty_scenario", build_warranty_scenario, 50),
    ("no_ctx", build_no_context, 45),
    ("weak", build_weak, 55),
    ("conflict", build_conflict, 55),
    ("clarify", build_clarify, 35),
]

TARGET_TOTAL = 1000  # 目标总条数，不足部分由素材池补充


def maybe_history(rng, p):
    """少量样本注入多轮历史，训练指代消解与上下文衔接"""
    opener = pick(rng, HISTORY_OPENERS)
    others = [c for c in KB.chunks_of(p, ("spec", "env")) if c["raw"].get("params")]
    if not others:
        return None
    c = pick(rng, others)
    k = pick(rng, list(c["raw"]["params"]))
    return [
        {"role": "user", "text": opener[0]},
        {"role": "assistant", "text": opener[1]},
        {"role": "user", "text": "%s 的%s是多少？" % (p["short"], k)},
        {"role": "assistant", "text": "%s 的%s为：%s。" % (p["short"], k, c["raw"]["params"][k])},
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="kb_finetune_1000.jsonl")
    parser.add_argument("--seed", type=int, default=20250831)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    mats = _materials()
    seen = set()
    samples = []
    stats = {}

    for name, builder, target in PLAN:
        pool = mats[name]
        got, tries = 0, 0
        limit = target * 60
        while got < target and tries < limit:
            tries += 1
            item = pick(rng, pool)
            s = builder(rng, item)
            if s is None:
                continue
            key = hashlib.md5(s["question"].encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            samples.append(s)
            got += 1
        stats[name] = got
        if got < target:
            print("[WARN] %s 目标 %d，实际生成 %d（素材不足或去重过多）" % (name, target, got))

    # 数量不足时按素材池补充
    names = [p[0] for p in PLAN]
    builders = {p[0]: p[1] for p in PLAN}
    guard = 0
    while len(samples) < TARGET_TOTAL and guard < TARGET_TOTAL * 80:
        guard += 1
        name = pick(rng, names)
        s = builders[name](rng, pick(rng, mats[name]))
        if s is None:
            continue
        key = hashlib.md5(s["question"].encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        samples.append(s)
        stats[name] = stats.get(name, 0) + 1

    # 少量样本注入多轮历史，训练指代消解与上下文衔接
    hist_count = 0
    for s in samples:
        if s["capability"] == "refusal" or rng.random() >= 0.15:
            continue
        names = [n for n in s["item"] if n in KB.PRODUCT_BY_NAME]
        if not names:
            continue
        h = maybe_history(rng, KB.PRODUCT_BY_NAME[names[0]])
        if not h:
            continue
        conv = s["record"]["conversations"][0]["content"]
        s["record"]["conversations"][0]["content"] = conv.replace(
            "【历史对话】\n暂无历史对话", "【历史对话】\n" + render_history(h))
        hist_count += 1

    rng.shuffle(samples)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s["record"], ensure_ascii=False) + "\n")

    print("已生成 %d 条 -> %s" % (len(samples), out_path))
    cap = {}
    for s in samples:
        cap[s["capability"]] = cap.get(s["capability"], 0) + 1
    print("能力分布：", dict(sorted(cap.items(), key=lambda x: -x[1])))
    print("构造器分布：", dict(sorted(stats.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
