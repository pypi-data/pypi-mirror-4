from pysky import utils

# Base URL for downloading grib2 files
base_url = 'http://weather.noaa.gov/pub/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus'
noaa_params = ['maxt', 'temp', 'mint', 'pop12', 'sky', 'wspd', 'apt', 'qpf', 'snow', 'wx', 'wgust', 'icons', 'rhm']
#noaa_params = ['wx']

# Degrib path
degrib_path = '/usr/local/bin/degrib'

def download_command_line():
    """ Handle download from command-line """
    from optparse import OptionParser

    usage = "usage:\n%prog download [options]"
    parser = OptionParser(usage)

    parser.add_option('-g', '--grib2-dir', dest='grib2_dir',
        action='store',
        help='Directory to download grib2 files to')
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
        action='store_true',
        help='Show verbose output')

    (options, args) = parser.parse_args()

     # use current dir if none provided
    grib2_dir = options.grib2_dir if options.grib2_dir else os.path.abspath(os.path.dirname(__file__))
    utils.verbose = options.verbose
    download(options.grib2_dir)

def download(data_dir):
    """
    Download grib2 files to data directory

    args:
        data_dir Directory to store data files
    """
    import urllib, re, os, sys, time, urllib2, dateutil
    from datetime import datetime
    from dateutil import tz
    from dateutil.parser import parse

    files_downloaded = False # whether files have been downloaded

    # Loop over directories that have forecast data files
    for dir in ['VP.001-003','VP.004-007']: # loop over remote directories

        data_subdir = "{0}/{1}".format(data_dir, dir)

        utils.info('\nChecking directory {0}'.format(dir))

        # Create directory if it doesn't exist
        if not os.path.exists(data_subdir):
            os.mkdir(data_subdir)

        # Get directory listing so we can see if we need a newer version
        f = urllib.urlopen("{0}/{1}/ls-l".format(base_url, dir))
        data = f.read()
        lines = data.split("\n")
  
        # Loop over lines in directory listing
        for line in lines:

            # Check file modified date if this is a .bin file
            if line.find(".bin") != -1:

                # Split line to get date and filename
                month, day, rtime, filename = re.split("\s+", line)[5:9]

                # Split filename to get noaa param name
                param = filename.split('.')[1]

                # Only download files if we are interested in this parameter
                if param in noaa_params:

                    # Local path and time
                    local_path = "{0}/{1}/{2}".format(data_dir, dir, filename)
                    local_time = os.stat(local_path).st_mtime if os.path.exists(local_path) else 0
                    utils.info("Local: {0} last modified {1}".format(local_path, local_time))

                    # Remote path and time
                    remote_path = "{0}/{1}/{2}".format(base_url, dir, filename)
                    request = urllib2.urlopen(remote_path)
                    last_modified_str = request.info()['Last-Modified']
                    remote_time = _utc2local(parse(last_modified_str))
                    utils.info("Remote: {0} last modified {1}".format(remote_path, remote_time))

                    # If file does not exist or the local file is older than the remote file, download
                    if not os.path.exists(local_path) or local_time < remote_time:
                        utils.info('Downloading remote file {0}'.format(remote_path))
                        _download_file(request, local_path)
                        os.utime(local_path, (remote_time, remote_time))
                        files_downloaded = True
                    # Otherwise, just log some information
                    else:
                        utils.info('Local file is up-to-date, skipping download')
                    
    # Cube data files if any were downloaded
    if files_downloaded:
        cmd = "{degrib} {data_dir}/VP.001-003/*.bin {data_dir}/VP.004-007/*.bin -Data -Index {data_dir}/all.ind -out {data_dir}/all.dat".format(
            degrib = degrib_path,
            data_dir = data_dir
        )
        utils.info(cmd)
        output = ""
        for line in os.popen(cmd).readlines():
    
            output += line
    
        utils.info(output)
    else:
        utils.info('No files downloaded - skipping cube')

def xml(data_dir, latitude, longitude):
    """
    Generate XML file from grib2 data cube

    args:
        data_dir - Directory where grib2 data cube is located
        latitude - Latitude
        longitude - Longitude

    returns - xml string
    """

    import os

    # build and execute command
    cmd = "{degrib_path} {data_dir}/all.ind -DP -pnt {latitude},{longitude} -XML 1 -geoData {data_dir}/geodata".format(
        data_dir = data_dir, latitude = latitude, longitude = longitude, degrib_path = degrib_path)

    utils.info(cmd)
    xml = ""
    for line in os.popen(cmd).readlines():

        xml += line

    # return output
    return xml

def _utc2local(utc):
    """ Convert utc datetime object to local datetime """
    from dateutil import tz
    import time
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = utc.replace(tzinfo = from_zone)
    return time.mktime(utc.astimezone(to_zone).timetuple())

def _download_file(request, local_path):
    """ Download file given a urllib2 urlopen from remote path to local path """
    import sys
    content_length = int(request.info()['Content-Length'])
    chunk_size = 8192

    with open(local_path, 'wb') as f:
        next_percentage = 5.0
        chunk = request.read(chunk_size)
        downloaded = 0
        while chunk:
            f.write(chunk)
            downloaded += chunk_size
            if (float(downloaded) / float(content_length)) * 100.0 > next_percentage:
                sys.stdout.write("\r")
                sys.stdout.write("{1}% complete {0}".format('#' * (int(next_percentage) / 5), int(next_percentage)))
                next_percentage += 5.0
                #sys.stdout.write('#')
                sys.stdout.flush()
            chunk = request.read(chunk_size)
        print('')
