"""Compute nustorm FD neutrino fluxes"""

__author__ = 'tunnell'

from msrflux.Sampler import Sampler
import msrflux.Output as Output
from msrflux.DecayKinematics import compute_neutrino_flux
from msrflux.InteractionRate import CC

energy_muon = 50.0  # GeV
baseline = 3000.0  # km
N_mu = 10.66e+20 * 4 # muons
my_mass = 50.0 # kt 

x = Sampler(energy_muon, baseline)

results = x.sample(N=100)

Output.print_samples_to_screen(results)

results = compute_neutrino_flux(results, N_mu=N_mu,
    E_min=4.0, E_max=energy_muon) # 1/m2

Output.create_plot('henf', results)
Output.print_events_to_screen(CC(results, mass=my_mass))
