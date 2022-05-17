import numpy as np

array1 = np.array([1,2,3])
array2 = np.array([2,4,5])

covariance = np.cov(array1, array2)
print(covariance)