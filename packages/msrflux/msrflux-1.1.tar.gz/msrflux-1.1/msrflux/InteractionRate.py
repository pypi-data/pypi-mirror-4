__author__ = 'tunnell'

from Constants import AVOGADROS_NUMBER

def CC(fluxes, mass=1):
    """Compute CC event rates

    mass in kt
    """

    xsec = {}
    xsec['nubar'] = 0.34 * 10 ** -42 # units of m^2
    xsec['nu'] = 0.67 * 10 ** -42     # units of m^2

    E_range = {'min': None, 'max': None}
    bins = {}

    interactions = {}
    for flavor, value in fluxes.iteritems():
        for energy, flux in value.iteritems():
            #  Units are flux/GeV, so need to know GeV range
            if E_range['min'] is None or energy < E_range['min']:
                E_range['min'] = energy
            if E_range['max'] is None or energy > E_range['max']:
                E_range['max'] = energy

            for nu_or_nubar in ['nu', 'nubar']:
                key = (flavor, nu_or_nubar)
                if key not in interactions:
                    interactions[key] = 0.0
                    bins[key] = 0

                my_int = mass * 10 ** 9 * AVOGADROS_NUMBER * xsec[nu_or_nubar]
                my_int *= energy * flux

                interactions[key] += my_int
                bins[key] += 1

    return interactions


