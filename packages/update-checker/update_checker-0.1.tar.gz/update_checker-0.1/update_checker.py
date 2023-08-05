#!/usr/bin/env python
import json
import platform
import requests
import sys
from datetime import datetime
from pkg_resources import parse_version as V

__version__ = '0.1'


class UpdateChecker(object):
    """A class to check for package updates."""
    def __init__(self, url=None):
        """Store the URL to use for checking."""
        self.url = url if url else 'http://csil.cs.ucsb.edu:65429/check'

    def check(self, package_name, package_version, **extra_data):
        """Return a UpdateResult object if there is a newer version."""
        data = extra_data
        data['package_name'] = package_name
        data['package_version'] = package_version
        data['python_version'] = sys.version.split()[0]
        data['platform'] = platform.platform(True)

        try:
            headers = {'content-type': 'application/json'}
            response = requests.put(self.url, json.dumps(data), timeout=1,
                                    headers=headers)
        except requests.exceptions.RequestException:
            return None

        data = response.json
        if not data or not data.get('success') or (V(package_version) >=
                                                   V(data['data']['version'])):
            return None

        return UpdateResult(package_name, running=package_version,
                            available=data['data']['version'],
                            release_date=data['data']['upload_time'])

    def output(self, *args, **kwargs):
        """Behaves similar to check, but outputs the result, if any."""
        result = self.check(*args, **kwargs)
        if result:
            print(result)


class UpdateResult(object):
    """Contains the information for a package that has an update."""
    def __init__(self, package, running, available, release_date):
        self.available_version = available
        self.package_name = package
        self.running_version = running
        if release_date:
            self.release_date = datetime.strptime(release_date,
                                                  '%Y-%m-%dT%H:%M:%S')
        else:
            self.release_date = None

    def __str__(self):
        retval = ('Version {0} of {1} is outdated. Version {2} '
                  .format(self.running_version, self.package_name,
                          self.available_version))
        if self.release_date:
            retval += 'was released {0}.'.format(
                pretty_date(self.release_date))
        else:
            retval += 'is available.'
        return retval


def pretty_date(the_datetime):
    # Source modified from
    # http://stackoverflow.com/a/5164027/176978
    diff = datetime.utcnow() - the_datetime
    if diff.days > 7 or diff.days < 0:
        return the_datetime.strftime('%A %B %d, %Y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif diff.seconds <= 1:
        return 'just now'
    elif diff.seconds < 60:
        return '{0} seconds ago'.format(diff.seconds)
    elif diff.seconds < 120:
        return '1 minute ago'
    elif diff.seconds < 3600:
        return '{0} minutes ago'.format(diff.seconds / 60)
    elif diff.seconds < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(diff.seconds / 3600)
