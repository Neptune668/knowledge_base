#
import torch
print(torch.cuda.is_available())  # 如果输出 True，说明成功认出显卡！
print(torch.version.cuda)
# import torch
# print(torch.cuda.is_available())  # 应该返回 True
# print(torch.version.cuda)        # 应该显示 12.8