try:
	import requests
except ImportError:
	print("Whoops, you don't have the requests library installed!")

IP_ADDRESS = 'localhost'

def raw_append(item):
	if type(item) is not dict:
		return "Your parameter must be a dictionary with key and value"
	r = requests.get("http://" + IP_ADDRESS + ":5000/append", params={'key': item['key'], 'value': item['value']})
	return (str(r.text))

def raw_remove(item):
	if type(item) is not dict:
		return "Your parameter must be a dictionary with key and value"
	r = requests.get("http://" + IP_ADDRESS + ":5000/remove", params={'key': item['key'], 'value': item['value']})
	return (str(r.text))


def raw_store(payload):
	r = requests.get("http://" + IP_ADDRESS + ":5000/store", params=payload)
	return (str(r.text))


def raw_parse_dict(dict_obj):
	temp_dict = {}
	for k, v in dict_obj.items():
		try:
			a = [str(x) for x in eval(str(v))]	
			temp_dict[str(k)] = a
		except (SyntaxError, NameError):
			temp_dict[str(k)] = str(v)
	return temp_dict



def raw_retrieve(payload):
	r = requests.get("http://" + IP_ADDRESS + ":5000/retrieve", params=payload)
	array = []
	try:
		r.json()
	except ValueError:
		return str(r.text)

	if type(r.json()) is list:
		array = []
		for item in r.json():
			array.append(raw_parse_dict(item))
		return array
	else:
		return raw_parse_dict(r.json())


def raw_clear_key(payload):
	r = requests.get("http://" + IP_ADDRESS + ":5000/clear_key", params=payload)
	return (str(r.text))

# end raw functions

#q1  q2  q3
#q4  q5  q6
#q7  q8  q9
#q10 q11 q12

neighbors = {}
neighbors['Q1'] = ['Q2', 'Q4']
neighbors['Q2'] = ['Q1', 'Q3', 'Q5']
neighbors['Q3'] = ['Q2', 'Q6']
neighbors['Q4'] = ['Q1', 'Q5', 'Q7']
neighbors['Q5'] = ['Q2', 'Q4', 'Q6', 'Q8']
neighbors['Q6'] = ['Q3', 'Q5', 'Q9']
neighbors['Q7'] = ['Q4', 'Q8', 'Q10']
neighbors['Q8'] = ['Q5', 'Q7', 'Q9', 'Q11']
neighbors['Q9'] = ['Q6', 'Q8', 'Q12']
neighbors['Q10'] = ['Q7', 'Q11']
neighbors['Q11'] = ['Q8', 'Q10', 'Q12']
neighbors['Q12'] = ['Q9', 'Q11']

q1 = 'Q1' # q1 easier to type than 'Q1'
q2 = 'Q2'
q3 = 'Q3'
q4 = 'Q4'
q5 = 'Q5'
q6 = 'Q6'
q7 = 'Q7'
q8 = 'Q8'
q9 = 'Q9'
q10 = 'Q10'
q11 = 'Q11'
q12 = 'Q12'
fire = 'fire'
spill = 'spill'

# wrappers for cis105 functions

def get_items( q ):
	rdict = raw_retrieve({ 'key': q})
	if type(rdict) != str:
		items = rdict['value']
	else:
		return rdict
	return items
	# => array of items
	# => 'Key Q1 is not in data' - have to first create q with store_items

def store_items( q, items ):
	store_string = raw_store({'key': q, 'value': items})
	return store_string
	# will create q if it does not exist

def add_item( q, a_item ):
	append_string = raw_append( {'key': q, 'value': a_item} )
	return append_string

def remove_item( q, a_item ):
	remove_string = raw_remove( {'key': q, 'value': a_item} )
	return remove_string
	# => 'foo successfully removed from Q1'
	# => 'Key Q1 is not in data'

# end wrappers

# factory helpers

def init_factory():
	for q in neighbors:
		store_items(q, [])

def move_item(qa, qb, item):
	if qb not in neighbors[qa]:
		print('non-contig: ' + qa + "|" + qb)
		return False # not contiguous

	print("removing ...")
	remove_string = remove_item( qa, item )
	if 'does not contain' in remove_string:
		print('remove error: ' + remove_string)
		return False # item not in qa

	print("appending ...")
	append_string = add_item( qb, item )
	print( append_string )
	return True

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
