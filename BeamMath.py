import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft2,ifft2,fftshift

class beam_math:
    
    noise_map=[[0]]
    calibration_coeffs=(1,3,5)
    cam_exp_time=2000
    cam_exp_mode=False

    def __init__(self,Nx,Ny):
        self.update_grid(Nx,Ny)
    
    def update_grid(self,Nx,Ny):
        self.I_grid,self.J_grid=np.meshgrid(\
			np.arange(Nx),\
			np.arange(Ny)
		)
        self.I_grid_sqr=self.I_grid*self.I_grid
        self.J_grid_sqr=self.J_grid*self.J_grid
    def RMS(self,img,dtype='float64'):
        P=np.sum(img,dtype=dtype)
        mx=np.sum(img*self.I_grid,dtype=dtype)
        my=np.sum(img*self.J_grid,dtype=dtype)
        Dx=np.sum(img*self.I_grid_sqr,dtype=dtype)
        Dy=np.sum(img*self.J_grid_sqr,dtype=dtype)
        mx/=P
        my/=P
        RMS_x=2*np.sqrt(Dx/P-mx*mx)
        RMS_y=2*np.sqrt(Dy/P-my*my)
        return P,mx,my,RMS_x,RMS_y

    @staticmethod
    def fft_debayer(I):
        X,Y=np.mgrid[-I.shape[1]//2:I.shape[1]//2,-I.shape[0]//2:I.shape[0]//2]
        w=(np.abs(X)<I.shape[1]//4)*(np.abs(Y)<I.shape[0]//4)
        return np.abs(ifft2(w.T*(fftshift(fft2(I)))))


    @staticmethod
    def FWHM(Y,level=1/np.e**2):
        half_max = np.max(Y) *level
        d = np.where(np.sign(Y-half_max)>0)[0]
        if len(d)<=2:
            return -1
        return d[-1]-d[0]




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
