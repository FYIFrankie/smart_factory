from pprint import pprint
import datetime
try:
	import cPickle as pickle
except ImportError:
	import pickle


def write_out(group_data, pickle_lock):
	"""Serialize the current user data to the info file."""

	# lock to assure two requests aren't serialized simultaneously 
	pickle_lock.acquire()

	info = open('info', "wb")
	try:
		pickle.dump(group_data, info)
	finally:
		info.close()
		pickle_lock.release()


def log_request(args, values, base_url, remote_addr, log_lock):
	"""Format and log the request at the top of the log file.
	Does this is a bit of a backwards way to ensure the top of
	the log file has the most recent entry.

	Keyword arguments:
	args -- Arguments from the GET request
	values -- Values from the GET request
	base_url -- URL client accessed to make GET request 
	remote_addr -- IP address of the client
	log_lock -- Lock for thread safety
	"""
	# lock to assure two requests aren't logged simultaneously

	log_lock.acquire()

	try:
		data = {}
		# iterate over all keys in request
		for key in args.keys():
			# if the key's name is 'value' then the value will be a list						
			if key == 'value': 
				data[key] = values.getlist('value')
			# otherwise it will just be one string 
			else:
				data[key] = str(args[key])
		# cache current log_file in list

		read_log = open('log_file.txt', 'r').readlines()
		# open log_file with w+, deleting all current data
		# and write new entry to log
		with open('log_file.txt', 'w+') as log_file:
			log_file.write('URL Accessed: ' + base_url +'\n' + 'Time Accessed: ' + str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")) + "\n" + 'IP Address: ' + str(remote_addr) + "\n" + 'Params: \n')
			pprint(data, stream=log_file, width=1, indent=1)
			log_file.write("\n")
			# rewrite the cached old data below new data in log_file
			log_file.writelines(read_log)
	finally:
		log_file.close()
		log_lock.release()