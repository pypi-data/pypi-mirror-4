# -*- coding: utf-8 -*-

import collections
import requests
import lxml.html

l = lambda: collections.defaultdict(l)
amis = l()


def _refresh_amis(target, version):
    """Refresh current amis dict based on ubuntu cloud images website.
    """
    url = "http://cloud-images.ubuntu.com/{0}/{1}/current/".format(
        target, version)
    html = lxml.html.fromstring(requests.get(url).content)
    rows = html.cssselect('div#main table tbody tr')[1:]
    for row in rows:
        i = [i.strip() for i in row.text_content().split('\n')]
        amis[target][version][i[0]][i[1]][i[2]]['ami'] = i[3].split()[1]
        amis[target][version][i[0]][i[1]][i[2]]['ec2_command'] = i[4]


def get(target='server', version='quantal',
        region='us-east-1', arch='64-bit', root_store='ebs'):
    """Get the current ami of current ubuntu cloud image.
    """
    if not amis[target][version]:
        _refresh_amis(target, version)

    return amis[target][version][region][arch][root_store]['ami']


def get_command(target='server', version='quantal',
                region='us-east-1', arch='64-bit', root_store='ebs'):
    """Get the ec2 command of current ubuntu cloud image.
    """
    if not amis[target][version]:
        _refresh_amis(target, version)

    return amis[target][version][region][arch][root_store]['ec2_command']
