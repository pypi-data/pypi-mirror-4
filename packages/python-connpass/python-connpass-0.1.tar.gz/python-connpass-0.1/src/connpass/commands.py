import sys
import locale
import argparse
from pprint import pprint
from six import u, print_, binary_type
from . import Connpass


def maybe_decoded(s):
    if isinstance(s, binary_type):
        return unicode(s, encoding=locale.getpreferredencoding())
    return s

def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser()
    parser.add_argument("--event-id",
                        default=[],
                        nargs="*",
                        type=int)
    parser.add_argument("--keyword",
                        default=[],
                        nargs="*",
                        type=maybe_decoded)
    parser.add_argument("--keyword-or",
                        default=[],
                        nargs="*",
                        type=maybe_decoded)
    parser.add_argument("--ym",
                        default=[],
                        nargs="*",
                        type=unicode)
    parser.add_argument("--ymd",
                        default=[],
                        nargs="*",
                        type=unicode)
    parser.add_argument("--nickname",
                        default=[],
                        nargs="*",
                        type=maybe_decoded)
    parser.add_argument("--owner-nickname",
                        nargs="*",
                        default=[],
                        type=maybe_decoded)
    parser.add_argument("--series-id",
                        default=[],
                        nargs="*",
                        type=int)
    parser.add_argument("--start",
                        default=1,
                        type=int)
    parser.add_argument("--count",
                        default=10,
                        type=int)
    parser.add_argument("--format",
                        default=u('json'),
                        choices=(u('json'),),
                        type=unicode)
    

    args = parser.parse_args(argv)
    pprint(args)

    connpass = Connpass()
    result = connpass.search(**vars(args))

    events = result['events']
    for event in events:
        print_(u("[{0[event_id]:5}] {0[started_at]} {0[event_url]} {0[title]}").format(event))


if __name__ == '__main__':
    sys.exit(main())
