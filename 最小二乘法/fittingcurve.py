'''
 拟合曲线
'''


## 样本数据转换
from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import leastsq
## 自变量
Xi = np.array([162,165,159,173,157,175,161,164,172,158])
## 因变量
Yi = np.array([48,64,53,66,52,68,50,52,64,49])

## 拟合函数 y= kx+b
def func(p,x):
    ## p(包含斜率k和截距b)和自变量x 返回拟合值y
    k,b = p
    return k*x+b


## 定义偏差函数 误差函数将用于最小二乘法优化
def error(p,x,y):
    return func(p,x)-y

p0 =[1,20]

## 接受误差函数error和初参数估计p0
## leastsq 函数内部执行的是一个迭代过程，它逐步调整参数 p，以找到最小化残差平方和的参数值。这个过程是基于最小二乘原理的，即通过最小化误差的平方和来找到最佳拟合参数。

Para = leastsq(error,p0,args=(Xi,Yi))

## 读取结果

k,b=Para[0]
## 打印斜率k和截距b
print("k=",k,"b=",b)

plt.figure(figsize=(8,6))
plt.scatter(Xi,Yi,color="red",label="身高体重样本数据:",linewidth=2)
x=np.linspace(150,180,80)
y=k*x+b
plt.plot(x,y,color="blue",label="Fitting Curve",linewidth=2)
plt.legend()
plt.xlabel('Height:cm')
plt.ylabel('Weight:kg')
plt.show()