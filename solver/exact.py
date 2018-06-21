import math
import numpy as np

import config as cfg

class CVectorPrimitive1D:
    """Primitive variables vector for 1D equations"""
    def __init__(self, ro=None, u=None, v=None, w=None, p=None):
        self.ro = ro
        self.u = u        
        self.p = p

        
class CVectorPrimitive3D:
    """Primitive variables vector for 1D equations"""
    def __init__(self, ro=0., u_des=0., u_adv_1=0., u_adv_2 =0., p=0.):
        self.ro = ro
        self.u_des = u_des
        self.u_adv_1 = u_adv_1
        self.u_adv_2 = u_adv_2
        self.p = p
        

class CRPSolutionPrimitive3D:
    """Riemann problem solution vector for 1D equations"""
    def __init__(self, ro_l=None, ro_r=None, u=None, v=None, w=None, p=None, s_type=None):
        self.ro_l = ro_l
        self.ro_r = ro_r
        self.u = u
        self.v = v
        self.w = w
        self.p = p
        self.s_type = ""
        

class CExactRiemannSolver:
    """Implements exact Riemann solver for 3D equations"""
    def __init__(self, eos):
        print("Class solver.CExactRiemannSolver: Initializing exact 3D Riemann solver...", end="")
        self.eos = eos        
        print("done!")
        
    def calc_step(self, field, problem, tau):
        i_min = field.i_min
        i_max = field.i_max     
        j_min = field.j_min
        j_max = field.j_max
        k_min = field.k_min
        k_max = field.k_max        
        CONS_VECT_N_SIZE = cfg.const["CONS_VECT_N_SIZE"]
        # F = np.zeros(CONS_VECT_N_SIZE)
        # G = np.zeros(CONS_VECT_N_SIZE)
        # H = np.zeros(CONS_VECT_N_SIZE)
        dx = field.dx
        dy = field.dy
        dz = field.dz
        g = 0 # ускорение
        # Calculating fluxes
        for i in range(i_min, i_max):
            for j in range(j_min, j_max):
                for k in range(k_min, k_max):
                    field.F[i][j][k] = self.calc_F(field.U[i-1][j][k], field.U[i][j][k])
                    field.G[i][j][k] = self.calc_G(field.U[i][j-1][k], field.U[i][j][k])
                    field.H[i][j][k] = self.calc_H(field.U[i][j][k-1], field.U[i][j][k])
                    field.S[i][j][k] = 0.
        # Calculating new time-layer variables
        for i in range(i_min, i_max):
            for j in range(j_min, j_max):
                for k in range(k_min, k_max):
                    field.U_new[i][j][k] = field.U[i][j][k] - (tau/dx*(field.F[i+1][j][k]-field.F[i][j][k]) -
                                                               tau/dy*(field.G[i][j+1][k]-field.G[i][j][k]) -
									                           tau/dz*(field.H[i][j][k+1]-field.H[i][j][k])) + \
                                                              field.S[i][j][k]*tau
        for i in range(i_min, i_max):
            for j in range(j_min, j_max):
                for k in range(k_min, k_max):
                    field.U[i][j][k] = field.U_new[i][j][k]  # Почему бы не сократить --
                                                # U[i][j][k] -= tau/dx(...)+tau/dy(...)+tau/dz(...)
					                            # Неудобство при реконструкции??? Только первый порядок?



                                                # Почему бы не использовать копирование массива numpy? Должно быть
                                                # быстрее!

        field.set_bc(problem)


    def calc_F(self, U_l, U_r):
        """Calculates F intercell flux based on Riemann problem solution in X direction"""
        ro_l = U_l[0]
        u_l = U_l[1]/ro_l
        v_l = U_l[2]/ro_l
        w_l = U_l[3]/ro_l
        E_l = U_l[4]/ro_l
        e_l = E_l - .5*(u_l*u_l + v_l*v_l + w_l*w_l)
        p_l = self.eos.getp(ro_l, e_l)
        ro_r = U_r[0]
        u_r = U_r[1]/ro_r
        v_r = U_r[2]/ro_r
        w_r = U_r[3]/ro_r
        E_r = U_r[4]/ro_r
        e_r = E_r - .5*(u_r*u_r + v_r*v_r + w_r*w_r)
        p_r = self.eos.getp(ro_r, e_r)
        Q = self.calc_RP_solution(ro_l, u_l, v_l, w_l, p_l, ro_r, u_r, v_r, w_r, p_r, 0., .001)
        E = self.eos.gete(Q.ro, Q.p) + .5*(Q.u_des*Q.u_des + Q.u_adv_1*Q.u_adv_1 + Q.u_adv_2*Q.u_adv_2)
        return [Q.ro,
                Q.p + Q.ro*Q.u_des*Q.u_des,
                Q.ro*Q.u_des*Q.u_adv_1,
                Q.ro*Q.u_des*Q.u_adv_2,
                Q.u_des*(Q.p * Q.ro*E)]
        
    def calc_G(self, U_l, U_r):    
        """Calculates G intercell flux based on Riemann problem solution in Y direction"""
        ro_l = U_l[0]
        u_l = U_l[1]/ro_l
        v_l = U_l[2]/ro_l
        w_l = U_l[3]/ro_l
        E_l = U_l[4]/ro_l
        e_l = E_l - .5*(u_l*u_l + v_l*v_l + w_l*w_l)
        p_l = self.eos.getp(ro_l, e_l)
        ro_r = U_r[0]
        u_r = U_r[1]/ro_r
        v_r = U_r[2]/ro_r
        w_r = U_r[3]/ro_r
        E_r = U_r[4]/ro_r
        e_r = E_r - .5*(u_r*u_r + v_r*v_r + w_r*w_r)
        p_r = self.eos.getp(ro_r, e_r)
        Q = self.calc_RP_solution(ro_l, v_l, w_l, u_l, p_l, ro_r, v_r, w_r, u_r, p_r, 0., .001)
        E = self.eos.gete(Q.ro, Q.p) + .5*(Q.u_adv_1*Q.u_adv_1 + Q.u_des*Q.u_des + Q.u_adv_2*Q.u_adv_2)
        return [Q.ro,
                Q.ro*Q.u_adv_1*Q.u_des,
                Q.p + Q.ro*Q.u_des*Q.u_des,
                Q.ro*Q.u_des*Q.u_adv_2,
                Q.u_des*(Q.p * Q.ro*E)]
        
    def calc_H(self, U_l, U_r):    
        """Calculates H intercell flux based on Riemann problem solution in Z direction"""    
        ro_l = U_l[0]
        u_l = U_l[1]/ro_l
        v_l = U_l[2]/ro_l
        w_l = U_l[3]/ro_l
        E_l = U_l[4]/ro_l
        e_l = E_l - .5*(u_l*u_l + v_l*v_l + w_l*w_l)
        p_l = self.eos.getp(ro_l, e_l)
        ro_r = U_r[0]
        u_r = U_r[1]/ro_r
        v_r = U_r[2]/ro_r
        w_r = U_r[3]/ro_r
        E_r = U_r[4]/ro_r
        e_r = E_r - .5*(u_r*u_r + v_r*v_r + w_r*w_r)
        p_r = self.eos.getp(ro_r, e_r)
        Q = self.calc_RP_solution(ro_l, w_l, u_l, v_l, p_l, ro_r, w_r, u_r, v_r, p_r, 0., .001)
        E = self.eos.gete(Q.ro, Q.p) + .5*(Q.u_adv_1*Q.u_adv_1 + Q.u_adv_2*Q.u_adv_2 + Q.u_des*Q.u_des)
        return [Q.ro,
                Q.ro*Q.u_adv_1*Q.u_des,
                Q.ro*Q.u_adv_2*Q.u_des,
                Q.p + Q.ro*Q.u_des*Q.u_des,
                Q.u_des*(Q.p * Q.ro*E)]
        
    def calc_RP_solution(self, ro_l, u_des_l, u_adv_1_l, u_adv_2_l, p_l, ro_r, u_des_r, u_adv_1_r, u_adv_2_r, p_r, x, t):
        GAMMA = self.eos.GAMMA
        res_1d = self.solve_RP_1d(ro_l, u_des_l, p_l, ro_r, u_des_r, p_r)
        #  // V = (ro, u, v, w, p)T
        V = CVectorPrimitive3D()
        if t!=0:
            xi = x/t
        else:
            xi = x/1.e-5
        c_l = 0.
        c_r = 0.
        if ro_l != 0.:
            c_l = math.sqrt(GAMMA*p_l/ro_l)
        if ro_r != 0.:
            c_r = math.sqrt(GAMMA*p_r/ro_r)
        # Trivial case
        if res_1d.s_type == "Const":
            V.ro = ro_l
            V.u_des = u_des_l
            V.u_adv_1 = u_adv_1_l
            V.u_adv_2 = u_adv_2_l
            V.p = p_l
            return V
        #   // Vacuum
        if res_1d.s_type == "VacRW":
            V.u_adv_1 = u_adv_1_r
            V.u_adv_2 = u_adv_2_r
            xi_head = u_des_r + c_r
            xi_tail = u_des_r - 2.*c_r/(GAMMA-1.)
            if xi <= xi_tail:
                V.ro = 0.
                V.u_des = u_des_r - 2.*c_r/(GAMMA-1.)
                V.p = 0.
            elif xi < xi_head:
                V.ro = ro_r*pow(2./(GAMMA+1.) - (GAMMA-1.)/(GAMMA+1.)/c_r*(u_des_r-xi), 2./(GAMMA-1.))
                V.u_des = 2./(GAMMA+1)*(-c_r + (GAMMA-1.)/2.*u_des_r + xi)
                V.p = p_r*pow(2./(GAMMA+1.) - (GAMMA-1.)/(GAMMA+1.)/c_r*(u_des_r-xi), 2.*GAMMA/(GAMMA-1.))
            else:
                V.ro = ro_r
                V.u_des = u_des_r
                V.p = p_r
            return V
        if res_1d.s_type == "RWVac":
            V.u_adv_1 = u_adv_1_l
            V.u_adv_2 = u_adv_2_l    
            xi_head = u_des_l - c_l
            xi_tail = u_des_l + 2.*c_l/(GAMMA-1.)
            if xi >= xi_tail:
                V.ro = 0.
                V.u_des = 0.
                V.p = 0.
            elif xi > xi_head:
                V.ro = ro_l*pow(2./(GAMMA+1.)+(GAMMA-1.)/(GAMMA+1.)/c_l*(u_des_l-xi), 2./(GAMMA-1.))
                V.u_des = 2./(GAMMA+1)*(c_l + (GAMMA-1.)/2.*u_des_l + xi)
                V.p = p_l*pow(2./(GAMMA+1.)+(GAMMA-1.)/(GAMMA+1.)/c_l*(u_des_l-xi), 2.*GAMMA/(GAMMA-1.))
            else:
                V.ro = ro_l
                V.u_des = u_des_l
                V.p = p_l
            return V
        if res_1d.s_type == "RWVacRW":
            xi_head_l = u_des_l - c_l
            xi_tail_l = u_des_l + 2.*c_l/(GAMMA-1.)
            xi_head_r = u_des_r + c_r
            xi_tail_r = u_des_r - 2.*c_r/(GAMMA-1.)
            if xi <= xi_head_l:
                V.ro = ro_l
                V.u_des = u_des_l
                V.u_adv_1 = u_adv_1_l
                V.u_adv_2 = u_adv_2_l
                V.p = p_l
            elif xi < xi_tail_l:
                V.ro = ro_l*pow(2./(GAMMA+1.)+(GAMMA-1.)/(GAMMA+1.)/c_l*(u_des_l-xi), 2./(GAMMA-1.))
                V.u_des  = 2./(GAMMA+1)*(c_l + (GAMMA-1.)/2.*u_des_l + xi)
                V.u_adv_1 = u_adv_1_l
                V.u_adv_2 = u_adv_2_l
                V.p  = p_l*pow(2./(GAMMA+1.)+(GAMMA-1.)/(GAMMA+1.)/c_l*(u_des_l-xi), 2.*GAMMA/(GAMMA-1.))
            elif xi <= xi_tail_r:
                V.ro = 0.
                V.u_des = 0.
                V.u_adv_1 = 0.
                V.u_adv_2 = 0.
                V.p = 0.
            elif xi < xi_head_r:
                V.ro = ro_r*pow(2./(GAMMA+1.) - (GAMMA-1.)/(GAMMA+1.)/c_r*(u_des_r-xi), 2./(GAMMA-1.))
                V.u_des = 2./(GAMMA+1)*(-c_r + (GAMMA-1.)/2.*c_r + xi)
                V.u_adv_1 = u_adv_1_r
                V.u_adv_2 = u_adv_2_r
                V.p = p_r*pow(2./(GAMMA+1.) - (GAMMA-1.)/(GAMMA+1.)/c_r*(u_des_r-xi), 2.*GAMMA/(GAMMA-1.))
            else:
                V.ro = ro_r
                V.u_des = u_des_r
                V.u_adv_1 = u_adv_1_r
                V.u_adv_2 = u_adv_2_r
                V.p = p_r
            return V
        c_l_local = math.sqrt(GAMMA*res_1d.p/res_1d.ro_l)
        c_r_local = math.sqrt(GAMMA*res_1d.p/res_1d.ro_r)
        #   // If non-vacuum zone -- let the point be to the left from the contact gap (xiContact = res.v)
        if xi < res_1d.u:
            V.u_adv_1 = u_adv_1_l
            V.u_adv_2 = u_adv_2_l
            if res_1d.s_type == "SWSW" or res_1d.s_type == "SWRW":
                xi_front = u_des_l - c_l*math.sqrt((GAMMA+1.)/2./GAMMA*res_1d.p/p_l + (GAMMA-1.)/2./GAMMA)
                if xi < xi_front:
                    V.ro = ro_l
                    V.u_des = u_des_l
                    V.p = p_l
                else:
                    V.ro = res_1d.ro_l
                    V.u_des = res_1d.u
                    V.p = res_1d.p
            elif res_1d.s_type == "RWSW" or res_1d.s_type == "RWRW":
                xi_head = u_des_l - c_l
                xi_tail = res_1d.u - c_l_local
                if xi <= xi_head:
                    V.ro = ro_l
                    V.u_des = u_des_l
                    V.p = p_l
                elif xi >= xi_tail:
                    V.ro = res_1d.ro_l
                    V.u_des = res_1d.u
                    V.p = res_1d.p
                else:
                    V.ro = ro_l*pow(2./(GAMMA+1.)+(GAMMA-1.)/(GAMMA+1.)/c_l*(u_des_l-xi), 2./(GAMMA-1.))
                    V.u_des = 2./(GAMMA+1)*(c_l + (GAMMA-1.)/2.*u_des_l + xi)
                    V.p = p_l * pow(2. / (GAMMA + 1.) + (GAMMA - 1.) / (GAMMA + 1.) / c_l * (u_des_l - xi),
                                    2. * GAMMA / (GAMMA - 1.))
        # Let point be to the right from the contact gap (xiContact = res.v)
        else:
            V.u_adv_1 = u_adv_1_r
            V.u_adv_2 = u_adv_2_r
            if res_1d.s_type == "RWSW" or res_1d.s_type == "SWSW":
                xi_front = u_des_r + c_r*math.sqrt((GAMMA+1.)/2./GAMMA*res_1d.p/p_r + (GAMMA-1.)/2./GAMMA)
                if xi > xi_front:
                    V.ro = ro_r
                    V.u_des = u_des_r
                    V.p = p_r
                else:
                    V.ro = res_1d.ro_r
                    V.u_des = res_1d.u
                    V.p = res_1d.p
            elif res_1d.s_type == "RWRW" or res_1d.s_type == "SWRW":
                xi_head = u_des_r + c_r
                xi_tail = res_1d.u + c_r_local
                if xi >= xi_head:
                    V.ro = ro_r
                    V.u_des = u_des_r
                    V.p = p_r
                elif xi <= xi_tail:
                    V.ro = res_1d.ro_r
                    V.u_des = res_1d.u
                    V.p = res_1d.p
                else:
                    V.ro = ro_r*pow(2./(GAMMA+1.) - (GAMMA-1.)/(GAMMA+1.)/c_r*(u_des_r-xi), 2./(GAMMA-1.))
                    V.u_des = 2./(GAMMA+1)*(-c_r + (GAMMA-1.)/2.*u_des_r + xi)
                    V.p = p_r*pow(2./(GAMMA+1.) - (GAMMA-1.)/(GAMMA+1.)/c_r*(u_des_r-xi), 2.*GAMMA/(GAMMA-1.))
        return V    
    
    def solve_RP_1d(self, ro_l, u_l, p_l, ro_r, u_r, p_r):
        """Function finds resulting ro, u, p of 1d Riemann task solving nonlinear equation by tangentials method of Newton"""
        GAMMA = self.eos.GAMMA
        res = CRPSolutionPrimitive3D(0., 0., 0., 0., 0., 0., "")
        tol = 1.e-6
        c_l = 0.
        c_r = 0.
        if ro_l != 0.:
            c_l = math.sqrt(GAMMA*p_l/ro_l)
        if ro_r != 0.:
            c_r = math.sqrt(GAMMA*p_r/ro_r)
        # Trivial case U_l = U_r
        if ro_l == ro_r and u_l == u_r and p_l == p_r:
            res.s_type = "Const"
            res.ro_l = ro_l
            res.ro_r = ro_r
            res.p = p_l
            res.u = u_l
            return res
        # Vacuum at the left side
        if ro_l == 0.:
            res.s_type = "VacRW"
            res.ro_l = 0.
            res.ro_r = ro_r
            res.p = 0.
            res.u = u_r - 2.*c_r/(GAMMA-1.)
            return res
        # Vacuum at the right side
        if ro_r == 0.:
            res.s_type = "RWVac"
            res.ro_l  = ro_l
            res.ro_r  = 0.
            res.p = 0.
            res.u = u_l + 2.*c_l/(GAMMA-1.)
            return res
        # Two rarefaction waves generating vacuum
        if 2.*c_l/(GAMMA-1.) + 2.*c_r/(GAMMA-1.) < u_r-u_l:
            res.type = "RWVacRW"
            res.ro_l = 0.
            res.ro_r = 0.
            res.u = 0.
            res.p = 0.
            return res
        # General case -- tangentials
        # fl_min = fl(p_l, ro_l, u_l, p_l) + fr(p_l, ro_r, u_r, p_r) + u_r-u_l
        # fr_max = fl(p_r, ro_l, u_l, p_l) + fr(p_r, ro_r, u_r, p_r) + u_r-u_l
        # Initial approximation
        p = p_l/2.
        it_c = 0
        while True:
            p_prev = p
            p = p_prev - \
            (self.fl(p_prev, ro_l, u_l, p_l) + self.fr(p_prev, ro_r, u_r, p_r) + u_r - u_l) / \
            (self.dfldp(p_prev, ro_l, u_l, p_l) + self.dfrdp(p_prev, ro_r, u_r, p_r))
            if p <= 0.:
                p = tol
            it_c += 1
            if math.fabs(2*(p-p_prev)/(p+p_prev))<=tol:
                break
        res.p = p
        res.u = 0.5*(u_l + u_r) + 0.5*(self.fr(p, ro_r, u_r, p_r) - self.fl(p, ro_l, u_l, p_l))
        if p < p_l and p > p_r:
            res.s_type = "RWSW"
            res.ro_l  = ro_l*pow(res.p/p_l, 1./GAMMA)
            res.ro_r  = ro_r*(res.p/p_r + (GAMMA-1.)/(GAMMA+1.))/((GAMMA-1.)/(GAMMA+1.)*res.p/p_r + 1.)
        elif p <= p_l and p <= p_r:
            res.s_type = "RWRW"
            res.ro_l = ro_l*pow(res.p/p_l, 1./GAMMA)
            res.ro_r = ro_r*pow(res.p/p_r, 1./GAMMA)
        elif p > p_l and p < p_r:
            res.s_type = "SWRW"
            res.ro_l = ro_l*(res.p/p_l + (GAMMA-1.)/(GAMMA+1.))/((GAMMA-1.)/(GAMMA+1.)*res.p/p_l + 1.)
            res.ro_r = ro_r*pow(res.p/p_r, 1./GAMMA)
        else:
            res.s_type = "SWSW"
            res.ro_l = ro_l*(res.p/p_l + (GAMMA-1.)/(GAMMA+1.))/((GAMMA-1.)/(GAMMA+1.)*res.p/p_l + 1.)
            res.ro_r = ro_r*(res.p/p_r + (GAMMA-1.)/(GAMMA+1.))/((GAMMA-1.)/(GAMMA+1.)*res.p/p_r + 1.)
#   //Testing (no vacuum)
#   /*double L =  - fL(p, roL, vL, pL);
#   double R = fR(p, roR, vR, pR) + vR - vL;
#   double delta = fabs((L-R)/0.5/(L+R));
#   double LToro = - fL(res.p, roL, vL, pL);
#   double RToro = fR(res.p, roR, vR, pR) + vR - vL;
#   double deltaToro = fabs((LToro-RToro)/0.5/(LToro+RToro));*/
        return res

    def fl(self, p, ro_l, u_l, p_l):
        GAMMA = self.eos.GAMMA
        if p>p_l:
            al = 2./(GAMMA+1)/ro_l
            bl = (GAMMA-1.)/(GAMMA+1.)*p_l
            f = (p-p_l) * math.sqrt(al/(p+bl))
            return f
        else:
            c_l = math.sqrt(GAMMA*p_l/ro_l)
            f = 2.*c_l/(GAMMA-1.) * ( (pow(p/p_l, (GAMMA-1.)/2./GAMMA)) - 1. )
            return f

    def dfldp(self, p, ro_l, u_l, p_l):
        GAMMA = self.eos.GAMMA
        if p>p_l:
            al = 2./(GAMMA+1)/ro_l
            bl = (GAMMA-1.)/(GAMMA+1.)*p_l
            dfdp = math.sqrt(al/(p+bl)) * (1. - (p-p_l)/2./(p+bl))
            return dfdp
        else:
            c_l = math.sqrt(GAMMA*p_l/ro_l)
            dfdp = c_l/p_l/GAMMA*pow(p/p_l, -(GAMMA+1)/2./GAMMA)
            return dfdp

    def fr(self, p, ro_r, u_r, p_r):
        GAMMA = self.eos.GAMMA
        if p > p_r:
            ar = 2./(GAMMA+1)/ro_r
            br = (GAMMA-1.)/(GAMMA+1.)*p_r
            f = (p-p_r) * math.sqrt(ar/(p+br))
            return f
        else:
            c_r = math.sqrt(GAMMA*p_r/ro_r)
            f = 2.*c_r/(GAMMA-1.) * ((pow(p/p_r, (GAMMA-1.)/2./GAMMA)) - 1.)
            return f

    def dfrdp(self, p, ro_r, u_r, p_r):
        GAMMA = self.eos.GAMMA
        if p > p_r:
            AR = 2./(GAMMA + 1) / ro_r
            BR = (GAMMA - 1.) / (GAMMA + 1.) * p_r
            dfdp = math.sqrt(AR/(p+BR)) * (1. - (p-p_r)/2./(p+BR))
            return dfdp
        else:
            cR = math.sqrt(GAMMA * p_r / ro_r)
            dfdp = cR/p_r / GAMMA * pow(p / p_r, -(GAMMA + 1) / 2. / GAMMA)
            return dfdp