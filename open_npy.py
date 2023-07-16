import sys
import numpy as np
import matplotlib.pyplot as plt


if __name__=='__main__':
	plt.imshow(np.load(sys.argv[1]))
	plt.show()
