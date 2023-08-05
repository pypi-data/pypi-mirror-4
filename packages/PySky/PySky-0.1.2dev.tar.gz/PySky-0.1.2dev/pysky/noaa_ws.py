server = 'http://www.weather.gov/forecasts/xml/SOAP_server/ndfdXMLclient.php'
params = [ 'maxt', 'temp', 'mint', 'pop12', 'sky', 'wspd', 'appt', 'qpf', 'snow', 'wx', 'wgust', 'icons', 'rh' ]


def xml(latitude, longitude):
        
    import urllib, xml.parsers.expat
        
    param_strs = []

    for param in params:

        param_strs.append("%s=%s" % (param,param))

    param_str = '&'.join(param_strs)

    # Attempt to download XML data
    attempt = 1
    while attempt <= 10:

        url = "%s?lat=%s&lon=%s&product=time-series&%s&Submit=Submit" % (server, latitude, longitude, param_str) # construct URL

        try: # try downloading and parsing data
            f = urllib.urlopen(url) # request URL
            data = f.read() # read response
            parser = xml.parsers.expat.ParserCreate('iso-8859-1') # construct parser to try parsing response
            parser.Parse(data)
            break
        except: # if not able to parse data, try to request again
            attempt=attempt+1

    if attempt != 10: # we didn't max out attempts

        return data
