import sys

from hncomments import utils

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s <url>" % (__file__)
        sys.exit(1)
    else:
        url = sys.argv[1]

    hn_url = utils.get_hn_comments_url(url)
    if not hn_url:
        sys.exit(1)
    print hn_url
