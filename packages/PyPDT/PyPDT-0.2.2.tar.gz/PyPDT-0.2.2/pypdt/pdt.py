# -*- python -*-

"Pythonic access to high energy particle data tables."


C_IN_MM_PER_PS = 0.299792458
HBAR_IN_GEVPS = 6.58211814E-13


def lifetime_to_width(tau): # tau in picoseconds
    "Convert a lifetime, tau, in picoseconds, to a width in GeV"
    if not tau:
        return None
    return HBAR_IN_GEVPS/float(tau)

def width_to_lifetime(gamma): # gamma in GeV
    "Convert a width, gamma, in GeV, to a lifetime in picoseconds"
    if not gamma:
        return None
    return HBAR_IN_GEVPS/float(gamma)


class LorentzViolation(Exception):
    "An exception thrown when a condition inconsistent with special relativity is encountered."
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return "Lorentz consistency has been violated: " + self.msg


class ParticleData(object):
    """
    Container for a few particle data properties. Its main job is to resolve
    which of lifetime vs. width to use for a given particle.

    A string representation is defined for convenience.

    The available properties are id, name, mass, threecharge, charge, width,
    lifetime, and ctau. The mean displacement in vacuum for a supplied energy is
    accessed via the mean_disp(energy) method.
    """

    def __init__(self, id, name, mass, threecharge, width=None, lifetime=None):
        assert id is not None
        self.id = int(id)
        assert name is not None
        self.name = name
        assert mass is not None
        self.mass = float(mass)
        assert threecharge is not None
        self.threecharge = threecharge
        if not lifetime and width is None:
            self._lifetime = None
            self._width = None
        elif not lifetime: # width = 0 overrides lifetime = 0
            self.set_width(width)
        else:
            self.set_lifetime(lifetime)

    @property
    def charge(self):
        return self.threecharge / 3.0

    def get_lifetime(self):
        "Get the particle lifetime in picoseconds."
        return self._lifetime
    def set_lifetime(self, tau):
        "Set the particle lifetime (and, implicitly, the width). tau is lifetime in picoseconds."
        self._lifetime = tau
        self._width = lifetime_to_width(tau)
    lifetime = property(get_lifetime, set_lifetime)

    def get_width(self):
        "Get the particle width in GeV."
        return self._width
    def set_width(self, gamma):
        "Set the particle width (and, implicitly, the lifetime). gamma is width in GeV."
        self._lifetime = width_to_lifetime(gamma)
        self._width = gamma
    width = property(get_width, set_width)

    @property
    def ctau(self):
        "Get the particle c tau distance in mm."
        if self.lifetime is None:
            return None
        return self.lifetime * C_IN_MM_PER_PS

    def mean_disp(self, energy):
        "Get the particle mean displacement in mm, for the given particle energy in GeV (includes Lorentz boost factor)."
        if self.lifetime is None:
            return None
        if energy < self.mass:
            raise LorentzViolation("energy %1.2f GeV less than particle mass %1.2f GeV for PID = %d" % (energy, self.mass, self.id))
        from math import sqrt
        gamma = float(energy) / self.mass
        beta = sqrt(1.0 - gamma**-2)
        #print beta, gamma
        return self.ctau * beta * gamma

    def __repr__(self):
        s = "%s: ID=%d, m=%1.2e GeV, 3*q=%d" % (self.name, self.id, self.mass, self.threecharge)
        if self.width is not None:
            s += ", width=%1.2e GeV" % self.width
        if self.lifetime is not None:
            s += ", tau=%1.2e ps" % self.lifetime
        if self.ctau is not None:
            s += ", ctau=%1.2e mm" % self.ctau
        return s



class ParticleDataTable(object):
    """
    Wrapper object for a whole database of ParticleData objects, indexed by their PDG ID codes.

    By default, the input database file will be the particle.tbl file from the most recent HepPDT
    version (3.04.01), accessed via the CERN AFS filesystem. If you want a different db file, or
    don't have AFS mounted, specify an explicit file path.
    """

    def __init__(self, dbpath=None):
        """
        Constructor, taking the path to the PDT database file as an argument.
        If no arg is supplied, or it is None, try to find and load the version
        installed by the package, or fall back to look on CERN AFS.
        """
        import os
        if dbpath is None:
            ## If no path specified, try first the local then the AFS db files
            prefix = os.path.dirname(__file__)
            for i in xrange(4): # remove 4 directory levels
                prefix = os.path.dirname(prefix)
            dbpath = os.path.join(prefix, "share", "pypdt", "particle.tbl")
            if not os.path.exists(dbpath):
                dbpath = "/afs/cern.ch/sw/lcg/external/HepPDT/3.04.01/src/HepPDT-3.04.01/data/particle.tbl"
        self.clear()
        self.read_db(dbpath)

    def clear(self):
        "Forget all currently known particles."
        self.entries = {}

    def read_db(self, dbpath):
        """Read a particle data database file, updating the currently registered
        particles. Call clear() first if you *only* want to know about the
        particle data in this db file."""
        dbf = open(dbpath)
        for line in dbf:
            ## Handle comments
            if "//" in line:
                line = line[:line.find("//")]
            line = line.strip()
            if not line:
                continue
            data = line.split()
            #print data

            ## Parse a data line
            pid = int(data[0])
            name = data[1]
            threecharge = int(data[2])
            mass = float(data[3])
            width = float(data[4])
            lifetime = float(data[5])

            ## Add a ParticleData object into the entries dict for this PID
            self.entries[pid] = ParticleData(pid, name, mass, threecharge, width, lifetime)
        dbf.close()

    def ids(self):
        """Get the list of known particle IDs (using the PDG Monte Carlo numbering
        scheme). These are the available keys for db lookup."""
        return self.entries.keys()

    def particle(self, id):
        "Get the particle data for the supplied particle ID. Alternatively usable as tbl[id]."
        return self.entries[int(id)]
    __getitem__ = particle

    def __iter__(self):
        "Iterate over all known particles, yielding a pair of (ID, ParticleData) for each iteration."
        for pid_pd in self.entries.iteritems():
            yield pid_pd


"Super-short alias for the rather lengthy ParticleDataTable class"
PDT = ParticleDataTable
