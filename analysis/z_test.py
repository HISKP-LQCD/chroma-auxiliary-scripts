# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>

from scipy.stats import norm
import numpy as np


def main():
    pion_z, pion_p = z_test(4.229299823727998286e-01,
                            5.198282496262007432e-03,
                            0.4115,
                            0.0006)
    print('pion', pion_z, pion_p)

    kaon_z, kaon_p = z_test(4.831713166682579663e-01,
                            5.168785751180492334e-03,
                            0.4749,
                            0.0006)
    print('kaon', kaon_z, kaon_p)


def z_test(my_val, my_err, other_val, other_err):
    z = (my_val - other_val) / np.sqrt(my_err**2 + other_val**2)
    cdf = norm().cdf
    p = cdf(-np.abs(z)) + 1 - cdf(np.abs(z))

    return z, p


if __name__ == '__main__':
    main()
