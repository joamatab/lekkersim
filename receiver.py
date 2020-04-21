import numpy as np
import solver
import sys 


r=0.5

#BS1=solver.Structure(model=solver.Splitter1x2())
#BS2=solver.Structure(model=solver.Splitter1x2())

BST=solver.Structure(model=solver.BeamSplitter(phase=0.5))
BSB=solver.Structure(model=solver.BeamSplitter(phase=0.5))
BSC=solver.Structure(model=solver.BeamSplitter(phase=0.5))
SPC=solver.Structure(model=solver.Splitter1x2())



Sol=solver.Solver(structures=[SPC,BSB,BSC,BST])

Sol.connect(SPC,'b0',BSB,'b1')  
Sol.connect(BSB,'b0',BSC,'b1')
Sol.connect(BSC,'b0',BST,'b1')
Sol.connect(BST,'b0',SPC,'b1')
  

pin_mapping={
    'a0': (SPC,'a0'),
    'r0': (BSC,'a0'),
    'r1': (BSC,'a1'),
    't0': (BST,'a0'),
    't1': (BST,'a1'),
    'b0': (BSB,'a0'),
    'b1': (BSB,'a1'),
}

Sol.map_pins(pin_mapping)

Sol.set_param('Lam',value=1.55)
full=Sol.solve()
new=full.get_model(pin_mapping)
#print(5*'%15.8f' % (1.55,new.get_T('a0','b0'),new.get_T('a1','b1'),new.get_T('a0','b1'),new.get_T('a1','b0')))
#print(5*'%15.8f' % (1.55,new.get_T('a0','b0'),new.get_T('a0','b1'),new.get_T('b0','a0'),new.get_T('b1','a0')))
#print(2*'%15.8f' % (1.55,new.get_T('a0','b0')))

for p in np.linspace(0.0,2.0,201):
    input_dic={'r0':0.0+0.0j,'a0':np.exp(1.0j*np.pi*p)}
    out=new.get_output(input_dic)
    print(7*'%8.4f' % (p,out['t0'],out['t1'],out['b0'],out['b1'],out['t0']-out['t1'],out['b0']-out['b1']))
