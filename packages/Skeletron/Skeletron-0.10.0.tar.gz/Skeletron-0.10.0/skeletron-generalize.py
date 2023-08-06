#!/usr/bin/env python
from json import load, JSONEncoder
from optparse import OptionParser
from itertools import repeat
from re import compile
import logging

from Skeletron.output import generalize_geojson_feature

float_pat = compile(r'^-?\d+\.\d+(e-?\d+)?$')
charfloat_pat = compile(r'^[\[,\,]-?\d+\.\d+(e-?\d+)?$')
earth_radius = 6378137

optparser = OptionParser(usage="""%prog [options] <geojson input file> <geojson output file>

Accepts GeoJSON input and generates GeoJSON output.""")

defaults = dict(zoom=12, width=15, single=False, loglevel=logging.INFO)

optparser.set_defaults(**defaults)

optparser.add_option('-z', '--zoom', dest='zoom',
                     type='int', help='Zoom level. Default value is %s.' % repr(defaults['zoom']))

optparser.add_option('-w', '--width', dest='width',
                     type='float', help='Line width at zoom level. Default value is %s.' % repr(defaults['width']))

optparser.add_option('-s', '--single', dest='single',
                     action='store_true',
                     help='Convert multi-geometries into single geometries on output.')

optparser.add_option('-v', '--verbose', dest='loglevel',
                     action='store_const', const=logging.DEBUG,
                     help='Output extra progress information.')

optparser.add_option('-q', '--quiet', dest='loglevel',
                     action='store_const', const=logging.WARNING,
                     help='Output no progress information.')

if __name__ == '__main__':

    options, (input_file, output_file) = optparser.parse_args()

    logging.basicConfig(level=options.loglevel, format='%(levelname)08s - %(message)s')
    
    #
    # Input
    #
    
    input = load(open(input_file, 'r'))
    features = []
    
    for (index, input_feature) in enumerate(input['features']):
        try:
            feature = generalize_geojson_feature(input_feature, options.width, options.zoom)
            
            if not feature:
                continue

        except Exception, err:
            logging.error('Error on feature #%d: %s' % (index, err))

        else:
            if options.single and feature['geometry']['type'].startswith('Multi'):
                coord = [part for part in feature['geometry']['coordinates']]
                types = repeat(feature['geometry']['type'][5:])
                props = repeat(feature['properties'])
                
                features.extend([dict(type='Feature', geometry=dict(coordinates=coords, type=type), properties=prop)
                                 for (coords, type, prop) in zip(coord, types, props)])
            
            else:
                features.append(feature)
    
    #
    # Output
    #
    
    geojson = dict(type='FeatureCollection', features=filter(None, features))
    output = open(output_file, 'w')

    encoder = JSONEncoder(separators=(',', ':'))
    encoded = encoder.iterencode(geojson)
    
    for token in encoded:
        if charfloat_pat.match(token):
            # in python 2.7, we see a character followed by a float literal
            output.write(token[0] + '%.5f' % float(token[1:]))
        
        elif float_pat.match(token):
            # in python 2.6, we see a simple float literal
            output.write('%.5f' % float(token))
        
        else:
            output.write(token)
