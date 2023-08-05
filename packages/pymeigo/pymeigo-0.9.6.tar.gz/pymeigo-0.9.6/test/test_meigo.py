from pymeigo import MEIGO, rosen_for_r


def test_meigo():
    m = MEIGO(f=rosen_for_r)
    print m
    m.run(x_U=[2,2], x_L=[-1,-1])
    m.plot()
    print m
