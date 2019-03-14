# cc.api

https://api.creativecommons.org/docs/


## Installation

To build/install with the current source:

    apt-get remove python-setuptools
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py

    #apt-get install apache2
    #cd /var/www
    #mkdir api.creativecommons.org

    git clone https://github.com/creativecommons/i18n.git
    cd i18n
    python bootstrap.py
    bin/buildout
    python setup.py install

    apt-get install libxslt-dev python-dev libz-dev
    wget https://bootstrap.pypa.io/bootstrap-buildout.py
    python bootstrap-buildout.py
    bin/buildout
