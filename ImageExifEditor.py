# coding:utf-8

from CreateLocationInfo import CreateLocationInfo
from ExifEditor import ExifEditor


location_info = CreateLocationInfo('/Users/anhm/Desktop/path').run()
ExifEditor('/Users/anhm/Desktop/img', location_info).run()
