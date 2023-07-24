import numpy as np

class beam_math:
    
    noise_map=[[0]]
    calibration_coeffs=(8,21,34)
    def __init__(self,Nx,Ny):
        self.update_grid(Nx,Ny)
    
    def update_grid(self,Nx,Ny):
        self.I_grid,self.J_grid=np.meshgrid(\
			np.arange(Nx),\
			np.arange(Ny)
		)
        self.I_grid_sqr=self.I_grid*self.I_grid
        self.J_grid_sqr=self.J_grid*self.J_grid
    def RMS(self,img):
        P=np.sum(img,dtype='uint64')
        mx=np.sum(img*self.I_grid,dtype='uint64')
        my=np.sum(img*self.J_grid,dtype='uint64')
        Dx=np.sum(img*self.I_grid_sqr,dtype='uint64')
        Dy=np.sum(img*self.J_grid_sqr,dtype='uint64')
        mx/=P
        my/=P
        RMS_x=2*np.sqrt(Dx/P-mx*mx)
        RMS_y=2*np.sqrt(Dy/P-my*my)
        return P,mx,my,RMS_x,RMS_y

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
