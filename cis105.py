try:
	import requests
except ImportError:
	print("Whoops, you don't have the requests library installed!")

IP_ADDRESS = 'localhost'

def append(item):
	if type(item) is not dict:
		return "Your parameter must be a dictionary with key and value"
	r = requests.get("http://" + IP_ADDRESS + ":5000/append", params={'key': item['key'], 'value': item['value']})
	return (str(r.text))

def remove(item):
	if type(item) is not dict:
		return "Your parameter must be a dictionary with key and value"
	r = requests.get("http://" + IP_ADDRESS + ":5000/remove", params={'key': item['key'], 'value': item['value']})
	return (str(r.text))


def store(payload):
	r = requests.get("http://" + IP_ADDRESS + ":5000/store", params=payload)
	return (str(r.text))


def parse_dict(dict_obj):
	temp_dict = {}
	for k, v in dict_obj.items():
		try:
			a = [str(x) for x in eval(str(v))]	
			temp_dict[str(k)] = a
		except (SyntaxError, NameError):
			temp_dict[str(k)] = str(v)
	return temp_dict



def retrieve(payload):
	r = requests.get("http://" + IP_ADDRESS + ":5000/retrieve", params=payload)
	array = []
	try:
		r.json()
	except ValueError:
		return str(r.text)

	if type(r.json()) is list:
		array = []
		for item in r.json():
			array.append(parse_dict(item))
		return array
	else:
		return parse_dict(r.json())


def clear_key(payload):
	r = requests.get("http://" + IP_ADDRESS + ":5000/clear_key", params=payload)
	return (str(r.text))

def get_item_color( item ):
	i = item.find('_')
	if i == -1:
		print('did not find a color in item ' + item)
		return ''
	return item[0:i]

def pick_up_cargo(truck, cargo, q):
	items = get_items( q )
	if truck not in items:
		print(truck + ' not in ' + q)
		return False
	if cargo not in items:
		print(cargo + ' not in ' + q)
		return False
	tcolor = get_item_color( truck )
	ccolor = get_item_color( cargo )
	if ccolor != 'universal' and tcolor != ccolor:
		print('cargo does not match truck')
		return False
	remove_item( q, truck )
	remove_item( q, cargo )
	add_item( q, truck + '-' + cargo )
	return True

def drop_off_cargo(truck, q):
	items = get_items( q )
	full_name = ''
	for item in items:
		if truck in item:
			full_name = item
			break
	if full_name == '':
		print(truck + ' not in ' + q)
		return False
	if 'cargo' not in full_name:
		print('cargo not on truck ' + truck)
		return False
	pieces = full_name.split('-')
	remove_item( q, full_name )
	add_item( q, pieces[0] ) # truck
	add_item( q, pieces[1] ) # cargo
	return True
	
def find_all_paths(start, end, path=[]):
	path = path + [start]
	if start == end:
		return [path] # path list
	paths = []
	for node in neighbors[start]:
		if node not in path:
			newpaths = find_all_paths(node, end, path)
			for newpath in newpaths:
				paths.append(newpath)
	return paths
