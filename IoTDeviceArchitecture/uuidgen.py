"""
Generates UUIDs in a consistent manner.
"""

import uuid
import netifaces


def generateUuid(namespace='', domain='snhu.edu'):
    """ Generate a device specific Type 5 UUID within a namespace and domain.

    :param namespace: The namespace where the UUID is being generated
    :param domain: The domain where the UUID is being generated
    :return: Type 5 UUID
    """
    mac = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr'].encode('utf-8')
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, mac+'.'+namespace+'.'+domain))
