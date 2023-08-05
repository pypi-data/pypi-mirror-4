__author__ = 'tunnell'


def print_samples_to_screen(results):
    for E, l, angle in results:
        print 'E_mu: %g GeV\tL: %g km\tangle:%g rad' % (E, l, angle)


def print_events_to_screen(events):
    print 'Total number of events:'
    for key, value in events.iteritems():
        flavor, polarity = key

        print '\t', flavor, polarity, value


def create_modglobes_samples_file(samples, N_mu):
    file_obj = open('samples', 'w')
    file_obj.write('%d\n' % len(samples))
    file_obj.write('%g\n' % N_mu)
    for E, l, angle in samples:
        file_obj.write('%g %g %g\n' % (E, l, angle))
    file_obj.close()


def translate(name):
    if name == 'mu_flux':
        return r'$\bar{\nu}_\mu$'
    elif name == 'e_flux':
        return r'$\nu_e$'

def create_plot(name, results, use_matplotlib=True,
                ylabel=r'Flux /(m${}^2$ GeV)'):
    """Create plot with matplotlib"""

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(4,4))
    except:
        print "Can't find matplotlib.  Just creating flux output."
        use_matplotlib = False

    for key in results.keys():
        par = results[key]

        x = []
        y = []
        for key2, val in par.iteritems():
            x.append(key2)
            y.append(val)

        if use_matplotlib:
            plt.plot(x, y, 'o', label=translate(key))

        x.sort()

        filename = '%s_%s_raw' % (name, key)
        print "Creating raw output:", filename
        file_obj = open(filename, 'w')
        for sorted_x in x:
            file_obj.write('%f %f\n' % (sorted_x, par[sorted_x]))
        file_obj.close()

        print key, 'sum', sum(y)

    if use_matplotlib:
        plt.xlabel("Neutrino energy [GeV]")
        plt.ylabel(ylabel)
        plt.legend(numpoints=1,
                   loc=0)
        
        filename = '%s.eps' % (name)
        print "Creating plot:", filename
        plt.savefig(filename, bbox_inches='tight')
