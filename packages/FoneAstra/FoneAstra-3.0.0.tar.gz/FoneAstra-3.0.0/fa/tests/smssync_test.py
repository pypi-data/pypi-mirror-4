import argparse
import datetime
import httplib
import json
import urllib

def test_smssync(hostname, path, phone_number, message, secret, time=None):
    if time == None:
        time = datetime.datetime.now()
    time_str = time.strftime("%m-%d-%Y %H:%M")
    params = urllib.urlencode({
        'from': phone_number,
        'message': message,
        'secret': secret,
        'sent_timestamp': time_str,
    })
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain',
    }
    conn = httplib.HTTPConnection(hostname)
    conn.request('POST', path, params, headers)
    response = conn.getresponse()
    data = response.read()
    if response.status != 200:
        print data
        raise httplib.BadStatusLine("Server returned {code}.".format(
            code=response.status
        ))
    conn.close()
    return json.loads(data)


def main():
    parser = argparse.ArgumentParser(description='Send sample messages to SMSSync.')
    parser.add_argument('--hostname', required=True, help='Hostname of server.')
    parser.add_argument('--path', required=True, help='Path of SMSSync view.')
    parser.add_argument('--number', required=True, help='Phone number this message is from.')
    parser.add_argument('--message', required=True, help='Message to send.')
    parser.add_argument('--secret', required=True, help='Secret to use for connection.')
    args = parser.parse_args()
    print "Connecting to {hostname}{path}".format(hostname=args.hostname, path=args.path)
    print test_smssync(
        args.hostname,
        args.path,
        args.number,
        args.message,
        args.secret,
    )


if __name__ == '__main__':
    main()
