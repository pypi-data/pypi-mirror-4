#!/usr/bin/env python
#
# Before running this:
# 1) Install a B2G build with Marionette enabled
# 2) adb forward tcp:2828 tcp:2828

from optparse import OptionParser
import os

from progressbar import Counter
from progressbar import ProgressBar

from marionette import Marionette
from gaiatest import GaiaData
from gaiatest import GaiaDevice


class B2GPopulate:

    def __init__(self, marionette):
        self.marionette = marionette
        self.data_layer = GaiaData(self.marionette)
        self.device = GaiaDevice(self.marionette)

    def populate(self, contact_count=0, music_count=0, picture_count=0, video_count=0):
        self.data_layer.remove_all_contacts(1000 * len(self.data_layer.all_contacts))

        if self.device.is_android_build and self.data_layer.media_files:
            for filename in self.data_layer.media_files:
                self.device.manager.removeFile('/'.join(['sdcard', filename]))

        if contact_count > 0:
            self.populate_contacts(contact_count)

        if music_count > 0:
            self.populate_files('music', 'MUS_0001.mp3', music_count)

        if picture_count > 0:
            self.populate_files('pictures', 'IMG_0001.jpg', picture_count, 'DCIM/100MZLLA')

        if video_count > 0:
            self.populate_files('videos', 'VID_0001.3gp', video_count, 'DCIM/100MZLLA')

    def populate_contacts(self, count):
        from gaiatest.mocks.mock_contact import MockContact
        progress = ProgressBar(
            widgets=['Contacts: ', '[', Counter(), '/%d] ' % count])
        for i in progress(range(count)):
            self.data_layer.insert_contact(MockContact())

    def populate_files(self, file_type, source, count, destination=''):
        progress = ProgressBar(
            widgets=['%s: ' % file_type.capitalize(), '[', Counter(), '/%d] ' % count],
            maxval=count)
        progress.start()
        self.device.push_file(
            os.path.join(os.path.dirname(__file__), source),
            count,
            destination,
            progress)
        progress.finish()


def cli():
    parser = OptionParser(usage='%prog [options]')
    parser.add_option(
        '--contacts',
        action='store',
        type=int,
        dest='contact_count',
        metavar='int',
        help='number of contacts to create')
    parser.add_option(
        '--music',
        action='store',
        type=int,
        dest='music_count',
        metavar='int',
        help='number of music files to create')
    parser.add_option(
        '--pictures',
        action='store',
        type=int,
        dest='picture_count',
        metavar='int',
        help='number of pictures to create')
    parser.add_option(
        '--videos',
        action='store',
        type=int,
        dest='video_count',
        metavar='int',
        help='number of videos to create')

    options, args = parser.parse_args()

    if not any([options.contact_count,
                options.music_count,
                options.picture_count,
                options.video_count]):
        parser.print_usage()
        print 'must specify at least one item to populate'
        parser.exit()

    marionette = Marionette(host='localhost', port=2828)  # TODO command line option for address
    marionette.start_session()
    B2GPopulate(marionette).populate(
        options.contact_count,
        options.music_count,
        options.picture_count,
        options.video_count)


if __name__ == '__main__':
    cli()
