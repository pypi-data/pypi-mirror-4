Deltacloud Python client
========================

A Python client for `Deltacloud API <http://deltacloud.apache.org/>`_ REST interface.


Features
--------

- Basic operations with images, instances, hardware-profiles and realms
- Manage instances using start, stop, destroy and reboot operations
- Create new instance from image


Install
-------

::

    pip install deltacloud


Examples
--------

Launching an instance
^^^^^^^^^^^^^^^^^^^^^

::

    from deltacloud import Deltacloud
    client = Deltacloud('http://localhost:3001/api', 'mockuser', 'mockpassword')
    instance = client.create_instance('img1', {'hwp_id': 'm1-small'})

Listing images/hardware profiles/realms/instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    print(client.images())
    print(client.hardware_profiles())
    print(client.realms())
    print(client.instances())

Stopping an instance
^^^^^^^^^^^^^^^^^^^^

::

    instance = client.instances()[0]
    instance.stop()


Contributions
-------------

* Michal Fojtik
* Tomas Sedovic
* Martin Packman


License
-------

Licensed under Apache License, Version 2.0 Copyright (C) 2009  Red Hat, Inc.

See http://www.apache.org/licenses/LICENSE-2.0
