#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Thu Oct 04 14:44:00 CEST 2012

import os
import antispoofing

def get_db_names():
    """
    Get the database names available
    """
    databases = []

    #For each resource
    import pkg_resources
    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
        plugin = entrypoint.load()
        databases.append(entrypoint.name)

    databases.append('all')
    return databases


def get_db_by_name(name):
    """
    Get a database instance by name
    """
    import pkg_resources

    if(name=="all"):
        return antispoofing.utils.db.spoofing.DatabaseAll()

    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
        plugin = entrypoint.load()
        if(name==entrypoint.name):
            return plugin()



def perfTable(databases,develTexts,testTexts,thres):
  tbl = []
  
  for i in range(len(databases)):
    tbl.append(databases[i])

    tbl.append(" threshold: %.4f" % thres[i])
    tbl.append(develTexts[i])
    tbl.append(testTexts[i])
    tbl.append("*****")

  txt = ''.join([k+'\n' for k in tbl])
  return txt

def ensure_dir(dirname):
  """ Creates the directory dirname if it does not already exist,
      taking into account concurrent 'creation' on the grid.
      An exception is thrown if a file (rather than a directory) already 
      exists. """
  try:
    # Tries to create the directory
    os.makedirs(dirname)
  except OSError:
    # Check that the directory exists
    if os.path.isdir(dirname): pass
    else: raise
