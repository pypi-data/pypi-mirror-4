============
Contributors
============

FireWorks was developed primarily by Anubhav Jain at Lawrence Berkeley National Lab, using research funding from Kristin Persson for the `Materials Project <http://www.materialsproject.org>`_.

Michael Kocher and Dan Gunter initiated the architecture of a central database with multiple workers that queued 'placeholder' scripts responsible for checking out jobs. Some of Michael's code was refashioned for the QueueLauncher and the PBS QueueAdapter.

Shyue Ping Ong was extremely helpful in providing guidance and feedback, as well as the nitty gritty of getting set up with Sphinx documentation, PyPI, continuous integration, etc. The code for modifying a FireWork specification using a dictionary (DictMod) was adapted (with permission) from his custodian_ library. Incidentally, that library is a nice complement to FireWorks for use in FireTasks. Also, if you are in the market for a free Python materials analysis code, I highly recommend his pymatgen_ library (which I also sometimes contribute to).

Wei Chen was the first test pilot of FireWorks, and contributed greatly to improving the docs and ensuring that FireWorks installation went smoothly for others. In addition, he made many suggestions to improve the usability of the code.

.. _pymatgen: http://packages.python.org/pymatgen/
.. _custodian: https://pypi.python.org/pypi/custodian