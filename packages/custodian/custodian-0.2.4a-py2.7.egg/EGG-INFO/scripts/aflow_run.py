#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""
TODO: Change the module doc.
"""

from __future__ import division

__author__ = "shyuepingong"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__status__ = "Beta"
__date__ = "2/4/13"

import logging

from custodian.custodian import Custodian
from custodian.vasp.handlers import VaspErrorHandler, UnconvergedErrorHandler, PoscarErrorHandler
from custodian.vasp.jobs import VaspJob

def aflow_run():
    #An example of an aflow run.

    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO, filename="run.log")
    handlers = [VaspErrorHandler(), UnconvergedErrorHandler(),
                PoscarErrorHandler()]
    jobs = VaspJob.aflow_style_run(["mpirun", "/share/apps/bin/pvasp.5.2.11"])
    c = Custodian(handlers, jobs, max_errors=10)
    c.run()

if __name__ == "__main__":
    aflow_run()