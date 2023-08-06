Ubuntu-AMI
==========

Get the daily build ami of Ubuntu Cloud Image.

Origin source: `Ubuntu Cloud Image <http://cloud-images.ubuntu.com>`_

Install
-------

Install by pip:

.. code:: bash

    $ pip install UbuntuAMI

This package depends on `requests` and `lxml`.


Usage
-----

As easy as

.. code:: python

    >>> import ubuntuami
    >>> ubuntuami.get()
    'ami-dc0e9cb5'
    >>> ubuntuami.get_command()
    'ec2-run-instances ami-dc0e9cb5 -t t1.micro --region us-east-1 --key ${EC2_KEYPAIR_US_EAST_1}'

You may also add more filter to get the ami you want.

.. code:: python

    >>> ubuntuami.get(target='server', version='quantal', region='us-west-2')
    'ami-66e07556'
    >>> ubuntuami.get(target='desktop', version='precise', region='ap-northeast-1', arch='32-bit')
    'ami-c41aa3c5'

Read the source for more info, it's simple.
