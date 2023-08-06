mins = ()
secs = ()
def sanitize(time_string):
	""" this function standardizes the data to using a '.'
	to seperate minutes from seconds"""
	if '-' in time_string:
		splitter = '-'
	elif ':' in time_string:
		splitter = ':'
	else:
		return(time_string)
	(min, secs) = time_string.split(splitter)
	return(min + '.' + secs)