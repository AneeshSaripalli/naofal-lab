import numpy as np
from numpy import matmul as mul
from numpy import subtract as sub

from numpy.linalg import inv
from scipy.spatial.transform import Rotation as R


# Translation Homogenous Mapping

MAT_B1 = np.array([
    [2.22711,	-0.226531,	-0.0671484],
    [6.45367  ,  -3.57227,    0.0133328],
    [3.50909  ,  -2.01472   , -0.0777887]
]).T

MAT_R1 = np.array([
    [0.901928 ,   0.23471,    0.121155],
    [5.50031 ,   -2.74337,    0.381287],
    [2.3099     ,  -1.40638 ,   0.134852]
]).T

MAT_R2 = np.array([
    [1.38289   , 0.205411 ,   0.186091],
    [4.36434 ,   -0.0080363 ,   0.432257],
    [6.31585  ,  0.684121   , 0.626229]
]).T

MAT_B2 = np.array([
    [2.72829 ,   -0.283092,    -0.0316143],
    [5.64502  ,  -0.762065,    0.0183434],
    [7.31903  ,  -0.230759  ,  0.0504592]
]).T


"""
MAT_B1 = np.array([
    [0.0888124,    0.120149 ,   0.123082],
    [0.0251261 ,   0.49067  ,  0.29864],
    [-0.000424148,    -0.314587,    0.13486]
]).T

MAT_R1 = np.array([
    [0.0469091  ,  0.0205414  ,  0.143977],
    [-0.056493   , 0.434341  ,  0.206382],
    [-0.0167119  ,  -0.394242 ,   0.210267]
]).T

MAT_R2 = np.array([
    [ 0.124649  ,  -0.279174    ,0.00398059],
    [ 0.144597   , -0.361941   , 0.479221],
    [0.00623608   , 0.0226165 ,   0.263949]
]).T

MAT_B2 = np.array([
    [0.13727   , -0.231298   , -0.146748],
    [ 0.152774 ,   -0.298024 ,   0.386462],
    [0.0285026 ,   0.173174  ,  -0.438944]
]).T
"""

"""
    Solving homogenous matrix mapping between
        road camera coordinate from and back camera coordinate frame.
    Equation is R * mat_road + t * I = mat_back
        r is a 3x3 matrix with the columns corresponding to the pre-transformed translations (relative to mat_back)
        R is an unknown rigid 3x3 rotation matrix
        t is the unknown 1x3 translation between origins of the coordinate frames
        b is a 3x3 matrix with the columns corresponding to the post-transformed translation (relative to mat_road)
    Math is as follows:
        Assume the homogenous matrix mapping exists:
            Let T be the matrix consisting of the 3 columns [t t t]
                where t is defined as earlier
            
            Then the change of basis can be defined by
                R * o + T = p with knowns o & p and unknowns R & T
                    System with 2 unknowns requires 2 equations
            We require a second system with a pre & post transform matrix
                Note our R & T matrices stay constant, and assume our bases
                    o_1, o_2, p_1, & p_2 are invertible (equiv. to being of rank 3)
                Our system is defined as follows:

                    R * o_1 + T = p_1
                    R * o_2 + T = p_2

                Right multiplying by inv[o_1] on the first eq. yields
                    R + T * inv[o_1] = p_1 * inv[o_1]
                
                Similiarly on the second eq., mulitply by inv[o_2]
                    R + T * inv[o_2] = p_2 * inv[o_2]

                Subtracting the two equations yields
                    T * (inv[o_1] - inv[o_2]) = p_1 * inv[o_1] - p_2 * inv[o_2]
                
                Right multiply by inv[(inv[o_1] - inv[o_2])], yielding
                    T  = (p_1 * inv[o_1] - p_2 * inv[o_2])(inv[(inv[o_1] - inv[o_2])])

        Substituting into equation 1 (2 works equally as well) yields 
                R = p_1 * inv[o_1] - T * inv[o_1]

        Denote R_1 to be the rotation derived by substitution into eq. 1
            and R_2 to be the rotation derived by substitution into eq.2
        Diff = R_1 - R_2 (component-wise subtractiob)
        AVG = (R_1 + R_2) / 2 (component-wise addition and division) 

        Though T should theoretically be of rank 1 (repeated columns of a translate vector),
            experiment-based data may not fit as nicely for obvious reasons. Interpret T as
            necessary.

    This function returns (AVG, T, Diff)
"""
def calc_basis_change(orig_basis_1, trans_basis_1, orig_basis_2, trans_basis_2):
    road1_inv = inv(orig_basis_1)
    road2_inv = inv(orig_basis_2)

    mat_translate_pre_mult = sub(mul(trans_basis_1, road1_inv), mul(trans_basis_2, road2_inv))
    mat_translate = mul(mat_translate_pre_mult, inv(sub(road1_inv, road2_inv)))

    ROT_APPRX_1 = sub(mul(trans_basis_1, road1_inv), mul(mat_translate, road1_inv))
    ROT_APPRX_2 = sub(mul(trans_basis_2, road2_inv), mul(mat_translate, road2_inv))
    
    AVG = (ROT_APPRX_1 + ROT_APPRX_2) / 2

    diff = ROT_APPRX_1 - ROT_APPRX_2

    return (AVG, mat_translate, diff)

def main():

    print(calc_basis_change(MAT_R1, MAT_B1, MAT_R2, MAT_B2))


if __name__ == "__main__":
    main()