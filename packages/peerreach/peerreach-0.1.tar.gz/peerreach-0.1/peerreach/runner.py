
import json
from optparse import OptionParser

from .api import Api
from .parsers import RawParser, JSONParser
import peerreach


def main(args=None):

    usage = "usage: %prog [options] screen_name [screen_name...]"

    parser = OptionParser(usage=usage, version=peerreach.__version__)
    parser.add_option("-i", "--ids",
                     action="store_true", dest="ids",
                     help="Use twitter ids instead of screen name")
    parser.add_option("-r", "--raw",
                     action="store_true", dest="raw",
                     help="Show raw peerreach api output")

    options, args = parser.parse_args(args)

    if not args:
        parser.error("No twitter users provided")

    if options.raw:
        parser = RawParser()
    else:
        parser = JSONParser()

    api = Api(parser=parser)

    if len(args) == 1:
        if options.ids:
            data = api.user_lookup(user_id=args[0])
        else:
            data = api.user_lookup(screen_name=args[0])
    else:
        if options.ids:
            data = api.multi_user_lookup(user_ids=args)
        else:
            data = api.multi_user_lookup(screen_names=args)

    if options.raw:
        print data
    else:
        print json.dumps(data, indent=2)


if __name__ == '__main__':
    main()
