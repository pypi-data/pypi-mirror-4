import pkg_resources
import pyblz.parse


def bank_data():
    return pyblz.parse.parse(
        pkg_resources.resource_filename(__name__, 'BLZ_20120903.txt'))
