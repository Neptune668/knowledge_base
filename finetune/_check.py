# -*- coding: utf-8 -*-
import json, sys, io, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

rows = [json.loads(l) for l in open("kb_finetune_1000.jsonl", encoding="utf-8") if l.strip()]


def show(r, name, full=False):
    u = r["conversations"][0]["content"]
    ctx = u.split("【参考内容】\n", 1)[1]
    q = u.split("【用户问题】\n", 1)[1].rsplit("\n\n请回答：", 1)[0]
    print("=" * 90)
    print("### " + name)
    if full:
        print(ctx.split("\n\n【历史对话】")[0])
    print("【用户问题】", q)
    print("-" * 50)
    print(r["conversations"][1]["content"])


SHOW = [
    ("条款判定(制度)", lambda a: "结论：" in a and "不属于免费保修" not in a and "整机保修" not in a),
    ("保修判定-免费", lambda a: a.startswith("结论：可以享受免费保修")),
    ("保修判定-主要部件", lambda a: a.startswith("结论：整机保修期已过")),
    ("保修判定-超保/免责", lambda a: a.startswith("结论：已超出保修期限") or a.startswith("结论：不属于免费保修")),
    ("部署整合", lambda a: "需要同时满足以下几方面条件" in a),
    ("供电环境整合", lambda a: "供电与环境方面的要求" in a),
    ("跨型号对比", lambda a: "| 机型 |" in a),
    ("型号澄清", lambda a: "涉及多个型号" in a),
    ("无召回拒答", lambda a: "没有检索到与" in a),
    ("弱相关拒答", lambda a: "不足以回答" in a),
    ("冲突拒答", lambda a: "暂不能给出确定结论" in a),
    ("部分不可答", lambda a: "资料中没有相关记载" in a),
    ("步骤带注意", lambda a: "步骤如下" in a and "注意：" in a),
    ("带图片", lambda a: "【图片】" in a),
]

random.seed(11)
random.shuffle(rows)
done = set()
for r in rows:
    a = r["conversations"][1]["content"]
    for name, cond in SHOW:
        if name in done:
            continue
        if cond(a):
            done.add(name)
            show(r, name, full=name in ("保修判定-免费", "部署整合", "型号澄清"))
            break
    if len(done) == len(SHOW):
        break
print("\n未覆盖:", [n for n, _ in SHOW if n not in done])

for r in rows:
    u = r["conversations"][0]["content"]
    if "暂无历史对话" not in u:
        show(r, "多轮历史")
        break
