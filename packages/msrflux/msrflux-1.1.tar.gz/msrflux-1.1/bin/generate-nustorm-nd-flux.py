"""Generate nuSTORM near detector fluxes

For details, see generate-nustorm-fd-flux.py which is commented."""

__author__ = 'tunnell'

from msrflux.Sampler import Sampler
import msrflux.Output as Output
from msrflux.DecayKinematics import compute_neutrino_flux
from msrflux.InteractionRate import CC

energy_muon = 3.8  # GeV
baseline = 0.1  # km

x = Sampler(energy_muon, baseline)

#x.set_accelerator_energy(spread=0.1 * energy_muon) # GeV

my_mass = 0.1 # kt
x.set_detector(radius=1.0, # m
    mass=my_mass, # kt
    density=1.4)  # g/cm^3

x.set_accelerator_length(0.15) # km

results = x.sample(N=1000)
N_mu = 1.8e18
Output.create_modglobes_samples_file(results, N_mu)
results = compute_neutrino_flux(results, N_mu=1.8e18) # 1/m2

Output.create_plot('nustorm_near', results)
Output.print_events_to_screen(CC(results, mass=my_mass))
