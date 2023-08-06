#!/usr/bin/env python

import atoms.atoms as atoms
import os

datadir = os.path.join(os.path.dirname(atoms.__file__),"tests","data")
#Read PDB
print "Reading PDB"
pdbfilename = os.path.join(datadir,"1L2Y.pdb")
myAtoms = atoms.readpdbintoAtoms(open(pdbfilename).readlines())

print "%s" % (myAtoms[0])

# Make new Atom
newatom = atoms.Atom(coord=[1.5, 1.5, 1.5])
print "%s" % (newatom)
