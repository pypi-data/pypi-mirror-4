#!/usr/bin/env python

import argparse
import logging
import maven


logger = logging.getLogger(__name__)


class AtomHopperMavenConnector(maven.MavenConnector):
    _default_url_root = ('http://maven.research.rackspacecloud.com/'
                         'content/repositories')

    def get_atomhopper_url(self, root, snapshot=False, version=None):
        if snapshot:
            s_or_r = 'snapshots'
        else:
            s_or_r = 'releases'

        vroot = "%s/%s/org/atomhopper/ah-jetty-server" % (root, s_or_r)

        return self.get_artifact_url(vroot, 'jar', snapshot=snapshot,
                                     version=version)

    def get_atomhopper(self, url_root=None, dest=None, snapshot=False,
                       version=None):

        if url_root is None:
            url_root = AtomHopperMavenConnector._default_url_root

        url = self.get_atomhopper_url(root=url_root, snapshot=snapshot,
                                      version=version)

        dest = self.clean_up_dest(url, dest)

        print '%s --> %s' % (url, dest)
        self.download_file(url=url, dest=dest)

        return dest


def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', help='The name that the downloaded file '
                        'should be renamed to, or the directory where it '
                        'should be downloaded to')
    parser.add_argument('--url-root', help='The url (with path) to download '
                        'artifacts from.')
    parser.add_argument('--snapshot', help='Download a SNAPSHOT build instead '
                        'of a release build.', action='store_true')
    parser.add_argument('--version', help='The version of the artifacts to '
                        'download. Typically of the forms "x.y.z" for '
                        'releases, "x.y.z-SNAPSHOT" for the most recent '
                        'snapshot build in version x.y.z, and '
                        '"x.y.z-date.time-build" for a specific snapshot '
                        'build.', type=str)
    parser.add_argument('--print-log', help="Print the log to STDERR.",
                        action='store_true')
    parser.add_argument('--full-log', help="Log more information.",
                        action='store_true')
    args = parser.parse_args()

    if args.print_log:
        if args.full_log:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(levelname)s:%(name)s:%(funcName)s:'
                                '%(filename)s(%(lineno)d):%(threadName)s'
                                '(%(thread)d):%(message)s')
        else:
            logging.basicConfig(level=logging.DEBUG)

    ahmc = AtomHopperMavenConnector()
    ahmc.get_atomhopper(url_root=args.url_root, dest=args.dest,
                        snapshot=args.snapshot, version=args.version)


if __name__ == '__main__':
    run()
