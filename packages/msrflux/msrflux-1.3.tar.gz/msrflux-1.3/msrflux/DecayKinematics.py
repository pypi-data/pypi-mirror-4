"""Double differential cross section"""

__author__ = 'tunnell'

import math
import numpy as np
from Constants import MUON_MASS


def compute_neutrino_flux(my_input, N_mu=1.8e18, E_min=0.5, E_max=3.8,
                          steps=100):
    """Compute neutrino fluxes using double differential cross section

    We assume unpolarized.

    For a good reference of the equation for neutrino fluxes, see
    hep-ph/0002108.  For a derivation, see Jian Tang's thesis.
    """

    nu_energies = np.linspace(E_min, E_max, steps)
    N_flux_bins = len(my_input)

    results = {'e_flux': {}, 'mu_flux': {}}

    for E_nu in nu_energies:
        E_nu = float(E_nu)
        results['e_flux'][E_nu] = []
        results['mu_flux'][E_nu] = []

    for event in my_input:
        E_mu, distance, angle = event
        # E_mu in GeV
        # distance in km
        # angle in rad

        distance = 1000 * distance  # km -> m

        for E_nu in nu_energies:
            E_nu = float(E_nu)

            y = E_nu / E_mu  # unitless, (0,1)

            if y < 0 or y > 1:
                continue

            beta = math.sqrt(1 - MUON_MASS ** 2 / E_mu ** 2)

            flux_e = 24.0 * N_mu
            flux_e /= (math.pi * distance ** 2 * MUON_MASS ** 6)
            flux_e *= E_mu ** 4 * y ** 2
            flux_e *= (1 - beta * math.cos(angle))
            flux_e *= (MUON_MASS ** 2 - 2 * E_mu ** 2 *
                                        y * (1 - beta * math.cos(angle)))

            flux_mu = 4.0 * N_mu
            flux_mu /= (math.pi * distance ** 2 * MUON_MASS ** 6)
            flux_mu *= E_mu ** 4 * y ** 2
            flux_mu *= (1 - beta * math.cos(angle))
            flux_mu *= (3 * MUON_MASS ** 2 - 4 * E_mu ** 2 *
                                             y * (1 - beta * math.cos(angle)))

            # Fluxes go negative if unphysical
            if flux_e > 0.0:
                results['e_flux'][E_nu].append(flux_e)
            if flux_mu > 0.0:
                results['mu_flux'][E_nu].append(flux_mu)

    for flux_name in results:
        for E_nu in results[flux_name]:
            my_sum = sum(results[flux_name][E_nu])
            my_sum /= N_flux_bins
            my_sum /= len(nu_energies)

            results[flux_name][E_nu] = my_sum

    return results
