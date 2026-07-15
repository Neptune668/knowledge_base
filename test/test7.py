from utils.embedding_utils import generate_embeddings, get_bge_m3_ef

model = get_bge_m3_ef()

texts = ["测试","hello"]

documents = model.encode_documents(texts)
print(documents)
from modelscope import snapshot_download
# model_dir = "D:\\ai_models\\modelscope_cache\\models\\models\\BAAI--bge-m3\\snapshots\\master"
# # 或使用 modelscope 的自动缓存机制
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer(model_dir)
# print(model.encode("测试文本").shape)
# from sentence_transformers import SentenceTransformer, util
#
# model = SentenceTransformer("D:\\ai_models\\modelscope_cache\\models\\models\\BAAI--bge-m3\\snapshots\\master")
#
# # 待比较的句子
# emb1 = model.encode("如何制作披萨")
# emb2 = model.encode("披萨的烹饪方法")
# emb3 = model.encode("今天天气怎么样")
#
# # 计算余弦相似度
# sim_12 = util.cos_sim(emb1, emb2)
# sim_13 = util.cos_sim(emb1, emb3)
#
# print(f"披萨制作 vs 烹饪方法: {sim_12[0][0]:.4f}")  # 输出应该很高，比如 0.85+
# print(f"披萨制作 vs 天气: {sim_13[0][0]:.4f}")    # 输出应该很低，比如 0.2
