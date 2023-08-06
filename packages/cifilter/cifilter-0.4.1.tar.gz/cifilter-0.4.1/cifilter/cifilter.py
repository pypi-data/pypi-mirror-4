#!/usr/bin/env python

import logging
import optparse
import os
import sys
import Foundation
import Quartz
import CoreFoundation
import re
from copy import copy
import tempfile
# import traceback
import commands

########################################################################
#### Set up logging

logger = logging.getLogger('cifilter')
handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

########################################################################
#### Support functions for optparse

def check_NSNumber(option, opt, value):
	try:
		return Foundation.NSNumber.numberWithDouble_(float(value))
	except ValueError:
		raise OptionValueError('option %s: invalid NSNumber value: %r' % (opt, value))

def check_CIColor(option, opt, value):
	try:
		theChannels = [float(C) for C in value.split(',')]
		value = Quartz.CIColor.colorWithRed_green_blue_alpha_(*theChannels)
		return value
	except ValueError:
		raise OptionValueError('option %s: invalid CIColor value: %r' % (opt, value))

def check_CIVector(option, opt, value):
	try:
		theValues = [float(C) for C in value.split(',')]
		if len(theValues) == 4:
			value = Quartz.CIVector.vectorWithX_Y_Z_W_(*theValues)
		elif len(theValues) == 3:
			value = Quartz.CIVector.vectorWithX_Y_Z_(*theValues)
		elif len(theValues) == 2:
			value = Quartz.CIVector.vectorWithX_Y_(*theValues)
		elif len(theValues) == 1:
			value = Quartz.CIVector.vectorWithX_(*theValues)
		return value
	except ValueError:
		raise OptionValueError('option %s: invalid CIColor value: %r' % (opt, value))

def check_CIImage(option, opt, value):
	try:
		if value != '-':
			value = os.path.expanduser(value)
			value = open(value).read()
			value = Foundation.NSData.dataWithBytes_length_(value, len(value))
			value = Quartz.CIImage.imageWithData_(value)
		return value
	except ValueError:
		raise OptionValueError('option %s: invalid CIColor value: %r' % (opt, value))

class MyOption(optparse.Option):
	TYPES = optparse.Option.TYPES + ('CIImage', 'NSNumber', 'CIColor', 'CIVector', )
	TYPE_CHECKER = copy(optparse.Option.TYPE_CHECKER)
	TYPE_CHECKER['NSNumber'] = check_NSNumber
	TYPE_CHECKER['CIImage'] = check_CIImage
	TYPE_CHECKER['CIColor'] = check_CIColor
	TYPE_CHECKER['CIVector'] = check_CIVector

def store_open_file(option, opt_str, value, parser, *args, **kwargs):
	if value == '-' and '-' in kwargs:
		theFile = kwargs['-']
	else:
		theMode = kwargs['mode'] if 'mode' in kwargs else 'r'
		theFile = file(os.path.expanduser(value), theMode)
	setattr(parser.values, option.dest, theFile)

########################################################################
#### Main entry point

def cifilter(args):
	#### Set up optparse
	theUsage = '''%prog [options]'''
	theVersion = '%prog 0.4'

	parser = optparse.OptionParser(usage=theUsage, version=theVersion, option_class=MyOption)

	parser.remove_option('--help')

	parser.add_option('-h', '--help', action='store_const', dest='action', const='help',
		help='Help!')
	parser.add_option('-i', '--inputImage', action='store', dest='inputImage', default = '-', type='CIImage', metavar='INPUT',
		help='The input image (or - for stdin)')
	parser.add_option('-o', '--outputImage', action='callback', dest='outputImage', type='string', default = None, callback=store_open_file, callback_kwargs = {'mode':'w', '-':sys.stdout}, metavar='OUTPUT',
		help='The output image (or - for stdout)')
	parser.add_option('-f', '--filter', action='store', dest='filter', type='string', default = None, metavar='FILTER',
		help='Name of the filter')
#	parser.add_option('-p', '--filterpath', action='store', dest='filter_path', type='string', default = None, metavar='FILTER_PATH',
#		help='Path to a filter')
	parser.add_option('', '--listfilters', action='store_const', dest='action', const='listfilters',
		help='List available CoreImage filters')
	parser.add_option('', '--listcategories', action='store_const', dest='action', const='listcategories',
		help='List available CoreImage filter categories')
	parser.add_option('', '--category', action='store', dest='category', type='string', default=None,
		help='Category used to filter listfilter results')
	parser.add_option('', '--width', action='store', dest='width', type='int', default=None,
		help='Desired width of output image')
	parser.add_option('', '--height', action='store', dest='height', type='int', default=None,
		help='Desired height of output image')
	parser.add_option('', '--type', action='store', dest='type', type='string', default='public.png',
		help='Desired UTI type of output image (e.g. public.png, public.jpg, etc)')
	parser.add_option('-v', '--verbose', action='store_const', dest='loglevel', const=logging.INFO, default=logging.WARNING,
		help='Set the log level to INFO')
	parser.add_option('', '--loglevel', action='store', dest='loglevel', type='int',
		help='set the log level, 0 = no log, 10+ = level of logging')
	parser.add_option('', '--logfile', action='callback', dest='logstream', type='string', default = sys.stderr, callback=store_open_file, callback_kwargs = {'mode':'w'}, metavar='LOG_FILE',
		help='File to log messages to. If - or not provided then stdout is used')
	parser.add_option('', '--open', action='store_const', dest='open', const = True, default = False,
		help='Open the output image after processing')


	Quartz.CIPlugIn.loadAllPlugIns()

	#### Try and guess the filter name (we can't use our optparser right now because it'll puke about all the filter specific options)
	theFilterName = None
	for N, arg in enumerate(args):
		if theFilterName:
			break
		for pattern in ['^--filter=(.+)$', '^--filter$', '^-f$' ]:
			theMatch = re.match(pattern, arg)
			if theMatch:
				if len(theMatch.groups()) == 0:
					theFilterName = args[N + 1]
					break
				else:
					theFilterName = theMatch.groups()[0]
					break

	#### If we have a filter we can add options to our optparser based on the filter inputKeys
	if theFilterName:
		parser.usage = '%%prog --filter %s [options]' % theFilterName

		theFilter = Quartz.CIFilter.filterWithName_(theFilterName)
		if theFilter == None:
			logger.error('Cannot find filter called \'%s\'', theFilterName)
			sys.exit(1)
		for theInputKey in theFilter.inputKeys():
			theOption = '--%s' % theInputKey
			if not parser.has_option(theOption):
				theAttributes = theFilter.attributes()
				theAttributes = theAttributes[theInputKey]
				if theAttributes:
					theDefault = theAttributes['CIAttributeDefault'] if 'CIAttributeDefault' in theAttributes else None
					theAttributeDescription = theAttributes['CIAttributeDescription'] if 'CIAttributeDescription' in theAttributes else '(No description)'
					theType = theAttributes['CIAttributeClass']
					theHelp = theAttributeDescription
					if theType:
						theHelp += ' Type: \'%s\'.' % theType
					if theDefault:
						theHelp += ' Default: \'%s\'.' % theDefault
					parser.add_option('', theOption, action='store', dest=theInputKey, type=theType, metavar='VALUE', default = theDefault, help=theHelp)

	#### And we're off!
	(options, theArguments) = parser.parse_args(args = args[1:])

	logger.setLevel(options.loglevel)

	logger.debug(options)
	logger.debug(theArguments)

	#### Decide what action to perform
	if options.action == 'listfilters':
		listfilters(options, theArguments)
	if options.action == 'listcategories':
		listcategories(options, theArguments)
	elif options.action == 'help':
		parser.print_help()
	else:
		filter(options, theArguments)

########################################################################
#### listfilters

def listfilters(options, arguments):
	theFilterNames = list(Quartz.CIFilter.filterNamesInCategories_([options.category] if options.category else None))
	theFilterNames.sort()
	for theFilterName in theFilterNames:
		theFilter = Quartz.CIFilter.filterWithName_(theFilterName)
		if not theFilter:
		    logger.warning('Could not load filter: %s' % theFilterName)
		    continue
		theAttributes = theFilter.attributes()
		print '%s - %s' % (theFilterName, theAttributes['CIAttributeDescription'])

########################################################################
#### listcategories

def listcategories(options, arguments):
	theCategories = set()
	for theFilterName in Quartz.CIFilter.filterNamesInCategories_(None):
		theFilter = Quartz.CIFilter.filterWithName_(theFilterName)
		if not theFilter:
		    logger.warning('Could not load filter: %s' % theFilterName)
		    continue
		theAttributes = theFilter.attributes()
		for theCategory in theAttributes['CIAttributeFilterCategories']:
			theCategories.add(theCategory)
	theCategories = list(theCategories)
	theCategories.sort()
	for theCategory in theCategories:
		print theCategory

########################################################################
#### filter - this is the workhorse function

def filter(options, inArguments):
	# TODO - fix all the leaks so this can be used properly directly from python

	if options.filter == None:
		logger.error('No filter specified')
		sys.exit(1)

	#### Create a filter
	logger.info('Using Filter: \'%s\'' % (options.filter))
	theFilter = Quartz.CIFilter.filterWithName_(options.filter)
	if theFilter == None:
		logger.error('Cannot find filter called \'%s\'', options.filter)
		sys.exit(1)

	#### Set all the inputkeys we can (from options)
	for theInputKey in theFilter.inputKeys():
		if hasattr(options, theInputKey):
			theValue = getattr(options, theInputKey)
			theAttributeClass = theFilter.attributes()[theInputKey]['CIAttributeClass']
			if theAttributeClass == 'CIImage' and theValue == '-':
				theValue = sys.stdin.read()
				theValue = Foundation.NSData.dataWithBytes_length_(theValue, len(theValue))
				theValue = Quartz.CIImage.imageWithData_(theValue)
			logger.info('\'%s\' = \'%s\'' % (theInputKey, str(theValue).replace('\n', ' ').strip()))
			theFilter.setValue_forKey_(theValue, theInputKey)

	theOutputImage = theFilter._.outputImage

	########################################################################

	#### Work out the final extent of the image
	theExtent = theOutputImage.extent()
	options.width = options.width if options.width else int(Quartz.CGRectGetWidth(theExtent))
	options.width = options.width if options.width < 1e10 else 1024
	options.height = options.height if options.height else int(Quartz.CGRectGetHeight(theExtent))
	options.height = options.height if options.height < 1e10 else 1024

	#### Create a quartz bitmap context
	bitmapBytesPerRow = options.width * 4
	bitmapByteCount = bitmapBytesPerRow * options.height
	theColorSpace = Quartz.CGColorSpaceCreateDeviceRGB()
	theBitmapData = Foundation.NSMutableData.dataWithLength_(bitmapByteCount)

	theQuartzContext = Quartz.CGBitmapContextCreate(theBitmapData.mutableBytes(), options.width, options.height, 8, bitmapBytesPerRow, theColorSpace, Quartz.kCGImageAlphaPremultipliedLast)

	Quartz.CFRelease(theColorSpace)

	#### Draw CIImage into context and create a Quartz image from the bitmap context
	theCoreImageContext = Quartz.CIContext.contextWithCGContext_options_(theQuartzContext, None)
	theRect = Quartz.CGRectMake(0, 0, options.width, options.height)
	theCoreImageContext.drawImage_atPoint_fromRect_(theOutputImage, (0,0), theRect)
	theQuartzImage = Quartz.CGBitmapContextCreateImage(theQuartzContext)

	#### Output the quartz image into a NSMutableData
	theOutputData = Foundation.NSMutableData.data()
	theImageDestination = Quartz.CGImageDestinationCreateWithData(theOutputData, options.type, 1, None)
	Quartz.CGImageDestinationAddImage(theImageDestination, theQuartzImage, None)
	Quartz.CGImageDestinationFinalize(theImageDestination)

	#### Write to our outputImage (if there is one)
	if options.outputImage:
		options.outputImage.write(theOutputData.bytes()[0:theOutputData.length()])

	#### Optionally write to a temp file and open it in Preview.app
	if options.open:
		theHandle, theFile = tempfile.mkstemp(suffix = '.' + extensionForUTI(options.type))
		file(theFile, 'w').write(theOutputData.bytes()[0:theOutputData.length()])
		status, output = commands.getstatusoutput('open -b com.apple.preview \'%s\'' % theFile)
		if status != 0:
			logger.error('Failed to open image')
			sys.exit(status)

def extensionForUTI(inType):
	d = {
		'public.png': 'png',
		'public.jpeg': 'jpg',
		'public.tiff': 'tiff',
		'public.jpeg-2000': 'jp2',
		}
	return d[inType] if inType in d else None

main = cifilter

########################################################################

if __name__ == '__main__':
	main(sys.argv)
