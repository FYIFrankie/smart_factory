import os


def speak(phrase):
	espeak_params= ["espeak -a 200 -s 150", "'", phrase, "'", "2> /dev/null"]
	speaking_phrase = ' '.join(espeak_params)
	os.system(speaking_phrase)


def main(group_data, store_data):
	phrase = (store_data['key']) + ' contains values ' + ', '.join(store_data['value'])
	speak(phrase)