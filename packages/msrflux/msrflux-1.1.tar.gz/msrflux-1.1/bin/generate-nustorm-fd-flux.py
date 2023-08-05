"""Compute nustorm FD neutrino fluxes"""

__author__ = 'tunnell'

from msrflux.Sampler import Sampler
import msrflux.Output as Output
from msrflux.DecayKinematics import compute_neutrino_flux
from msrflux.InteractionRate import CC

#  What is the mean stored muon energy in the decay ring?
energy_muon = 3.8  # GeV

#  Set the baseline between the accelerator and detector.
baseline = 2.0  # km

#  Sampler performs the MC integration by sampling points in the detector and
#  accelerator volumes.
x = Sampler(energy_muon, baseline)

###########################
##  OPTIONAL SET METHODS ##
###########################

# Smear the stored muon energy by 10% uniform spread
#x.set_accelerator_energy(spread=0.1 * energy_muon) # GeV

#  Integrate over the detector volume
my_mass = 1.3 # kt
x.set_detector(radius=2.5, # m
    mass=my_mass, # kt
    density=7.8)  # g/cm^3

#  Integrate over the detector straight
x.set_accelerator_length(0.15) # km

#  Set the Twiss parameters (ie. accelerator optics).  This doesn't matter
#  much but is here for complessness.
x.set_accelerator_twiss(emittance=2.1e-06,
    beta=0.04) # km, km

#  Sample N points
results = x.sample(N=1000)

# Print to screen
Output.print_samples_to_screen(results)

# Compute the fluxes
results = compute_neutrino_flux(results, N_mu=1.8e18) # 1/m2

#  Create plots and flux files
Output.create_plot('nustorm', results)

Output.print_events_to_screen(CC(results, mass=my_mass))
