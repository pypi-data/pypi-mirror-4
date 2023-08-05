#!/usr/bin/python

import os
import sys
import argparse
from trackhub import Hub, GenomesFile, Genome, TrackDb, Track
from trackhub.upload import upload_track, upload_hub
from trackhub import helpers

ap = argparse.ArgumentParser()
ap.add_argument('--host', help='host to upload to')
ap.add_argument('--urlbase', help='top-level publicly-accessible dir on host')
ap.add_argument('--user', help='user for host')
ap.add_argument('--upload-dir', dest='upload_dir',
                help='directory on host to upload hub to')
args = ap.parse_args()

for k, v in args._get_kwargs():
    if v is None:
        ap.print_help()
        sys.exit(1)

URLBASE = args.urlbase
GENOME = 'dm3'

hub = Hub(
    hub='example_hub',
    short_label='example hub',
    long_label='an example hub for testing',
    email='none@example.com')
genomes_file = GenomesFile()
genome = Genome(GENOME)
trackdb = TrackDb()

t1, t2 = helpers.example_bigwigs()

print t1

track1 = Track(
    name="track1Track",
    url=os.path.join(URLBASE, GENOME, 'track1.bigWig'),
    local_fn=t1,
    tracktype='bigWig',
    short_label='track1',
    long_label='my track #1',
    color='128,0,0')

track2 = Track(
    name="track2Track",
    url=os.path.join(URLBASE, GENOME, 'track2.bigWig'),
    local_fn=t2,
    tracktype='bigWig',
    short_label='track2',
    long_label='my track #2',
    color='0,0,255')

trackdb.add_tracks([track1, track2])
genome.add_trackdb(trackdb)
genomes_file.add_genome(genome)
hub.add_genomes_file(genomes_file)
results = hub.render()


hub.upload_fn = os.path.join(args.upload_dir, os.path.basename(hub.filename))

for track in trackdb.tracks:
    track.upload_fn = os.path.join(args.upload_dir, GENOME, os.path.basename(track.local_fn))
    upload_track(track=track, host=args.host, user=args.user)

upload_hub(hub=hub, host=args.host, user=args.user)
