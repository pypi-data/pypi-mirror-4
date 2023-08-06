'''
File: splitter.py
Author: Jon Eisen
Description: Calculate parameters to split SQL data before transfer.
'''
import logging
from split import SqlSplit

def calculate_splits(config):
    """reads config to find out what type of split to perform"""

    if config.get("split", False):
      logging.error("Input splits are not implemented!")

    logging.info("Non-Split mode calculation entering.")
    return calculate_single_split(config)

def calculate_single_split(config):
	'''Returns parameters for a single split'''
	split = SqlSplit(
		sqltype = config.get('sqltype'),
		connargs = config.get('connargs'),
		query = config.get('query')
	)

	logging.debug('Calculated split: %s' % split)

	return [split.uri()]