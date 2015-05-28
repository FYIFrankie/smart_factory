from flask import Flask, request, send_file
from threading import Lock
from pprint import pprint
import datetime
import json
import time
import on_store
import evil_script
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
try:
	import cPickle as pickle
except ImportError:
	import pickle

app = Flask(__name__)
lock = Lock()
log_lock = Lock()


def crossdomain(origin=None, methods=None, headers=None,
				max_age=21600, attach_to_all=True,
				automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, str):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, str):
		origin = ', '.join(origin)
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods

		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp

			h = resp.headers

			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp

		f.provide_automatic_options = False
		return update_wrapper(wrapped_function, f)
	return decorator
	
def write_out():
	global group_data, lock
	lock.acquire()
	info = open('info', "wb")
	try:
		pickle.dump(group_data, info)
	finally:
		info.close()
		lock.release()

try:
	existing_file = open('info', "rb")
	group_data = pickle.load(existing_file)
	print("Group data file exsits")
	existing_file.close()
except:
	group_data = []
	write_out()

logs = open('log_file.txt', "a")
logs.close()


def log(args, values, base_url, remote_addr):
	global log_lock
	log_lock.acquire()

	try:
		data = {}
		for key in args.keys():
			if key == 'value':
				data[key] = values.getlist('value')
			else:
				data[key] = str(args[key])
		read_log = open('log_file.txt', 'r').readlines()
		with open('log_file.txt', 'w+') as log_file:
			log_file.write('URL Accessed: ' + base_url +'\n' + 'Time Accessed: ' + str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")) + "\n" + 'IP Address: ' + str(remote_addr) + "\n" + 'Params: \n')
			pprint(data, stream=log_file, width=1, indent=1)
			log_file.write("\n")
			log_file.writelines(read_log)
	finally:
		log_file.close()
		log_lock.release()


@app.route('/favicon.ico')
def favicon():
	return '0'

@app.route('/log', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def log_route():
	return send_file('log_file.txt')

@app.route('/help', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def help_route():
	return send_file('help.txt')

@app.errorhandler(404)
def page_not_found(e):
	log(request.args, request.values, request.base_url, request.remote_addr)
	return 'Your route is incorrect'

@app.route('/append', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def append_route():
	global group_data

	log(request.args, request.values, request.base_url, request.remote_addr)
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"
	try:
		value = request.args['value']
	except KeyError:
		return "Params don't contain value. Example: {'value': 'truck1'}"

	for item in group_data:
		if item['key'] == key:
			if value in item['value']:
				return (key + ' already contains ' + value)
			else:
				item['value'].append(value)
				write_out()
				try:
					on_store.main(group_data, store_data)
				except:
					print("An error has occurred in the student script")
				try:
					evil_script.main(group_data, store_data)
				except:
					print("An error has occurred in the evil script")
				return (value + ' successfully added to ' + key)

	group_data.append({'key' : str(key), 'value' : [value], 'date': str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")) })
	try:
		on_store.main(group_data, store_data)
	except:
		print("An error has occurred in the student script")
	try:
		evil_script.main(group_data, store_data)
	except:
		print("An error has occurred in the evil script")
	write_out()
	return (value + ' successfully added to ' + key)



@app.route('/remove', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def remove_route():
	global group_data

	log(request.args, request.values, request.base_url, request.remote_addr)
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"
	try:
		value = request.args['value']
	except KeyError:
		return "Params don't contain value. Example: {'value': 'truck1'}"

	for item in group_data:
		if item['key'] == key:
			if value not in item['value']:
				return (key + ' does not contain ' + value)
			else:
				item['value'].remove(value)
				write_out()
				return (value + ' succesfully removed from ' + key)
	return 'Key '+ key + ' is not in data'




@app.route('/retrieve', methods= ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def retrieve_route():

	global group_data

	log(request.args, request.values, request.base_url, request.remote_addr)

	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"

	data = []
	if (key == '*group'):
		return json.dumps(group_data)
	else:
		for item in group_data:
			if item['key'] == key:
				return json.dumps(item)
		return ('Key is not stored in ' + group + ' data')



@app.route('/store', methods= ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def store_route():
	global group_data


	log(request.args, request.values, request.base_url, request.remote_addr)
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"
	try:
		value = request.values.getlist('value')
	except KeyError:
		return "Params don't contain value. Example: {'value': ['t1', 'fire']...}"
	store_data = {'key': key, 'value': value}
	for item in group_data:
		if item['key'] == key:
			item['value'] = value
			item['date'] = str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p"))
			write_out()
			try:
				on_store.main(group_data, store_data)
			except:
				print("An error has occurred in the student script")
			try:
				evil_script.main(group_data,store_data )
			except:
				print("An error has occurred in the evil script")
			return ('Successfully updated ' + key +  ' to value ' + str([str(x) for x in value]))

	group_data.append({'key' : str(key), 'value' : value, 'date': str(datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")) })
	try:
		on_store.main(group_data, store_data)
	except:
		print("An error has occurred in the student script")
	try:
		evil_script.main(group_data, store_data)
	except:
		print("An error has occurred in the evil script")
	write_out()
	return ('Successfully added ' + key +  ' with value ' + str([str(x) for x in value]))



@app.route('/clear_key', methods= ['GET', 'OPTIONS'])
@crossdomain(origin='*')
def clear_route():
	global group_data

	log(request.args, request.values, request.base_url, request.remote_addr)
	
	try:
		key = request.args['key']
	except KeyError:
		return "Params don't contain key. Example: {'key': 'example_key',...}"


	group_data[:] = [x for x in group_data if x['key'] != key]

	write_out()
	return ('Successfully removed ' + key)




app.run(port = 5000, host='0.0.0.0')