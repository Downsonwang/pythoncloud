


import numpy as np
import scipy as sp
import matplotlib.pyplot as plt 
from scipy.optimize import leastsq


## 样本数据转换
Xi = np.array([162,165,159,173,157,175,161,164,172,158])
Yi = np.array([48,64,53,66,52,68,50,52,64,49])


## 绘制样本

plt.figure(figsize=(8,6))
plt.scatter(Xi,Yi,color="red",label="身高体重样本数据:",linewidth=1)
plt.xlabel('Height:cm')
plt.ylabel('Weight:kg')
plt.show()