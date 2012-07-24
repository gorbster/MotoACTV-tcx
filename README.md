# Overview #
Simple Python script that converts the MotoACTV CSV format to TCX. Useful for uploading MotoACTV workout data to sites like [Strava](http://www.strava.com) or [RunKeeper](http://www.runkeeper.com).

# Notes #
The workout data is condensed to a single Lap / Track. Heart-rate information will be included if it exists in the CSV file, but power data is not read. Elevation data may not be correctly handled, but most fitness sites will re-calculate elevation based on the position data.

# Usage #
    ./motoactv_tcx.py <CSV file> | tidy -q -i -xml > output.tcx

# Requirements #
* [ElementTree](http://effbot.org/zone/element-index.htm)