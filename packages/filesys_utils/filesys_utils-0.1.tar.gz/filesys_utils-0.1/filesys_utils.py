# Author: Andrea Leopardi
# email: an.leopardi@gmail.com
# skype: whatyouhide
# Developed in L'Aquila, Italy
# December 2012

"""
Tested for:
- 2.6+
- 2.7+

This module provides functions to analyze disks and directories. It works only on Unix systems (Linux, Mac OS X) (for now...).
It provides functions in two standard forms: function_name and function_name_str:
the first one returns a floating point number as its output, while the second one returns a string.

NB: whatever path you pass as an argument of one of the functions which deal with disks space,
the function will return information about the disk the given path belongs to.
So in Linux, for example, free_space('/') and free_space('/usr/bin') will return the same result.
""" 

# Imports
# os: for most of the operations in this module
# statvfs: a helper module to remember the constants needed in os.statvfs(). Could be replaced with actual numbers.
import os, statvfs


# Exceptions
class InvalidSizeException(Exception):
	"""Raised when one of the functions in this module is called with an invalid size, like bit.

	Attributes:
	- msg: a message explaining what caused the exception.
	"""
	def __init__(self):
		import StringIO
		self.msg = StringIO.StringIO()
		print >> self.msg, 'You entered an invalid size. Valid sizes are:'
		print >> self.msg, 'B  --> bytes'
		print >> self.msg, 'KB --> kilobytes'
		print >> self.msg, 'MB --> megabytes'
		print >> self.msg, 'GB --> gigabytes'
		print >> self.msg, 'TB --> terabytes'
		self.msg = self.msg.getvalue()


# Module constants
CONVERSION_UNIT = 1000.0 # Should be 1024, but many systems use 1000 as conversion unit between different sizes


# Methods

def _isdir(path):
	"""Used instead of os.path.isdir() because _isdir doesn't follow links."""
	return os.path.isdir(path) and not os.path.islink(path)

def _isfile(path):
	"""Used instead of os.path.isfile() because _isfile doesn't follow links."""
	return os.path.isfile(path) and not os.path.islink(path)

def _convert_size(bytes, size='B'):
	"""Converts the given integer (expressing bytes) to a floating point number in the given size."""
	s = size.upper()
	if s == 'TB':
		return bytes / CONVERSION_UNIT**4
	elif s == 'GB':
		return bytes / CONVERSION_UNIT**3
	elif s == 'MB':
		return bytes / CONVERSION_UNIT**2
	elif s == 'KB':
		return bytes / CONVERSION_UNIT
	elif s == 'B':
		return float(bytes)
	elif s == 'BIT':
		return 8.0 * bytes
	else:
		raise InvalidSizeException

def _are_there_dirs(path):
	"""Returns True if there are directories in the specified path."""
	# if path[-1] != '/': path += '/' would have worked, but only under Unix
	for elem in os.listdir(path):
		if os.path.isdir(os.path.join(path, elem)): return True
	return False

def _sum_files_sizes(path):
	"""Returns the sum of the file sizes in the given directory. This size is expressed in bytes.
	Note that this function reads only the size of the files, not the directories sizes.
	By default, it returns the size of the current working directory."""
	# if path[-1] != '/': path += '/' would have worked, but only under Unix
	return sum([os.path.getsize(os.path.join(path, elem)) for elem in os.listdir(path) if _isfile(os.path.join(path, elem))])

def free_space(disk='/', size='GB'):
	"""Returns a real number representing the entire (if disk is left to '/') disk free space
	expressend in specified size, which is 'GB' by default."""
	stats = os.statvfs(disk)
	free_bytes = stats[statvfs.F_FRSIZE] * stats[statvfs.F_BAVAIL]
	return _convert_size(free_bytes, size)

def free_space_str(disk='/', size='GB'):
	"""Returns a string in the form of 'FREE_SPACE' SIZE, for example '143.03 GB', representing the entire
	(if disk is left to '/') disk free space in the specified size."""
	return '%.2f %s' % (free_space(disk, size), size.upper())

def total_space(disk='/', size='GB'):
	"""Returns a real number representing the (if disk is left to '/') entire disk space
	expressend in specified size, which is 'GB' by default."""
	stats = os.statvfs(disk)
	tot_bytes = stats[statvfs.F_FRSIZE] * stats[statvfs.F_BLOCKS]
	return _convert_size(tot_bytes, size)

def total_space_str(disk='/', size='GB'):
	"""Returns a string in the form of 'FREE_SPACE' SIZE, for example '143.03 GB', representing the entire
	disk space in the specified size."""
	return '%.2f %s' % (total_space(disk, size), size.upper())

def used_space(disk='/', size='GB'):
	"""Returns a floating point number representing the selected disk used space"""
	return total_space(disk, size) - free_space(disk, size)

def used_space_str(disk='/', size='GB'):
	"""Returns a string in the form of 'USED_SPACE' SIZE, for example '143.03 GB', representing the used
	disk space in the specified size."""
	return '%.2f %s' % (used_space(disk, size), size.upper())

def _dir_size_bytes(path):
	"""Returns the size, expressed in bytes, of the given directory. Path has to end with a '/'."""
	# This function works recursively finding the size of the non-dirs elements
	# in the given folder and then entering every nested folder, until it finds
	# a folder with no directories in it.
	# NB: Exceptions are handled in 'dir_size' function.

	# BIG NOTE: list comprehension is faster than looping (looping is done in Python, while list
	# comprehension is done in C), so here I paste the for loop which corresponds the list comprehension
	# for easier debugging.
	# 
	# inner_sizes = [_sum_files_sizes(path)]
	# for elem in os.listdir(path):
	# 	new_path = os.path.join(path, elem)
	# 	if _isdir(new_path):
	# 		inner_sizes.append(_dir_size_bytes(new_path))
	# return sum(inner_sizes)

	if not _are_there_dirs(path):
		return _sum_files_sizes(path)
	else:
		return _sum_files_sizes(path) + sum([_dir_size_bytes(os.path.join(path, elem)) for elem in os.listdir(path) if _isdir(os.path.join(path, elem))])

def dir_size(path, size='B'):
	"""Returns the size of the given directory expressed in the specified size (as a floating point number)"""
	if not os.path.isdir(path): raise OSError('Not a directory')
	return _convert_size(_dir_size_bytes(path), size)

def dir_size_str(path, size='B'):
	"""Returns a string containing the size of the given directory expressed in the specified size in the 
	form of, for example, 141.32 MB."""
	return '%.2f %s' % (dir_size(path, size), size.upper())

def file_size(path, size='B'):
	"""Returns a floating point number representing the given file size"""
	if not os.path.isfile(path): raise OSError('Not a file')
	return _convert_size(os.path.getsize(path), size)

def file_size_str(path, size='B'):
	"""Returns a string containing the size of the given file expressed in the specified size in the 
	form of, for example, 141.32 MB."""
	return '%.2f %s' % (file_size(path, size), size.upper())

def disk_summary(disk='/', size='GB'):
	"""Returns a string containing informations about the given disk, which is the current running OS one,
	with sizes expressed as given."""
	infos = {
		'tot_str': total_space_str(disk, size),
		'free_str': free_space_str(disk, size),
		'used_str': used_space_str(disk, size),
		'free_perc_str': '%.1f%s' % (free_space(disk, size) / total_space(disk, size) * 100, '%'),
		'used_perc_str': '%.1f%s' % (used_space(disk, size) / total_space(disk, size) * 100, '%')
		}

	import StringIO
	output = StringIO.StringIO()
	print >> output, 'These are the informations available for the selected disk space:'
	print >> output, '--- Total space: %(tot_str)s' % infos
	print >> output, '--- Used space: %(used_str)s (%(used_perc_str)s of the total space)' % infos
	print >> output, '--- Free space: %(free_str)s (%(free_perc_str)s of the total space)' % infos
	return output.getvalue()


# DEBUGGING
if __name__ == '__main__':
	PATH = '/Users/andrealeopardi/Music'
	# for direct in os.listdir(PATH):
	# 	if os.path.isdir(PATH + '/' + direct):
	# 		size = dir_size(PATH + '/' + direct, 'mb')
	# 		if size > 0.00:
	# 			print '%s:\t%s' % (direct, dir_size_str(PATH + '/' + direct, 'mb'))
	print _are_there_dirs('/Users/')
	print dir_size_str(PATH, 'gb')

	#print dir_size_str('/Users/andrealeopardi/Library', 'gb')