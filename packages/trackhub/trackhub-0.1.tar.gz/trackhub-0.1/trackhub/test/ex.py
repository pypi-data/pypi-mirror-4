from trackhub import Hub, GenomesFile, Genome, TrackDb, Track, \
    CompositeTrack, ViewTrack
from trackhub.track import SubGroupDefinition
from trackhub.upload import upload_track, upload_hub
import os
import json

HOST = 'marenz.webfactional.com'
USER = 'marenz'
REMOTE_BASE = '/home/marenz/webapps/xfer/hubs'
URL_BASE = 'http://xfer.genomicnorth.com/hubs'
GENOME = 'dm3'
UPLOAD = True

hub = Hub(
    hub='example_hub',
    short_label='example hub',
    long_label='an example hub for testing',
    email='none@example.com')

genomes_file = GenomesFile()
genome = Genome('dm3')
trackdb = TrackDb()
genome.add_trackdb(trackdb)
genomes_file.add_genome(genome)
hub.add_genomes_file(genomes_file)

composite = CompositeTrack(
    name="mycomposite",
    short_label="my composite",
    long_label="An example composite track",
    tracktype="bigWig")

composite.add_params(dragAndDrop='subtracks', visibility='full')

from trackhub.track import SubGroupDefinition
subgroups = [

    SubGroupDefinition(
        name="frequency",
        label="Frequency",
        mapping=dict(lo="Low", hi="High")),

    SubGroupDefinition(
        name="size",
        label="Feature_size",
        mapping=dict(small="Small", med="Medium", lg="Large")),

    SubGroupDefinition(
        name="celltype",
        label="Cell_Type",
        mapping=dict(a="CelltypeA", b="CelltypeB")),

]

composite.add_subgroups(subgroups)
trackdb.add_tracks(composite)

bed_view = ViewTrack(
    name="bedViewTrack",
    view="Bed",
    visibility="squish",
    tracktype="bigBed 3",
    short_label="beds",
    long_label="Beds")

signal_view = ViewTrack(
    name="signalViewTrack",
    view="Signal",
    visibility="full",
    tracktype="bigWig",
    short_label="signal",
    long_label="Signal")
composite.add_view(bed_view)
composite.add_view(signal_view)

for view in composite.views:
    view.add_params(configurable="on")

from trackhub import helpers
bbs = helpers.example_bigbeds()
bws = helpers.example_bigwigs()

bw_p = {'1000': 'lo',   '10000': 'hi'}
bw_c = {'1000': 'a',    '10000': 'b'}
bb_s = {'0': 'small', '1': 'med', '2': 'lg'}
bb_c = {'0': 'a',     '1': 'a',   '2': 'b'}

import os
from trackhub import Track

# A quick function to return the number in the middle of filenames -- this
# will become the key into the subgroup dictionaries above
def num_from_fn(fn):
    return os.path.basename(fn).split('.')[0].split('-')[-1]

# Make the bigBed tracks
for bb in sorted(bbs):
    num = num_from_fn(bb)
    basename = os.path.basename(bb)
    track = Track(
        name='features%s' % num,
        tracktype='bigBed 3',
        local_fn=bb,
        shortLabel='features %s' % num,
        longLabel='features %s' % num,
        subgroups=dict(
            size=bb_s[num],
            celltype=bb_c[num]))

    # add this track to the bed view
    bed_view.add_tracks(track)

# Make the bigWig tracks
for bw in sorted(bws):
    num = num_from_fn(bw)
    basename = os.path.basename(bw)
    track = Track(
        name='signal%s' % num,
        tracktype='bigWig',
        local_fn=bw,
        shortLabel='signal %s' % num,
        longLabel='signal %s' % num,
        subgroups=dict(
            frequency=bw_p[num],
            celltype=bw_c[num]))

    # add this track to the signal view
    signal_view.add_tracks(track)


for track in signal_view.subtracks:
    track.add_params(viewLimits='0:3', autoScale='off')

hub.url = os.path.join(URL_BASE, 'myhub.txt')
hub.remote_fn = os.path.join(REMOTE_BASE, 'myhub.txt')

hub.render()

from trackhub.upload import upload_track, upload_hub
for track in trackdb.tracks:
    #upload_track(track=track, host=HOST, user=USER)
    pass
    print track.kwargs
upload_hub(hub=hub, host=HOST, user=USER)


print
print hub.url
print
