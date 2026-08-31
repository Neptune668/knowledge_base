# -*- coding: utf-8 -*-
"""
语料归一化：把结构化语料渲染成"知识库切片"的形态（标题 + 正文 + 可选图片）

渲染结果与线上 RAG 流水线中 Milvus 切片的结构保持一致，保证微调数据与推理时
喂给模型的上下文同构。
"""

import hashlib

from corpus_products import PRODUCTS
from corpus_policy import POLICY_DOCS, CONFLICT_TOPICS, WEAK_QUERIES, NO_CONTEXT_QUERIES, CLARIFY_QUERIES

IMG_HOST = "http://192.168.100.100:9000/knowledge-base/upload-images/"

_PARAMS_KINDS = {"spec", "iface", "env", "consumable", "warranty"}
_NOTES_KINDS = {"safety", "maint", "cert"}
_HEADERS = {
    "spec": "",
    "iface": "",
    "env": "",
    "consumable": "",
    "warranty": "",
    "safety": "安全注意事项：",
    "maint": "维护保养要求：",
    "cert": "认证与合规情况：",
}


def _hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _join_numbered(items):
    return "".join(f"{i}）{s}；" for i, s in enumerate(items, 1)).rstrip("；") + "。"


def _render_text(chunk):
    """由结构化字段派生切片正文，保证问题与答案同源"""
    kind = chunk["kind"]

    if kind in _PARAMS_KINDS:
        body = "；".join(f"{k}：{v}" for k, v in chunk["params"].items())
        return body + "。"

    if kind == "step":
        body = f"{chunk['topic']}步骤：" + "".join(
            f"{i}）{s}；" for i, s in enumerate(chunk["steps"], 1)
        ).rstrip("；") + "。"
        return body + (chunk.get("tail") or "")

    if kind == "fault":
        parts = []
        for f in chunk["faults"]:
            parts.append(
                f"故障现象：{f['symptom']}。排查："
                + "".join(f"{i}）{x}；" for i, x in enumerate(f["fixes"], 1)).rstrip("；") + "。"
            )
        return "".join(parts)

    if kind in _NOTES_KINDS:
        return _HEADERS[kind] + _join_numbered(chunk["notes"])

    if kind == "packing":
        body = "包装箱内包含：" + "、".join(chunk["items"]) + "。"
        return body + (chunk.get("note") or "")

    if kind == "clause":
        return chunk["text"]

    raise ValueError(f"未知切片类型: {kind}")


def _normalize(chunk, product=None):
    item = {
        "doc": chunk["doc"],
        "sec": chunk["sec"],
        "kind": chunk["kind"],
        "text": _render_text(chunk),
        "raw": chunk,
        "product": product["name"] if product else None,
    }
    item["chunk_id"] = "kb_" + _hash(item["doc"] + "|" + item["sec"])[:12]
    item["img_url"] = IMG_HOST + _hash(item["doc"] + "|" + item["sec"]) + ".jpg" if chunk.get("img") else None
    return item


# ------------------------------------------------------------------ 产品切片
NORMALIZED_PRODUCTS = []
for _p in PRODUCTS:
    _chunks = [_normalize(c, _p) for c in _p["chunks"]]
    NORMALIZED_PRODUCTS.append({
        "name": _p["name"],
        "short": _p["short"],
        "category": _p["category"],
        "unknown": _p["unknown"],
        "chunks": _chunks,
    })

PRODUCT_BY_NAME = {p["name"]: p for p in NORMALIZED_PRODUCTS}


def chunks_of(product, kinds):
    if isinstance(kinds, str):
        kinds = (kinds,)
    return [c for c in product["chunks"] if c["kind"] in kinds]


# ------------------------------------------------------------------ 制度切片
POLICY_CHUNKS = []
for _d in POLICY_DOCS:
    for _c in _d["clauses"]:
        _c["kind"] = "clause"
        _c["doc"] = _d["doc"]
        POLICY_CHUNKS.append(_normalize(_c))


def find_clause(sec_keyword, doc_keyword=None):
    """按章节关键字查找条款，可用 doc_keyword 限定制度文档，避免跨文档误匹配"""
    for c in POLICY_CHUNKS:
        if doc_keyword and doc_keyword not in c["doc"]:
            continue
        if sec_keyword in c["sec"]:
            return c
    return None


# ---------------------------------------------------------------- 冲突/拒答语料
CONFLICTS = []
for _t in CONFLICT_TOPICS:
    CONFLICTS.append({
        "item": _t["item"],
        "topic": _t["topic"],
        "questions": _t["questions"],
        "a": {"doc": _t["a"]["doc"], "sec": _t["a"]["sec"], "text": _t["a"]["text"],
              "chunk_id": "kb_" + _hash(_t["a"]["doc"] + "|" + _t["a"]["sec"])[:12]},
        "b": {"doc": _t["b"]["doc"], "sec": _t["b"]["sec"], "text": _t["b"]["text"],
              "chunk_id": "kb_" + _hash(_t["b"]["doc"] + "|" + _t["b"]["sec"])[:12]},
        "hint": _t["hint"],
        "need": _t["need"],
    })

WEAK = WEAK_QUERIES
NO_CONTEXT = NO_CONTEXT_QUERIES
CLARIFY = CLARIFY_QUERIES
