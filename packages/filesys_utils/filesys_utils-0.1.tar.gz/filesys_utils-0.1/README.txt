This module provides functions to analyze disks and directories. It works only on Unix systems (Linux, Mac OS X) (for now...).
It provides functions in two standard forms: function_name and function_name_str:
the first one returns a floating point number as its output, while the second one returns a string.

NB: whatever path you pass as an argument of one of the functions which deal with disks space,
the function will return information about the disk the given path belongs to.
So in Linux, for example, free_space('/') and free_space('/usr/bin') will return the same result.