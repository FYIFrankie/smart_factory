from flask import Flask, request
from threading import Lock
from http_access import crossdomain
import datetime
import json
import store_scripts.on_store as on_store, store_scripts.evil_script as evil_script
import color_scripts.red as red, color_scripts.blue as blue, color_scripts.purple as purple
from file_io import write_out, log_request
try:
	import cPickle as pickle
except ImportError:
	import pickle


#create the Flask app
app = Flask(__name__)

#create the log and pickle locks
pickle_lock = Lock()
log_lock = Lock()

#try to load file with pickle 
try:
	existing_file = open('info', "rb")
	group_data = pickle.load(existing_file)
	print("Group data file exists")
	existing_file.close()
# if the file doesn't exist create it
except:
	group_data = []
	write_out(group_data, pickle_lock)


def try_scripts(group_data, store_data):
	"""Scripts to call after stores or appends to data are made

	Keyword arguments:
	group_data -- The entire data set that the group currently has stored in the factory
	store_data -- The data the the group has has to store in the GET request
	"""

	try:
		on_store.main(group_data, store_data)
	except:
		print("An error has occurred in the student script")
	try:
		evil_script.main(group_data, store_data)
	except:
		print("An error has occurred in the evil script")
	try:
		red.main(group_data, store_data)
	except:
		print("An error has occurred in the red script")
	try:
		blue.main(group_data, store_data)
	except:
		print("An error has occurred in the blue script")
	try:
		purple.main(group_data, store_data)
	except:
		print("An error has occurred in the purple script")


@app.route('/favicon.ico')
def favicon():
	"""Return '0' on favicon route so it doesn't default to page_not_found"""

	return '0'

@app.route('/log', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def log_route():
	"""Route to check log file"""

	return send_file('log_file.txt')

@app.route('/help', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def help_route():
	"""Route to view help file"""

	return send_file('help.txt')

@app.errorhandler(404)
def page_not_found(e):
	"""Deafult route for 404 error"""
	global log_lock

	#log_request(request.args, request.values, request.base_url, request.remote_addr, log_lock)
	return 'Your route is incorrect'

@app.route('/append', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def append_route():
	"""Route to append data to a key, or create a key and add a value to it"""

	global group_data, log_lock, pickle_lock

	# log the request - currently commented out
	#log_request(request.args, request.values, request.base_url, request.remote_addr, log_lock)

	# try to get key from request.args, return help_text if it isn't there
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"

	# try to get value from request.args, return help_text if it isn't there
	try:
		value = request.args['value']
	except KeyError:
		return "Params don't contain value. Example: {'value': 'truck1'}"

	# create store_data dictionary for the try_scripts call
	store_data = {'key': key, 'value': value}
	
	# iterate over items in group_data
	for item in group_data:
		# check if this dictionary has the same key as our request
		if item['key'] == key:
			# check if the value exists already for that key
			if value in item['value']:
				return (key + ' already contains ' + value)
			# if it doesn't, add item to list
			else:
				item['value'].append(value)
				item['date'] = str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p"))
				write_out(group_data, pickle_lock)
				#try_scripts(group_data, store_data)
				return (value + ' successfully added to ' + key)

	# if the key isn't currently in our group data, create it and add the value
	group_data.append({'key' : str(key), 'value' : [value], 'date': str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")) })
	write_out(group_data, pickle_lock)


	#try_scripts(group_data, store_data)
	return (value + ' successfully added to ' + key)



@app.route('/remove', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def remove_route():
	"""Route to remove a value from the list of values based on key"""
	global group_data, log_lock, pickle_lock

	# log the request - currently commented out
	#log_request(request.args, request.values, request.base_url, request.remote_addr, log_lock)

	# try to get key from request.args, return help_text if it isn't there
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"

	# try to get value from request.args, return help_text if it isn't there
	try:
		value = request.args['value']
	except KeyError:
		return "Params don't contain value. Example: {'value': 'truck1'}"


	# iterate over items in group_data
	for item in group_data:
		# check if this dictionary has the same key as our request
		if item['key'] == key:
			# if the requests value isn't in the item's list, can't remove it
			if value not in item['value']:
				return (key + ' does not contain ' + value)
			# otherwise remove and return success
			else:
				item['value'].remove(value)
				write_out(group_data, pickle_lock)
				return (value + ' successfully removed from ' + key)

	# return if requests key is not in our data
	return 'Key '+ key + ' is not in data'




@app.route('/retrieve', methods= ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def retrieve_route():
	"""Route to retrieve data based on key parameter"""


	global group_data, log_lock

	# log the request - currently commented out

	#log_request(request.args, request.values, request.base_url, request.remote_addr, log_lock)

	
	# try to get key from request.args, return help_text if it isn't there
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"


	# is the key is *group, return the entire group_data
	if (key == '*group'):
		return json.dumps(group_data)
	else:
		# if key isn't *group, iterate through group
		for item in group_data:
			if item['key'] == key:
				return json.dumps(item)
		return ('Key is not stored in data')



@app.route('/store', methods= ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def store_route():
	"""Route to store data to a key, or create a key and add a list to it"""

	global group_data, log_lock, pickle_lock

	# log the request - currently commented out
	#log_request(request.args, request.values, request.base_url, request.remote_addr, log_lock)

	# try to get key from request.args, return help_text if it isn't there
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"

	# try to get value list from request
	try:
		value = request.values.getlist('value')
	except KeyError:
		return "Params don't contain value. Example: {'value': ['t1', 'fire']...}"

	# create store_data dictionary for the try_scripts call
	store_data = {'key': key, 'value': value}

	for item in group_data:
		if item['key'] == key:
			item['value'] = value
			item['date'] = str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p"))
			write_out(group_data, pickle_lock)
			#try_scripts(group_data, store_data)
			return ('Successfully updated ' + key +  ' to value ' + str([str(x) for x in value]))


	group_data.append({'key' : str(key), 'value' : value, 'date': str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")) })
	#try_scripts(group_data, store_data)
	write_out(group_data, pickle_lock)
	return ('Successfully added ' + key +  ' with value ' + str([str(x) for x in value]))



@app.route('/clear_key', methods= ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def clear_route():
	"""Route to remove dictionary from group_data based on key """
	global group_data, log_lock, pickle_lock

	#log_request(request.args, request.values, request.base_url, request.remote_addr, log_lock)
	
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"

	# List comprehension to remove key from group_data 
	group_data[:] = [x for x in group_data if x['key'] != key]

	write_out(group_data, pickle_lock)
	return ('Successfully removed ' + key)


