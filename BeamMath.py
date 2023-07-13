import numpy as np

def RMS(A):
    I, J = np.meshgrid(np.arange(A.shape[1]), np.arange(A.shape[0]))
    P = np.sum(A)
    mx, my = np.sum(A * I) / P, np.sum(A * J) / P
    dx, dy = np.sum(A * I * I) / P, np.sum(A * J * J) / P
    return np.array([2 * np.sqrt(dx - mx ** 2), 2 * np.sqrt(dy - my ** 2), mx, my])

def center_max(I):
    imax=np.argmax(I)
    return imax%I.shape[1],imax//I.shape[1]


def center_mean(I):
    ii=np.arange(0,I.shape[1])
    jj=np.arange(0,I.shape[0])
    s=np.sum(I)
    return int(np.sum(jj*I.T)/s),int(np.sum(ii*I)/s)