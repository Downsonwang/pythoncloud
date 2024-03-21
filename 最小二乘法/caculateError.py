'''
引入残差计算是为了判定拟合的是否正确
'''
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot

Xi = np.array([162,165,159,173,157,175,161,164,172,158])
Yi = np.array([48,64,53,66,52,68,50,52,64,49])
xy_res=[] # 定义变量xy_res

# 定义计算残差函数
def residual(x,y):
    res = y -(0.42116973935*x-8.28830260655)
    return res

# 循环读取残差
for d in range(0,len(Xi)):
    res=residual(Xi[d],Yi[d])
    xy_res.append(res)
    
# 计算残差平方和,和越小表示越好
xy_res_num=np.dot(xy_res,xy_res)
print(xy_res_num)
# 如果数据拟合模型效果好,残差应该遵从正态分布(0,d*d),d表示残差。
fig=plt.figure(figsize=(8,6))
ax=fig.add_subplot(111)
fig=qqplot(np.array(xy_res),line='q',ax=ax)
plt.show()