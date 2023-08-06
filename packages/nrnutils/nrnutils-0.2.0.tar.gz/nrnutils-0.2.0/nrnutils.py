"""
Wrapper classes to make working with NEURON easier.

Author: Andrew P. Davison, UNIC, CNRS
"""

__version__ = "0.2.0"

from neuron import nrn, h, hclass

h.load_file('stdrun.hoc')

PROXIMAL = 0
DISTAL = 1

class Mechanism(object):
    """
    Examples:
    >>> leak = Mechanism('pas', {'e': -65, 'g': 0.0002})
    >>> hh = Mechanism('hh')
    """
    def __init__(self, name, **parameters):
        self.name = name
        self.parameters = parameters

    def insert_into(self, section):
        section.insert(self.name)
        for name, value in self.parameters.items():
            for segment in section:
                mech = getattr(segment, self.name)
                setattr(mech, name, value)


class Section(nrn.Section):
    """
    Examples:
    >>> soma = Section(L=30, diam=30, mechanisms=[hh, leak])
    >>> apical = Section(L=600, diam=2, nseg=5, mechanisms=[leak],
    ...                  parent=soma, connection_point=DISTAL)
    """
    
    def __init__(self, L, diam, nseg=1, Ra=100, cm=1, mechanisms=[], parent=None, connection_point=DISTAL):
        nrn.Section.__init__(self)
        # set geometry
        self.L = L
        self.diam = diam
        self.nseg = nseg
        # set cable properties
        self.Ra = Ra
        self.cm = cm
        # connect to parent section
        if parent:
            self.connect(parent, connection_point, PROXIMAL)
        # add ion channels
        for mechanism in mechanisms:
            mechanism.insert_into(self)
        #self.synapses = {}

    def add_synapse(self, label, type, location=0.5, **parameters):
        synapse = getattr(h, type)(location, sec=self)
        for name, value in parameters.items():
            setattr(synapse, name, value)
        if hasattr(self, label):
            raise Exception("Can't overwrite synapse labels (to keep things simple)")
        setattr(self, label, synapse)
        
    def plot(self, variable, location=0.5, tmin=0, tmax=5, xmin=-80, xmax=40):
        import neuron.gui
        self.graph = h.Graph()
        h.graphList[0].append(self.graph)
        self.graph.size(tmin, tmax, xmin, xmax)
        self.graph.addvar('%s(%g)' % (variable, location), sec=self)

    def record_spikes(self, threshold=-30):
        self.spiketimes = h.Vector()
        self.spikecount = h.APCount(0.5, sec=self)
        self.spikecount.thresh = threshold
        self.spikecount.record(self.spiketimes)
        

if __name__ == "__main__":
    
    class SimpleNeuron(object):
    
        def __init__(self):
            # define ion channel parameters
            leak = Mechanism('pas', e=-65, g=0.0002)
            hh = Mechanism('hh')
            # create cable sections
            self.soma = Section(L=30, diam=30, mechanisms=[hh])
            self.apical = Section(L=600, diam=2, nseg=5, mechanisms=[leak], parent=self.soma,
                                  connection_point=DISTAL)
            self.basilar = Section(L=600, diam=2, nseg=5, mechanisms=[leak], parent=self.soma,
                                   connection_point=0.5)
            self.axon = Section(L=1000, diam=1, nseg=37, mechanisms=[hh],
                                connection_point=0)
            # synaptic input
            self.soma.add_synapse('syn', 'AlphaSynapse', onset=0.5, gmax=0.05, e=0)
    
    neuron = SimpleNeuron()
    neuron.soma.plot('v')
    neuron.apical.plot('v')
    
    h.dt = 0.025
    v_init = -65
    tstop = 5
    h.finitialize(v_init)
    h.run()
