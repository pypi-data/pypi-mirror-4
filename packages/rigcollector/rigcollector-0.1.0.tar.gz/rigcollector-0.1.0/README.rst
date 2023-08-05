============
Rigcollector
============

Rigcollector is the Python client for `RigsMonitoring <https://rigsmonitoring.com>`_ a a web application that allows yous to monitor your mining rigs, by **tracking system metrics** (CPU, MEM, Disks, Network, Processes...) and **mining-related metrics** (GPU temperature, Hashrate, BTC Balace...).



Rigcollector is bundled with the following collectors:

- System Metrics (CPU, MEM, load, disks, network)
- ATI GPU temperature for linux, and GPU-Z for Windows
- Processes Info
- Infos from MtGox, Slush's mining pool...

You can easily create and use your own collector.

Installation
============

You can install rigcollector via **easy_install** or **pip**.

::

    $ pip install rigcollector


Usage
=====

Basic usage, "rigcollector -h" or "bakcollector collect -h" to show the help.

You can get your rig API key in your **rig settings** on RigsMonitoring.

::

    $ rigcollector collect --api-key your_rig_api_key


If everything is ok, you can run the process in the background:

::
    
    $ rigcollector collect --api-key your_rig_api_key --detach 1


By default, the AtiGpuCollector is disabled, to enable it...


Configuration
=============

Here is a basic **rigcollector.yml** config file, see below for more informations on cu
stoms collectors.

Rigcollector check for a configuration file named **rigcollector.yml** but you can set a different config file with **-c** option:

::

    $ rigcollector collect --api-key your_rig_api_key -c yourconfigfile.yml


::

    ProcessesCollector:
      processes:
        - bitcoind

    CustomCollector:
      custom:
        - rigcollector.custom.SlushsPoolCollector
        - rigcollector.custom.MtGoxCollector

    SlushsPoolCollector:
      token: YOUR_TOKEN

    MtGoxCollector:
      auth_key: YOUR_AUTH_KEY
      auth_secret: YOUR_SECRET_KEY


You can desactivate any Collector with the **is_active** directive.

::

    ProcessesCollector:
      is_active: 0


Custom Collecor
===============

Rigcollector is bundled with few customs collectors, please create a pull request if you create one.

- **SlushsPoolCollector**, gather information from `Slush Mining Pool API <http://mining.bitcoin.cz>`_.
- **MtGoxCollector**, get your BTC balacnce from your MtGox account `MtGox <https://mtgox.com>`_.

Create your own Collector
-------------------------

You can take a look at DummyCollector in rigcollector.custom.dummy, it contains everything to get you started.

License (MIT)
=============

Copyright (c) 2013 Thomas Sileo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.