import numpy
import xml.etree.ElementTree as ET



class XMLMidas(object):
    """

    """
    def __init__(self, filename):
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()
        self._data = None

    def _get_stimuli_names(self):
        stimuli = self.root.find('experiments').findall('stimuli')
        return [s.attrib['name'] for s in stimuli]
    stimuliNames = property(_get_stimuli_names)

    def _get_inh_names(self):
        inh = self.root.find('experiments').findall('inhibitor')
        return [s.attrib['name'] for s in inh]
    inhibitorNames = property(_get_inh_names)

    def _get_species_names(self):
        species = self.root.find('measurements').findall('specy')
        return [s.attrib['name'] for s in species]
    species = property(_get_species_names)

    def get_rootchild_index(self, child):
        return [x.tag for x in self.root.getchildren()].index(child)

    def _get_times(self):
        species = self.root.find('measurements').findall('specy')
        times = set()
        for s in species:
            for t in s.findall("time"):
                times.add(t.attrib['value'])
        return list(times)
    times = property(_get_times)

    def _get_length(self):
        l = int(self.root.find('measurements').attrib['length'])
        return l
    length = property(_get_length)

    def _get_measurements(self):
        L = self.length
        times = sorted(self.times)
        #species = self.species
        #data = numpy.zeros((len(species), len())
        species = self.root.find('measurements').findall('specy')
        data = numpy.zeros((len(times), L, len(species)))


        for ispe, specy in enumerate(species):
            for itime, t in enumerate(specy.findall('time')):
                time = t.attrib['value']
                index_time = times.index(time)
                index_specy = species.index(specy)
                for iexp, x in enumerate(t.text.split(',')):
                    data[itime][iexp,ispe] = float(x)
        return data

    measurements = property(_get_measurements)

    def _get_data(self):
        if self._data == None:
            self._data = self.measurements
            return self._data
        else:
            return self._data
    data = property(_get_data)


    def save(self, filename):
        species = self.species
        data = self.data
        stimuli = self.stimuli
        f = open(filename, "w")
        f.close()

    def test(self):
        #m = XMLMidas("midas.xml")
        self.stimuliNames
        self.inhibitorNames
        self.species
        self.times
        self.data
