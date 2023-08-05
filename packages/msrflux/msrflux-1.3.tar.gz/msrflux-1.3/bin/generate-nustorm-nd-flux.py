"""Generate nuSTORM near detector fluxes

For details, see generate-nustorm-fd-flux.py which is commented."""

__author__ = 'tunnell'

from msrflux.Sampler import Sampler
import msrflux.Output as Output
from msrflux.DecayKinematics import compute_neutrino_flux
from msrflux.InteractionRate import CC

energy_muon = 3.8  # GeV
energy_spread = 0.1 * energy_muon # GeV   
baseline = 0.05  # km
my_mass = 0.1 # kt  
my_density = 1.4 # g/cm^3
radius = 5.625/2 # m
straight_length = 0.15 # km  
N_mu = 1.8e18 # number of muons

x = Sampler(energy_muon, baseline)

x.set_accelerator_energy(spread=energy_spread) # GeV

x.set_detector(radius=radius, # m
    mass=my_mass, # kt
    density=my_density)  # g/cm^3

x.set_accelerator_length(straight_length) # km

results = x.sample(N=1000)
Output.create_modglobes_samples_file(results, N_mu)
results = compute_neutrino_flux(results, N_mu=N_mu) # 1/m2

Output.create_plot('nustorm_near', results)
Output.print_events_to_screen(CC(results, mass=my_mass))
