import rpy2
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector

# R package names
packnames = ('ggplot2', 'hexbin', 'tuneR')


utils = rpackages.importr('utils')
tuneR = rpackages.importr('tuneR')
# R vector of strings


utils.chooseCRANmirror(ind=1) # select the first mirror in the list

# Selectively install what needs to be install.
# We are fancy, just because we can.
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))

rsum = robjects.r['sum']