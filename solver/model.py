import numpy as np
from solver.scattering import S_matrix
import solver.structure
from solver import sol_list
from copy import deepcopy


class model:
    def __init__(self,pin_list=[],param_dic={}):
        self.pin_dic={}
        for i,pin in enumerate(pin_list):
            self.pin_dic[pin]=i
        self.N=len(pin_list)
        self.S=np.identity(self.N,complex)
        self.param_dic=param_dic

    def create_S(self):
        return self.S

    def get_T(self,pin1,pin2):
        return np.abs(self.S[self.pin_dic[pin1],self.pin_dic[pin2]])**2.0

    def get_PH(self,pin1,pin2):
        return np.angle(self.S[self.pin_dic[pin1],self.pin_dic[pin2]])

    def get_A(self,pin1,pin2):
        return self.S[self.pin_dic[pin1],self.pin_dic[pin2]]


    def get_output(self,input_dic,power=True):
        l1=list(self.pin_dic.keys())
        l2=list(input_dic.keys())
        for pin in l2:
            l1.remove(pin)
        if l1!=[]:
            #print('WARNING: Not all input pin provided, assumed 0')
            pass
            for pin in l1:
                input_dic[pin]=0.0+0.0j
        u=np.zeros(self.N,complex)
        for pin,i in self.pin_dic.items():
            u[i]=input_dic[pin]
        #for pin,i in self.pin_dic.items():
        #    print(pin,i,u[i])
        d=np.dot(self.S,u)
        out_dic={}
        for pin,i in self.pin_dic.items():
            if power:
                out_dic[pin]=np.abs(d[i])**2.0
            else:
                out_dic[pin]=d[i]
        return out_dic

    def put(self,pins=None,pint=None,param_mapping={}):
        ST=solver.structure.Structure(model=deepcopy(self),param_mapping=param_mapping)
        sol_list[-1].add_structure(ST)
        if (pins is not None) and (pint is not None):
            sol_list[-1].connect(ST,pins,pint[0],pint[1])
        return ST

    def __str__(self):
        return f'Model object (id={id(self)}) with pins: {list(self.pin_dic)}'
                                       
                
class Waveguide(model):
    def __init__(self,L,wl=1.0,n=1.0):
        self.pin_dic={'a0':0,'b0':1}        
        self.N=2
        self.S=np.identity(self.N,complex)
        self.L=L        
        self.param_dic={}
        self.param_dic['wl']=wl
        self.n=n


    def create_S(self):
        wl=self.param_dic['wl']
        n=self.n
        self.S=np.zeros((self.N,self.N),complex)
        self.S[0,1]=np.exp(2.0j*np.pi*n/wl*self.L)
        self.S[1,0]=np.exp(2.0j*np.pi*n/wl*self.L)
        return self.S

    def __str__(self):
        return f'Model of waveguide of lenght {self.L:.3f} and index {self.n:.3f} (id={id(self)})'  

class GeneralWaveguide(model):
    def __init__(self,L,Neff,R=None,w=None, wl=None, pol=None):
        self.pin_dic={'a0':0,'b0':1}        
        self.N=2
        self.Neff=Neff
        self.L=L
        self.param_dic={}
        self.param_dic['R']=R
        self.param_dic['w']=w
        self.param_dic['wl']=wl
        self.param_dic['pol']=pol
        
    def create_S(self):
        wl=self.param_dic['wl']
        n=self.Neff(**self.param_dic)
        self.S=np.zeros((self.N,self.N),complex)
        self.S[0,1]=np.exp(2.0j*np.pi*n/wl*self.L)
        self.S[1,0]=np.exp(2.0j*np.pi*n/wl*self.L)
        return self.S

    def __str__(self):
        return f'Model of waveguide of lenght {self.L:.3} (id={id(self)})'        


class BeamSplitter(model):
    def __init__(self,phase=0.5):
        self.pin_dic={'a0':0,'a1':1,'b0':2,'b1':3}        
        self.N=4
        self.S=np.zeros((self.N,self.N),complex)
        self.phase=phase
        self.param_dic={}
        p1=np.pi*self.phase
        p2=np.pi*(1.0-self.phase)
        #self.S[:2,2:]=1.0/np.sqrt(2.0)*np.array([[1.0,np.exp(1.0j*p1)],[-np.exp(-1.0j*p1),1.0]])
        #self.S[2:,:2]=1.0/np.sqrt(2.0)*np.array([[1.0,-np.exp(1.0j*p1)],[np.exp(-1.0j*p1),1.0]])
        self.S[:2,2:]=1.0/np.sqrt(2.0)*np.array([[np.exp(1.0j*p1),1.0],[-1.0,np.exp(-1.0j*p1)]])
        self.S[2:,:2]=1.0/np.sqrt(2.0)*np.array([[np.exp(-1.0j*p1),1.0],[-1.0,np.exp(1.0j*p1)]])



class GeneralBeamSplitter(model):
    def __init__(self,ratio=0.5,phase=0.5):
        self.pin_dic={'a0':0,'a1':1,'b0':2,'b1':3}        
        self.N=4
        self.ratio=ratio
        self.phase=phase
        p1=np.pi*self.phase
        c=np.sqrt(self.ratio)
        t=np.sqrt(1.0-self.ratio)
        self.S=np.zeros((self.N,self.N),complex)
        self.param_dic={}
        #self.S[:2,2:]=np.array([[t,c],[c,-t]])
        #self.S[2:,:2]=np.array([[t,c],[c,-t]])
        #self.S[:2,2:]=np.array([[t,c*np.exp(1.0j*p1)],[-c*np.exp(-1.0j*p1),t]])
        #self.S[2:,:2]=np.array([[t,-c*np.exp(1.0j*p1)],[c*np.exp(-1.0j*p1),t]])
        self.S[:2,2:]=np.array([[t*np.exp(1.0j*p1),c],[-c,t*np.exp(-1.0j*p1)]])
        self.S[2:,:2]=np.array([[t*np.exp(-1.0j*p1),c],[-c,t*np.exp(1.0j*p1)]])

    def __str__(self):
        return f'Model of beam-splitter with ratio {self.ratio:.3} (id={id(self)})'      
    
class Splitter1x2(model):
    def __init__(self):
        self.pin_dic={'a0':0,'b0':1,'b1':2}        
        self.N=3
        self.S=1.0/np.sqrt(2.0)*np.array([[0.0,1.0,1.0],[1.0,0.0,0.0],[1.0,0.0,0.0]],complex)
        self.param_dic={}

class Splitter1x2Gen(model):
    def __init__(self,cross=0.0,phase=0.0):
        self.pin_dic={'a0':0,'b0':1,'b1':2}        
        self.N=3
        self.param_dic={}
        c=np.sqrt(cross)
        t=np.sqrt(0.5-cross)
        p1=np.pi*phase
        self.S=np.array([[0.0,t,t],[t,0.0,c*np.exp(1.0j*p1)],[t,c*np.exp(-1.0j*p1),0.0]],complex)

class PhaseShifter(model):
    def __init__(self,param_name='PS'):
        self.param_dic={}
        self.pin_dic={'a0':0,'b0':1}        
        self.N=2
        self.pn=param_name
        self.param_dic={}
        self.param_dic[param_name]=0.5    


    def create_S(self):
        self.S=np.zeros((self.N,self.N),complex)
        self.S[0,1]=np.exp(1.0j*np.pi*self.param_dic[self.pn])
        self.S[1,0]=np.exp(1.0j*np.pi*self.param_dic[self.pn])
        return self.S

    def __str__(self):
        return f'Model of variable phase shifter (id={id(self)})'  

class PolRot(model):
    def __init__(self,angle=None,angle_name='angle'):
        self.pin_dic={'a0_TE':0, 'a0_TM':1, 'b0_TE':2, 'b0_TM':3}        
        self.N=4
        self.param_dic={}
        if angle is None:
            self.fixed=False
            self.angle_name=angle_name
            self.param_dic={angle_name: 0.0}
        else:
            self.fixed=True
            c=np.cos(np.pi*angle/180.0)
            s=np.sin(np.pi*angle/180.0)
            self.S=np.zeros((self.N,self.N),complex)
            self.S[:2,2:]=np.array([[c,s],[-s,c]])
            self.S[2:,:2]=np.array([[c,-s],[s,c]])

    def create_S(self):
        if self.fixed:
            return self.S
        else:
            angle=self.param_dic[self.angle_name]
            c=np.cos(np.pi*angle/180.0)
            s=np.sin(np.pi*angle/180.0)
            S=np.zeros((self.N,self.N),complex)
            S[:2,2:]=np.array([[c,s],[-s,c]])
            S[2:,:2]=np.array([[c,-s],[s,c]])
            return S

class Attenuator(model):
    def __init__(self,loss=0.0):
        self.param_dic={}
        self.pin_dic={'a0':0,'b0':1}        
        self.N=2
        self.loss=loss
        self.S=np.zeros((self.N,self.N),complex)
        self.S[0,1]=10.0**(-0.1*loss)
        self.S[1,0]=10.0**(-0.1*loss)

class Mirror(model):
    def __init__(self,ref=0.5,phase=0.0):
        self.pin_dic={'a0':0,'b0':1}        
        self.param_dic={}
        self.N=2
        self.ref=ref
        self.phase=phase
        t=np.sqrt(self.ref)
        c=np.sqrt(1.0-self.ref)
        p1=np.pi*self.phase
        self.S=np.array([[t*np.exp(1.0j*p1),c],[-c,t*np.exp(-1.0j*p1)]],complex)


class PerfectMirror(model):
    def __init__(self,phase=0.0):
        self.pin_dic={'a0':0}      
        self.param_dic={}  
        self.N=1
        self.phase=phase
        p1=np.pi*self.phase
        self.S=np.array([[np.exp(1.0j*p1)]],complex)

class FPR_NxM(model):
    def __init__(self,N,M,phi=0.1):
        self.param_dic={}  
        self.pin_dic={f'a{i}':i for i in range(N)}
        self.pin_dic.update({f'b{i}': N+i for i in range(M)}) 
        Sint=np.zeros((N,M),complex)
        for i in range(N):
            for j in range(M):     
                Sint[i,j]=np.exp(-1.0j*np.pi*phi*(i-0.5*N+0.5)*(j-0.5*M+0.5))
        Sint2=np.conj(np.transpose(Sint))
        self.S=np.concatenate([np.concatenate([np.zeros((N,N),complex),Sint/np.sqrt(M)],axis=1),np.concatenate([Sint2/np.sqrt(N),np.zeros((M,M),complex)],axis=1)],axis=0)        



