import numpy as np
import pytest
import importlib.util
spec = importlib.util.spec_from_file_location("solver", "../solver/__init__.py")
sv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sv)


def test_single():
    ps=sv.PhaseShifter()

    with sv.Solver() as S1:
        ps.put()
        sv.raise_pins()

    with sv.Solver() as S2:
        ps.put(param_mapping={'PS': 'PS2'})
        sv.raise_pins()

    with sv.Solver() as S3:
        S1.put(param_mapping={'PS': 'PS2'})
        sv.raise_pins()

    assert S1.solve().get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert S1.solve(PS=0.5).get_PH('a0','b0') == pytest.approx(0.5*np.pi, 1e-8)
    assert S1.solve().get_PH('a0','b0') == pytest.approx(0.0, 1e-8)

    assert S2.solve().get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert S2.solve(PS=0.5).get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert S2.solve(PS2=0.5).get_PH('a0','b0') == pytest.approx(0.5*np.pi, 1e-8)
    assert S2.solve().get_PH('a0','b0') == pytest.approx(0.0, 1e-8)

    assert S3.solve().get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert S3.solve(PS=0.5).get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert S3.solve(PS2=0.5).get_PH('a0','b0') == pytest.approx(0.5*np.pi, 1e-8)
    assert S3.solve().get_PH('a0','b0') == pytest.approx(0.0, 1e-8)


def test_double():
    ps=sv.PhaseShifter()

    with sv.Solver() as S1:
        ps1= ps.put()
        ps2= ps.put()

        sv.Pin('a0').put(ps1.pin['a0'])
        sv.Pin('b0').put(ps1.pin['b0'])
        sv.Pin('a1').put(ps2.pin['a0'])
        sv.Pin('b1').put(ps2.pin['b0'])

    M=S1.solve()
    assert M.get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.0, 1e-8)

    M=S1.solve(PS=0.5)
    assert M.get_PH('a0','b0') == pytest.approx(0.5*np.pi, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.5*np.pi, 1e-8)

def test_double2():
    ps=sv.PhaseShifter()

    with sv.Solver() as S1:
        ps1= ps.put()
        ps2= ps.put(param_mapping={'PS': 'PS2'})

        sv.Pin('a0').put(ps1.pin['a0'])
        sv.Pin('b0').put(ps1.pin['b0'])
        sv.Pin('a1').put(ps2.pin['a0'])
        sv.Pin('b1').put(ps2.pin['b0'])

    M=S1.solve()
    assert M.get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.0, 1e-8)

    M=S1.solve(PS=0.5)
    assert M.get_PH('a0','b0') == pytest.approx(0.5*np.pi, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.0, 1e-8)

    M=S1.solve(PS2=0.5)
    assert M.get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.5*np.pi, 1e-8)

    M=S1.solve()
    assert M.get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.0, 1e-8)

    with sv.Solver() as S2:
        S1.put()
        sv.raise_pins()

    M=S2.solve()
    assert M.get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.0, 1e-8)

    M=S2.solve(PS=0.5)
    assert M.get_PH('a0','b0') == pytest.approx(0.5*np.pi, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.0, 1e-8)

    M=S2.solve(PS2=0.5)
    assert M.get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.5*np.pi, 1e-8)

    M=S2.solve()
    assert M.get_PH('a0','b0') == pytest.approx(0.0, 1e-8)
    assert M.get_PH('a1','b1') == pytest.approx(0.0, 1e-8)



def test_complex():
    def func(wl,pol,**kwargs):
        return 3.2-0.1*pol

    with sv.Solver(name='EOBiasSection') as ActivePhaseShifter:
        wg = sv.UserWaveguide(500.0, func=func, param_dic={'wl': None},
                              allowedmodes={'TE': {'pol': 0}, 'TM': {'pol': 1}}).put()
        ps = sv.PhaseShifter().expand_mode(['TE', 'TM']).put()
        
        sv.connect(wg.pin['b0_TE'],ps.pin['a0_TE'])
        sv.connect(wg.pin['b0_TM'],ps.pin['a0_TM'])

        sv.Pin('o1_TE').put(wg.pin['a0_TE'])
        sv.Pin('o1_TM').put(wg.pin['a0_TM'])
        sv.Pin('o2_TE').put(ps.pin['b0_TE'])
        sv.Pin('o2_TM').put(ps.pin['b0_TM'])

        
    with sv.Solver(name='EOBiasTwinSection') as TwinPhaseShifter:
        a1= ActivePhaseShifter.put(param_mapping={'PS': 'TOP'})
        a2= ActivePhaseShifter.put(param_mapping={'PS': 'BOTTOM'})
        
        for l in [1,2]:
            for pol in ['TE','TM']:
                sv.Pin(f'o{l}_{pol}').put(a1.pin[f'o{l}_{pol}'])
                sv.Pin(f'o{l + 2}_{pol}').put(a2.pin[f'o{l}_{pol}'])
                
    ActivePhaseShifter.solve(wl=1.55)
    TwinPhaseShifter.solve(wl=1.55)
    assert ActivePhaseShifter.default_params == {'PS': 0.0, 'wl': None}
    assert TwinPhaseShifter.default_params == {'TOP': 0.0, 'BOTTOM': 0.0, 'wl': None}


def test_params():
    with sv.Solver(name='MZM_BB') as MZM_BB_sol:
        BM=sv.BeamSplitter()
        WG=sv.Waveguide(L=500,n=2.5)
        PS=sv.PhaseShifter()
        AT=sv.Attenuator(loss=0.0)

        bm1= BM.put()
        t_= WG.put('a0', bm1.pin['b0'])
        t_= PS.put('a0', t_.pin['b0'], param_mapping={'PS': 'PS1'})
        t_= PS.put('a0', t_.pin['b0'], param_mapping={'PS': 'DP'})
        t_= AT.put('a0', t_.pin['b0'])
        bm2= BM.put('a0', t_.pin['b0'])
        t_= WG.put('a0', bm1.pin['b1'])
        t_= PS.put('a0', t_.pin['b0'], param_mapping={'PS': 'PS2'})
        t_= AT.put('a0', t_.pin['b0'])
        sv.connect(t_.pin['b0'],bm2.pin['a1'])

        sv.Pin('a0').put(bm1.pin['a0'])
        sv.Pin('a1').put(bm1.pin['a1'])
        sv.Pin('b0').put(bm2.pin['b0'])
        sv.Pin('b1').put(bm2.pin['b1'])

        sv.set_default_params({'PS1':0.0, 'PS2': 0.5, 'DP' : 0.0})

        psl=np.linspace(0.0,1.0,5)

        T=[MZM_BB_sol.solve(wl=1.55, DP=ps, PS1=0.0, PS2=0.0).get_T('a0','b0') for ps in psl]
        assert np.allclose(T,np.sin(0.5*np.pi*psl)**2.0)
        T=[MZM_BB_sol.solve(wl=1.55, DP=ps, PS1=0.0, PS2=0.5).get_T('a0','b0') for ps in psl]
        assert np.allclose(T,np.sin((0.5*psl-0.25)*np.pi)**2.0)
        T=[MZM_BB_sol.solve(wl=1.55, DP=ps).get_T('a0','b0') for ps in psl]
        assert np.allclose(T,np.sin((0.5*psl-0.25)*np.pi)**2.0)


def test_renaming():
    with sv.Solver() as S:
        ps = sv.PhaseShifter().put()
        S.add_param('PS', lambda PW: 0.1*PW, {'PW': 0.0})
        sv.raise_pins()
    data=S.solve(wl=1.55, PW = np.linspace(0.0,10.0,11)).get_data('a0','b0')
    assert S.default_params == {'wl' : None, 'PW' : 0.0}
    assert np.allclose(data['Phase'].to_numpy(), np.linspace(0.0, np.pi, 11))  

def test_renaming_hierarchical():
    with sv.Solver() as TH_PS:
        ps = sv.PhaseShifter().put()
        TH_PS.add_param('PS', lambda PW: 0.1*PW, {'PW': 0.0})
        sv.raise_pins()

    with sv.Solver() as MZM:
        BM = sv.BeamSplitter()
        bm1 = BM.put()
        ps1 = TH_PS.put('a0', bm1.pin['b0'], param_mapping={'PW': 'PW1'})
        ps2 = TH_PS.put('a0', bm1.pin['b1'], param_mapping={'PW': 'PW2'})
        bm2 = BM.put('a0', ps1.pin['b0'])
        sv.connect(ps2.pin['b0'], bm2.pin['a1'])
        sv.raise_pins()

    data=MZM.solve(wl=1.55, PW1 = np.linspace(0.0,10.0,11)).get_data('a0','b0') 
    assert MZM.default_params == {'wl' : None, 'PW1' : 0.0, 'PW2' : 0.0}
    assert np.allclose(data['T'].to_numpy(), np.sin(0.5*np.linspace(0.0,1.0,11)*np.pi)**2.0)

def test_renaming_introspection():
    with sv.Solver() as S:
        ps = sv.PhaseShifter().put()
        sv.add_param('PS', lambda PW=0.0: 0.1*PW)
        sv.raise_pins()
    data=S.solve(wl=1.55, PW = np.linspace(0.0,10.0,11)).get_data('a0','b0')
    assert S.default_params == {'wl' : None, 'PW' : 0.0}
    assert np.allclose(data['Phase'].to_numpy(), np.linspace(0.0, np.pi, 11))  


if __name__ == '__main__':
    pytest.main([__file__, '-s', '-v'])  # -s: show print output