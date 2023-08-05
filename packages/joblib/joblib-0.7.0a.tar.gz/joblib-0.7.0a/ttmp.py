import numpy as np

a = np.memmap('tmp.mmap', dtype=np.float64, shape=50, mode='w+')
a[:] = np.arange(50)
b = a[10:]
