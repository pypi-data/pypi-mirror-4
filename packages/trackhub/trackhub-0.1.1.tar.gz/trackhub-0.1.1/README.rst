``trackhub``
============

``trackhub`` is a Python package for handling the creation and uploading of
track hubs for the UCSC Genome Browser (see
http://genome.ucsc.edu/goldenPath/help/hgTrackHubHelp.html for more info)

Some reasons for using ``trackhub`` to manage your track hubs:

* `filename handling`: automatic (yet still completely configurable, if needed)
  handling of filenames and directory structure
* `uploading`: upload a full hub -- hub/genomes/trackdb files, plus all data
  files (bam/bigWig/bigBed) -- via rsync over ssh
* `validation`: mechanisms for handling validation of parameters so errors are
  [hopefully] caught prior to uploading
* `rapid deployment`: mapping local filenames to remote filenames on the host enables
  rapid updating of the hub with new or updated data (e.g., when analysis
  parameters change)
* `flexibility`: support for simple hubs up through complex composite hubs with
  views and subtracks
* `extensible`: provides a framework for working with hub components, allowing
  new functionality to be easily added


Full documentation, including a full in-depth tutorial, can be found at
http://packages.python.org/trackhub.


**Note:** ``trackhub`` is still under active development and should be considered an
alpha version.  Please open an issue on github
(https://github.com/daler/trackhub/issues) if you run into problems.


Copyright 2012 Ryan Dale; BSD 2-clause license.
