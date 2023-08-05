"""Sample accelerator phasespace and detector volume

"""

__author__ = 'tunnell'

import math
import numpy as np
from Constants import MUON_MASS


class Sampler(object):
    """Sample"""

    def __init__(self, E_mu, baseline):
        """Setup the accelerator and detector phasespace calculator

        :param E_mu: central muon energy in decay ring (GeV)
        :param baseline: distance between accelerator and detector (km)

        The baseline should be the
        distance between the accelerator and the detector.  More specifically,
        it's the point between the most downstream part of the accelerator and
        the most upstream part of the detector.  This is the minimum distance
        that a neutrino could possibly travel between the accelerator and
        detector.
        """
        self.detector_radius = 0.0  # km
        self.detector_mass = 0.0  # grams
        self.detector_density = 0.0  # g/km^3

        self.accelerator_straight_length = 0.0  # km
        self.E_mu = E_mu  # GeV
        self.E_mu_spread = 0.0  # GeV

        self.baseline = baseline  # km

        self.emittance = None
        self.beta = None

    def set_accelerator_twiss(self, emittance, beta):
        """Set twiss parameters

        Alpha (ie. beta-prime) is assumed to be zero.
        These are the central momentum optics.
        """
        self.emittance = emittance
        self.beta = beta

    def set_accelerator_length(self, accelerator_straight_length):
        """set length in km
        """
        self.accelerator_straight_length = accelerator_straight_length

    def set_accelerator_energy(self, energy=None, spread=None):
        if energy:
            self.E_mu = energy
        if spread:
            self.E_mu_spread = spread

    def set_detector(self, radius, mass, density):
        """Set detector volume parameters

        :param radius: detector radius in m
        :param mass: detector mass in kt
        :param density: density of detector in g/cm^3

        :returns: nothing
        """

        radius, mass, density = [float(x) for x in [radius, mass, density]]

        # Convert: m -> km
        self.detector_radius = radius / 1000

        # Convert: kt -> grams
        self.detector_mass = mass * 10 ** 9

        # We do a units conversion here from g/cm^3 to g/km^3
        self.detector_density = density * 10 ** 15

        if self.detector_radius:
            self.detector_max_z = self.detector_mass
            self.detector_max_z /= self.detector_density
            self.detector_max_z /= (2 * self.detector_radius) ** 2

            #print 'max_detector_z', self.detector_max_z

    def sample_accelerator(self, nbins):
        """Sample a point in the accelerator phasespace

        a is x, km
        b is x', radians
        c is uniform value for z in straight, km
        """

        if self.emittance and self.beta:
            # From Penn 61 MUCOOL note
            mean = [0, 0]
            cov = [[0, 0], [0, 0]]  # covariance matrix

            #  Ignore cross terms (done in initialization)
            #ie. cov[0][1] = 0.0 # sigma_xx'
            #ie. cov[0][1] = 0.0 # sigma_x'x

            # sigma_xx
            cov[0][0] = self.emittance * self.beta * MUON_MASS / self.E_mu

            # sigma_x'x'
            cov[1][1] = MUON_MASS * self.emittance / self.beta / self.E_mu

            # Step 1: compute phasespace
            result = np.random.multivariate_normal(mean, cov, nbins)
            result = result.astype(np.float32)
            a, b = result.T  # transpose for phasespace x, x-prime
        else:
            a, b = np.zeros([2, nbins], dtype=np.float32)

        #  This is used for figuring out where along the ring the muon decays
        c = np.random.uniform(high=self.accelerator_straight_length,
            size=nbins).astype(np.float32)

        return a, b, c

    def sample_detector(self, nbins):
        """Sample detector volume

        d is uniform values for x,y,z in detector
        """

        #  Where in the detector volume the decay happens?
        #  The size is 3*nbins because there are three spacial dimensions
        if self.detector_radius == 0.0:
            d = np.zeros(3 * nbins)
        else:
            #  In compute final states, we multiply by length in x, y, z
            d = np.random.uniform(
                low=-1, high=1,
                size=3 * nbins)
            d = d.astype(np.float32)

        return d

    def compute_final_states(self, N, a, b, c, d):
        """Compute distances and angles"""
        multiplier = 3
        for i in range(N):
            z = 0
            r = 0
            if self.detector_radius > 0:
                x = self.detector_radius * d[multiplier * i]
                y = self.detector_radius * d[multiplier * i + 1]

                z = self.detector_max_z * (d[multiplier * i + 2] + 1) / 2

                r = math.sqrt(x * x + y * y)

            radius = a[i]

            distance = c[i]  # somewhere along the accelerator straight
            distance += self.baseline
            distance += z

            distance = math.sqrt(distance * distance + (radius - r) ** 2)

            angle_lab = b[i]
            angle_lab = math.asin(r / distance) - angle_lab

            a[i] = distance
            b[i] = angle_lab

        return [a, b]

    def sample(self, N=1):
        """Sample phasespace
        """

        a, b, c = self.sample_accelerator(N)

        d = self.sample_detector(N)

        distance, angle = self.compute_final_states(N, a, b, c, d)

        E = np.random.uniform(low=(self.E_mu - self.E_mu_spread),
            high=(self.E_mu + self.E_mu_spread),
            size=N)
        return zip(E, distance, angle)
