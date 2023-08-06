
====================================
tome - Markup Language for Authors
====================================


.. contents:: Contents
    :depth: 2


Introduction
---------------

Tome is a markup language and associated tool suite intended for authors, primarily authors of
novels and other relatively simple "chapter books". Tome offers a simple an unobtrusive markup
language that allows you to focus on the writing instead of the formatting and styling. The tool
suite will parse your markup and generate output in a number of different formats including
EPUB, text, and latex (from which you can use the standard latex tool chains to produce DVI,
Postscript, or PDF).


Installation
------------

You can install in a couple of ways.

From Source
~~~~~~~~~~~~~

You can get the source by cloning this repository or by downloading the source package from the 
`Download page <https://bitbucket.org/bmearns/tome/downloads/tome-1.0.0.0.zip>`_. Once you have
the source, you can use python to install by simply executing:

::
    
    python setup.py install

This should take care of installing Tome on your system, as well as the templ package which is
required by Tome. On Unix like systems, you may need to have superuser priveledges to install
the package.


From PyPi
~~~~~~~~~~~~~

You can also get tome from PyPi: http://pypi.python.org/pypi/tome/. From there you
can download an appropriate distribution, or you can use
`pip <http://www.pip-installer.org/en/latest/installing.html>`_ to install it with:

::
    
    pip install tome


Windows Binary Installer
~~~~~~~~~~~~~~~~~~~~~~~~

A GUI installer program for Windows is available for the latest official release.
You can get the installer from the 
`Download section on PyPi <http://pypi.python.org/pypi/tome/#downloads>`_ or
from the 
`Downloads page on bitbucket <https://bitbucket.org/bmearns/tome/downloads/tome-1.0.0.0.win32.exe>`_.


Logistics
------------

Contact Information
~~~~~~~~~~~~~~~~~~~~~~~~

This project is currently hosted on `bitbucket <https://bitbucket.org>`_, 
at `https://bitbucket.org/bmearns/tome/ <https://bitbucket.org/bmearns/tome/>`_. The primary author is Brian Mearns:
you can contact Brian through bitbucket at `https://bitbucket.org/bmearns <https://bitbucket.org/bmearns>`_. 

You can also follow the project on `twitter <https://twitter.com/TomeProject>`_ `@TomeProject`.  


Copyright and License
~~~~~~~~~~~~~~~~~~~~~~~~~~

\ ``tome``\  is \ *free software*\ : you can redistribute it and/or modify
it under the terms of the \ **GNU Affero General Public License**\  as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 



\ ``tome``\  is distributed in the hope that it will be useful,
but \ **without any warranty**\ ; without even the implied warranty of
\ *merchantability*\  or \ *fitness for a particular purpose*\ .  See the
GNU Affero General Public License for more details. 



A copy of the GNU Affero General Public License is available in the templ
distribution under the file LICENSE.txt. If you did not receive a copy of
this file, see `http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_. 


