# coding: utf-8
import os
import sys
import glob
import datetime
import subprocess

exif_tag_list = {
    'Camera Model Name': '-CameraModelName=',
    'Create Date': '-CreateDate=',  # korea time

    'Date/Time Original': "-DateTimeOriginal='{0}'",  # korea time -7: (difference in time: Germany)
    'GPS Altitude Ref': "-GPSAltitudeRef='Above Sea Level'",
    'GPS Date Stamp': '-GPSDateStamp={0}',  # korea time -9: (GPS time)
    'GPS Time Stamp': '-GPSTimeStamp={0}',
    'GPS Altitude': '-GPSAltitude={0}',
    'GPS Latitude': '-GPSLatitude={0}',
    'GPS Longitude': '-GPSLongitude={0}',
}


def run_script(cmd):
    cmd = ' '.join(cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out_msg = proc.stdout.read()

    return out_msg.split('\n')


class ExifEditor(object):
    def __init__(self, file_path, location_info):
        self._file_path = file_path
        self._location_info = location_info
        self._img_exif_info = None

    def get_img_exif_info(self, file_name):
        self._img_exif_info = {}

        cmd = ['exiftool', file_name]
        msg = run_script(cmd)

        for _exif in msg:
            _exif = _exif.strip()
            if _exif == '':
                continue
            exif_tag, exif_msg = _exif.split(':', 1)
            exif_tag = exif_tag.strip()
            exif_msg = exif_msg.strip()

            if exif_tag in exif_tag_list:
                self._img_exif_info[exif_tag] = exif_msg

    def _get_location_info(self, i_datetime):
        near_location = None
        check_time_delta = None
        for l_info in self._location_info:
            l_datetime = l_info[0]

            if l_datetime > i_datetime:
                time_delta = l_datetime - i_datetime
            else:
                time_delta = i_datetime - l_datetime

            if time_delta > datetime.timedelta(seconds=300):
                if check_time_delta is None or check_time_delta > time_delta:
                    check_time_delta = time_delta
                continue

            if near_location is None or near_location[0] > time_delta:
                near_location = [time_delta, l_info]

        if near_location is not None:
            return near_location[1]
        else:
            print check_time_delta,
            return None

    def _set_location_info(self, file_path):
        create_datetime = datetime.datetime.strptime(self._img_exif_info['Create Date'].split('.')[0],
                                                     "%Y:%m:%d %H:%M:%S")
        original_datetime = create_datetime - datetime.timedelta(hours=7)
        gpx_date_time = create_datetime - datetime.timedelta(hours=9)

        img_location_info = self._get_location_info(gpx_date_time)

        if img_location_info is None:
            return False

        """
        Time, Latitude, Longitude, Altitude
        exiftool test2.jpg -DateTimeOriginal='2016:09:27 13:31:39'
        exiftool test2.jpg -gpsaltitude=797.8443603515625
        exiftool test2.jpg -gpsLongitude=10.6972303390502930
        exiftool test2.jpg -gpslatitude=47.5706596374511719
        exiftool test2.jpg -GPSDateStamp=2016:10:03
        exiftool test2.jpg -GPSTimeStamp=08:58:28Z
        """
        cmd = ['exiftool', file_path,
               exif_tag_list['Date/Time Original'].format(original_datetime.strftime("%Y:%m:%d %H:%M:%S")),
               exif_tag_list['GPS Altitude Ref'],
               exif_tag_list['GPS Altitude'].format(img_location_info[3]),
               exif_tag_list['GPS Latitude'].format(img_location_info[1]),
               exif_tag_list['GPS Longitude'].format(img_location_info[2]),
               exif_tag_list['GPS Date Stamp'].format(gpx_date_time.strftime("%Y:%m:%d")),
               exif_tag_list['GPS Time Stamp'].format(gpx_date_time.strftime("%H:%M:%SZ"))
               ]

        msg = run_script(cmd)
        return ''.join(msg).strip()

    def run(self):
        print self._file_path
        if os.path.isdir(self._file_path):
            file_path_list = glob.glob(os.path.join(self._file_path, "*.JPG"))
        elif os.path.isfile(self._file_path):
            file_path_list = [self._file_path]
        else:
            sys.exit(1)

        for n, file_path in enumerate(file_path_list):
            print "{0}/{1} {2}\t\t".format(n, len(file_path_list), file_path),
            sys.stdout.flush()

            self.get_img_exif_info(file_path)
            if 'Camera Model Name' in self._img_exif_info:
                if self._img_exif_info["Camera Model Name"] == 'Canon EOS 600D':
                    msg = False
                    try:
                        msg = self._set_location_info(file_path)
                        print msg
                    except Exception, err:
                        print "{0}[{1}]".format(err.__class__.__name__, str(err))

                    if type(msg) == bool and not msg:
                        new_file_path = os.path.join(os.path.dirname(file_path),
                                                     "fail",
                                                     os.path.basename(file_path))

                        if not os.path.exists(os.path.dirname(new_file_path)):
                            os.mkdir(os.path.dirname(new_file_path))

                        os.rename(file_path, new_file_path)
                    else:
                        new_file_path = os.path.join(os.path.dirname(file_path),
                                                     "OK",
                                                     os.path.basename(file_path))

                        if not os.path.exists(os.path.dirname(new_file_path)):
                            os.mkdir(os.path.dirname(new_file_path))

                        os.rename(file_path, new_file_path)


