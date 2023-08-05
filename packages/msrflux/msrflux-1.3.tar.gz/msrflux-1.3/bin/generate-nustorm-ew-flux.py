"""Generate nuSTORM flux for a near detector for electroweak measurements

For details, see generate-nustorm-fd-flux.py which is commented."""

__author__ = 'tunnell'

from msrflux.Sampler import Sampler
import msrflux.Output as Output
from msrflux.DecayKinematics import compute_neutrino_flux
from msrflux import InteractionRate

detectors = {}

this_detector = {}
this_detector['mass'] = 0.06 # kt
this_detector['radius'] = 2.5 / 2 # m

detectors['60t_uBooNe'] = this_detector

this_detector = {}
this_detector['mass'] = 1.0 # kt
# We want a scale up uBooNe:
#  5.625 m x 5.625 m x 22.5 m
this_detector['radius'] = 5.625 / 2 # m

detectors['1kt_LAr'] = this_detector

normed_results_to_plot_together = {}

for my_baseline in [0.1, 0.05, 0.02, 2.0]: # km
    for detector_key in detectors.keys():
        #
        # nuSTORM LOI parameters
        #
        N_mu = 1.8e18 # number of muons, 10**21 POT
        energy_muon = 3.8  # GeV
        energy_spread = 0.1 * energy_muon # GeV
        straight_length = 0.15 # km

        #
        # Detecor parameters: 1 kT of uBooNe
        #
        #my_baseline # km, end of straight to front of detector
        my_mass = detectors[detector_key]['mass'] # kt
        my_density = 1.4 # g/cm^3

        radius = detectors[detector_key]['radius'] # m

        #
        # Sim. parameters
        #
        my_sample_E_min = 0.01 # GeV, ie. 10 MeV
        my_sample_E_max = 4.01 # GeV
        my_sample_steps = 401 # this gives us 10 MeV bins

        #################
        ### Internals ###
        #################

        bin_size = float(my_sample_E_max - my_sample_E_min)/(my_sample_steps-1)

        x = Sampler(energy_muon, my_baseline)

        x.set_accelerator_energy(spread=energy_spread) # GeV

        x.set_detector(radius=radius, # m
            mass=my_mass, # kt
            density=my_density)  # g/cm^3

        x.set_accelerator_length(straight_length) # km

        results = x.sample(N=50000)
        Output.create_modglobes_samples_file(results, N_mu)
        results = compute_neutrino_flux(results,
                                        N_mu=N_mu,
                                        E_min = my_sample_E_min,
                                        E_max = my_sample_E_max,
                                        steps = my_sample_steps,
                                        ) # 1/m2

        normed_results = {}
        for key in results:
            normed_results[key] = {}
            for key2, val2 in results[key].iteritems():
                normed_results[key][key2] = val2 * bin_size

        if detector_key == '1kt_LAr':
            normed_results_to_plot_together[my_baseline] = results

        Output.create_plot('nustorm_%0.2fkm_%s' % (my_baseline, detector_key), results,
                           ylabel=r'Flux /(m${}^2$ %d MeV)' % (bin_size * 1000))
        Output.print_events_to_screen(InteractionRate.CC(results, mass=my_mass))
        

#import matplotlib.pyplot as plt

#print normed_results_to_plot_together.keys()

#plt.figure()

"""
for key in normed_results_to_plot_together.keys():
    x = []
    y = []
    for key2, val in normed_results_to_plot_together[key].iteritems():
        print key2, val
        x.append(key2)
        y.append(val)

    plt.plot(x, y,
             label=key)
plt.savefig('test.eps')
"""
