## Find appropriate unittest module
import unittest
if not hasattr(unittest, 'skipIf'):
    try: 
        import unittest2 as unittest        
    except ImportError:
        raise NotImplementedError, \
            """Tests require either the Python 2.7 or later version of unittest or
            the unittest2 module."""

import sys
from sersic import *

## Make it easy to skip long-running tests.  
## 0 = tests instantaneous
## 1 = test takes longer than 10 sec
## 2 = test takes longer than 1 min
## 3 = test takes longer than I'm willing to wait
patience = 2

def progress_tick():
    sys.stdout.write('.')
    sys.stdout.flush()

def fdiff(x,y): return abs(x/y-1)

class SersicTest(unittest.TestCase):
    def test_lum_int_2d(self):
        self.assertAlmostEqual(lum_int_2d(lambda x: x, 1, 2),
                               2*np.pi*(2**3-1**3)/3.0)

    def test_lum_int_3d(self):
        self.assertAlmostEqual(lum_int_3d(lambda x: x**2, 1, 2),
                               4*np.pi*(2**5-1**5)/5.0)

    def test_half_light_2d(self): 
        def ir(xx): return 1/(2*np.pi*xx*(1+xx)**2)
        self.assertAlmostEqual(half_light_2d(ir, np.inf), 1.0)

    def test_half_light_3d(self):
        def rho(xx): return 1/(4*np.pi*xx**2*(1+xx)**2)
        self.assertAlmostEqual(half_light_3d(rho, np.inf), 1.0)

    def test_lum_proj(self):
        def rho(rr): return 1.0/rr**2
        def ir(rp): return np.pi/rp  
        
        for rp in (0.5, 1.5):
            self.assertAlmostEqual(lum_proj(rho, rp, np.inf), ir(rp))

    def test_bm_func(self):
        global reff_max
        ro = reff_max
        ns = [0.5, 1, 2.5, 4, 7, 10]

        for nn in ns:
            ir = bm_func(nn)
            self.assertAlmostEqual(half_light_2d(ir), 1.0)
            self.assertAlmostEqual(lum_int_2d(ir, 0, ro), 1.0)
            self.assertLess(lum_int_2d(ir, ro, np.inf), 1e-3)

    def test_bm_func_ml(self):
        ns = [1, 4]
        global reff_max
        for nn in ns:
            ibm = bm_func(nn)
            i0, rs = ml_constants(nn)
            self.assertAlmostEqual(ml(1.5, nn, i0, rs),                                   
                                   ibm(1.5))
            self.assertAlmostEqual(half_light_2d(lambda xx: ml(xx, nn, i0, rs)),
                                   1.0)
            self.assertAlmostEqual(lum_int_2d(lambda xx: ml(xx, nn, i0, rs), 0.0, reff_max),
                                   1.0)

    def test_bm_bn_limits(self):
        # Test values at limits
        self.assertLess(fdiff(bm_bn(0.014,np.inf), 4.0071010589599586e-12), 1e-4)
        self.assertLess(fdiff(bm_bn(29.99,np.inf), 25.904362099799854), 1e-4)
        self.assertLess(fdiff(bm_bn(0.014,1000.0), 5.724430084228513e-13), 1e-4)
        self.assertLess(fdiff(bm_bn(29.99,1000.0), 25.75436938944069), 1e-4)

    def test_bg_constants_limits(self):
        # Test values at limits
        self.assertLess(fdiff(bg_constants(1,30)[1], 1.8069611852846725e-05), 1e-4)
        self.assertLess(fdiff(bg_constants(70,1)[1], 144.14946767410251), 1e-4)

    @unittest.skipIf(patience < 1, "Not patient enough.")
    def test_bm_bn_convergence_slow(self):

        # Failures to converge raise an exception.  Don't care what
        # the values are.

        # Using inf as outer radius
        ns = np.logspace(np.log10(0.015), np.log10(12.0), 30)        
        for nn in ns:
            bm_bn(nn, ro=np.inf)

        # Using reff_max as outer radius
        global reff_max
        for nn in ns:
            bm_bn(nn, ro=reff_max)
        
    def test_ml_lum_func(self):
        ns = (1,4)
        xs = (0.2, 0.5, 2.0, 5.0)

        for nn in ns:
            lum = ml_lum_func(nn)
            ir = bm_func(nn)
            for xx in xs:
                # Don't enforce very stringent limit b/c it's just a fitting formula
                self.assertAlmostEqual(lum_proj(lum, xx), ir(xx), places=2)

    def test_bg(self):
        ns = (1,4)
        xs = (0.5, 1.5)
        for nn in ns:
            i0,bb = bg_constants_from_bm(nn, np.inf)
            ir = bm_func(nn, np.inf)
            for xx in xs:
                self.assertAlmostEqual(bg(xx, nn, i0, bb), ir(xx))
            
    def test_bg_constants(self):
        ns = ((1,1), (3,2), (5,3), (4,1))
        
        for pp,qq in ns:
            i01,bb1 = bg_constants(pp,qq)
            i02,bb2 = bg_constants_from_bm((1.0*pp)/qq, ro=np.inf)
            self.assertLess(fdiff(bb2, bb1), 0.01)
            self.assertLess(fdiff(i02, i01), 0.01)
    
    def test_bg_lum_tot(self):
        ### Ensure that total lum is unity when constants computed
        ### from B+M solution.

        # The routine to find constants uses bg_lum_tot, so
        # we CANNOT use it or else we will mask errors.            
        ## i0, bb = bg_constants(pp, qq)

        for pp, qq, i0, bb in ((1, 1,  0.44831538163919277, 1.6783469900166608),
                               (3, 2,  1.0144075495201119,  2.6740603136964345),
                               (5, 3,  1.3483144760950312,  3.0065819755372734),
                               (4, 1, 94.482746947119537,   7.6692494422849338)):
            self.assertAlmostEqual(bg_lum_tot(pp,qq,i0,bb), 1.0)
            
    def test_bg_3d_lum_int(self):
        global reff_max
        ns = ((1,1), (3,2), (5,3), (4,1))
        xs = (0.2, 0.5, 1.0, 2.0, 5.0)

        for pp,qq in ns:  
            nn = (1.0*pp)/qq
            i0, bb = bg_constants(pp, qq)

            # Ensure that total lum is ~unity
            # Evaluating low sersics at large radii takes forever: skip it.
            if nn > 1: 
                self.assertAlmostEqual(bg_3d_lum_int(reff_max,pp,qq,i0,bb), 1.0)

            # Ensure that answer is ~close to numerically integrating
            # M+L approx.  Do this as a fractional diff b/c the approx
            # isn't necessarily great, and values compared may be far
            # from unity, so assertAlmostEqual's places arg isn't useful.
            for xx in xs:
                self.assertLess(fdiff(bg_3d_lum_int(xx,pp,qq,i0,bb),
                                      lum_int_3d(ml_lum_func(nn, ro=np.inf), 0, xx)),
                                      0.1) 
                                       
    def test_bg_lum_hi_agreement(self):
        # Test that rational and half integer functions agree
        
        ns = ((1,1), (3,2), (4,1))
        xs = (0.2, 0.5, 1.0, 2.0, 5.0)

        for pp,qq in ns:
            i0, bb = bg_constants(pp, qq)
            lum = bg_lum(pp,qq)
            lum_hi = bg_lum_hi(pp,qq)

            for xx in xs:
                self.assertAlmostEqual(lum(xx), lum_hi(xx))
                
    def test_bg_lum_gcf_reduction(self):
        xs = (0.2, 0.5, 1.0, 2.0, 5.0)
        
        lum1 = bg_lum(6,3)
        lum2 = bg_lum_hi(2,1)

        for xx in xs:
            self.assertAlmostEqual(lum1(xx), lum2(xx))

    def test_bg_lum_hi(self):
        ns = ((1,1), (3,2), (4,1))
        for pp,qq in ns:
            self.bg_lum_test(bg_lum_hi(pp, qq), pp, qq)

    def test_bg_lum(self):
        ns = ((1,1), (3,2), (5,3), (4,1))
        for pp,qq in ns:
            self.bg_lum_test(bg_lum(pp, qq), pp, qq)

    @unittest.skipIf(patience < 2, "Not patient enough.")
    def test_bg_lum_slow(self):
        
        ns = ((1,1), (3,2), (5,3), (4,1))
        for pp,qq in ns:
            self.bg_lum_slow_test(bg_lum(pp, qq), pp, qq)
            
    @unittest.skipIf(patience < 2, "Not patient enough.")
    def test_bg_lum_hi_slow(self):

        ns = ((1,1), (3,2), (4,1))
        for pp,qq in ns:
            self.bg_lum_slow_test(bg_lum_hi(pp, qq), pp, qq)

    def bg_lum_test(self, lum, pp, qq):
        xs = (0.2, 0.5, 1.0, 2.0, 5.0)

        nn = (1.0*pp)/qq

        # Ensure that answer is ~close to M+L approx
        bn = bm_bn(nn, ro=np.inf)
        ie = bm_ie(nn, bn, ro=np.inf)
        lum_approx = ml_lum_func(nn, ro=np.inf)

        for xx in xs:
            self.assertLess(fdiff(lum(xx), lum_approx(xx)), 0.05)


    def bg_lum_slow_test(self, lum, pp, qq, rmax = 30.0):
        # rmax = number of reff to carry out numerical integrals that go to large radius        
        xs = (0.2, 0.5, 1.0, 2.0, 5.0)
        nn = (1.0*pp)/qq

        # Larger sersic indicies have more light at large radius
        rmax = 10*nn  
        
        i0, bb = bg_constants(pp, qq)

        # Ensure that integrating this gives exp. for total lum
        self.assertAlmostEqual(lum_int_3d(lum, 0.0, rmax),
                               bg_lum_tot(pp,qq,i0,bb), places=2)
        progress_tick()


        # Ensure that integrating this gives exp. for total lum(r)
        for xx in xs:                
            self.assertAlmostEqual(lum_int_3d(lum, 0.0, xx),
                                   bg_3d_lum_int(xx, pp,qq,i0,bb))                                       
            progress_tick()

        # Ensure that projecting this give sersic profile compare
        # to different parameterization of sersic as a more
        # independent check
        for xx in xs:
            bn = bm_bn(nn, ro=np.inf)
            ie = bm_ie(nn, bn, ro=np.inf)
            self.assertAlmostEqual(lum_proj(lum, xx, ro=rmax), 
                                   bm(xx, nn, ie, bn), places=5)
            progress_tick()
                                
def test():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SersicTest)
    unittest.TextTestRunner().run(suite)

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    test()
