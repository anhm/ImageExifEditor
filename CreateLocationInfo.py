import os
import sys
import glob
import gpxpy
import cPickle


class CreateLocationInfo(object):
    """
    Time, Latitude, Longitude, Altitude
    """
    def __init__(self, file_path):
        self._file_path = file_path
        self._location_info = []

    def run(self):
        if os.path.isdir(self._file_path):
            file_path_list = glob.glob(os.path.join(self._file_path, "*.gpx"))
        elif os.path.isfile(self._file_path):
            file_path_list = [self._file_path]
        else:
            sys.exit(1)

        for file_path in file_path_list:
            print file_path
            if os.path.basename(file_path).split('.')[1] == 'dump':
                self.get_dump_data(file_path)
            else:
                self.get_location_info(file_path)
                self._location_info.sort()

        return self._location_info

    def get_dump_data(self, file_path):
        with open(file_path, 'r') as fd:
            self._location_info += cPickle.load(fd)

    def get_location_info(self, file_path):
        gpx_data = open(file_path, 'r')
        gpx = gpxpy.parse(gpx_data)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self._location_info.append([point.time, point.latitude, point.longitude, point.elevation])


if __name__ == '__main__':
    #location_info = CreateLocationInfo('/Users/anhm/Desktop/path/location.dump').run()
    location_info = CreateLocationInfo('/Users/anhm/Desktop/path').run()
    print len(location_info)

    with open('/Users/anhm/Desktop/path/location.dump', 'w') as fd:
        cPickle.dump(location_info, fd)


