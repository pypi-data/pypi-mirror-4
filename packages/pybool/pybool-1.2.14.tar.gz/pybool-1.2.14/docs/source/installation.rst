..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html




Installation
============

.. _installation instructions:

These installation instructions are for a general Linux system but should work with minor 
changes on other OSes (Windows, MacOS, etc..). It assumes that most software will be
installed in ``$HOME/local``.



Prerequisites
~~~~~~~~~~~~~

pybool relies on the following third-party softwares

- Python_ 2.5 or newer. Development has been
  done on Python 2.6 but it should work on Python 2.5 and Python 2.7. It
  should not be difficult to get pybool working on Python 3 but it may not work
  out of the box. pybool uses the following Python libraries: 

    * numpy_
    * matplotlib_
    * networkx_
    * pygraphviz_
  
  I find easy_install_ or the more recent pip_ are the easiest ways to install Python packages.

- A C++ compiler to compile the core C++ algorithm. All development has been
  done with GCC_ 4.4.3 but other versions and compilers should work.

- The `Boost C++ libraries`_: I have used version 1.45 although other versions should work.
  Following the commands_ given at the Boost website is straightforward, e.g.::
  
    ./bootstrap.sh --help
    ./bootstrap.sh --prefix=$HOME/local
    ./bjam --with-python --prefix=$HOME/local install release
  
  should install the boost Python library and the necessary headers. Once they are installed,
  you will need to update your ``LD_LIBRARY_PATH`` environment variable, e.g.::
  
    export LD_LIBRARY_PATH=$HOME/local/lib:$LD_LIBRARY_PATH
  
  so that the shared objects can be found at runtime.
        
- GraphViz_ tools: These are used to generate the network diagrams. In particular ``neato`` must
  be in your ``PATH``.


The following softwares are optional

- dot2tex_: This is used to create the publication quality network diagrams.

- LaTeX_: This is also used to generate the publication quality network diagrams. The preview style 
  and the tikz package should be installed.

- IPython_: This is used for the parallel implementation. It is not required
  if you do not wish to run pybool in parallel mode.

.. _Python: http://www.python.org/
.. _numpy: http://numpy.scipy.org/
.. _matplotlib: http://matplotlib.sourceforge.net/
.. _networkx: http://networkx.lanl.gov/
.. _pygraphviz: http://networkx.lanl.gov/pygraphviz/
.. _dot2tex: http://www.fauskes.net/code/dot2tex/
.. _GCC: http://gcc.gnu.org/
.. _Boost C++ libraries: http://www.boost.org/
.. _commands: http://www.boost.org/doc/libs/1_45_0/more/getting_started/unix-variants.html#easy-build-and-install
.. _LaTeX: http://www.latex-project.org/
.. _GraphViz: http://www.graphviz.org/
.. _IPython: http://ipython.scipy.org/


Next, download_ and install the Python package cookbook using the standard::

  python setup.py install

If you haven't already, download the
pybool `source distribution`_, unpack it and change into the top level directory. 

.. _download: http://pypi.python.org/pypi/cookbook/



Configure, build, install
~~~~~~~~~~~~~~~~~~~~~~~~~

This Python package uses aksetup for installation, which means that
installation should be easy and quick. Try::
  
  ./configure.py --help

to examine the possible options. By the way, if a configuration option says ``several ok``,
then you may specify several values, separated by commas. Something like the
following should work::

  ./configure.py --boost-inc-dir=$HOME/local/include --boost-lib-dir=$HOME/local/lib
  python setup.py build
  sudo python setup.py install
  
Configuration is obtained from files in this order::

  /etc/aksetup-defaults.py
  $HOME/.aksetup-defaults.py
  $PACKAGEDIR/siteconf.py

Once you've run configure, you can copy options from your ``siteconf.py`` file to
one of these files, and you won't ever have to configure them again manually.
In fact, you may pass the options ``--update-user`` and ``--update-global`` to
configure, and it will automatically update these files for you.

This is particularly handy if you want to perform an unattended or automatic
installation via easy_install_.

.. _easy_install: http://packages.python.org/distribute/easy_install.html
.. _pip: http://pypi.python.org/pypi/pip

To check that pybool has been successfully installed, change to an empty directory and
try running the following command::

  python -c "import pybool.cNetwork"

If you see any errors such as::

  Traceback (most recent call last):
    File "<string>", line 1, in <module>
  ImportError: libboost_python.so.1.45.0: cannot open shared object file: No such file or directory

you probably have not updated your ``LD_LIBRARY_PATH`` successfully.

The next step is to use the tutorial_ on how to use pybool. Enjoy!

.. _tutorial: http://sysbio.mrc-bsu.cam.ac.uk/johns/pybool/pybool-tutorial.pdf


