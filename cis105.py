try:
	import requests
except ImportError:
	print("Whoops, you don't have the requests library installed!")

IP_ADDRESS = 'localhost'

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