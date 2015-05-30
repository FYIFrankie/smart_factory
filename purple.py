import os

def speak(phrase):
	espeak_params= ["espeak -a 200 -s 150", "'", phrase, "'", "2> /dev/null"]
	speaking_phrase = ' '.join(espeak_params)
	os.system(speaking_phrase)

def main(group_data, store_data):
        print('purple.py called')
        quadrant = store_data['key'] # the quadrant where items changed
        items = store_data['value']    # items now in the quadrant
	#phrase = (quadrant + ' contains values ' + ', '.join(items)
	#speak(phrase)