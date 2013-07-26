import os
import traceback
from subprocess import Popen
from flask import Flask, request, redirect, url_for
from parse import parse_xml
from settings import METAMAP_PATH, METAMAP_VERSION

'''
WORDS WHICH METAMAP DOES NOT PLAY NICELY WITH:
	pheochromocytomy
	enterography
	lyphoma
	lymphona
	lymphopiothopy
	saity
'''

app = Flask(__name__)

TEMP_UPLOAD = 'tmp_up.txt'
TEMP_XML = 'tmp_xml.txt'
DEFAULT_OUTPUT_FOLDER = 'Outputs'
DEFAULT_OUTPUT_FILE = 'tmp_out.txt'

# Front page. Gets either text or a file to parse
@app.route('/', methods=['POST', 'GET'])
def get_input():
	if request.method == 'POST':
		content = request.form['input']
		
		use_wsd = 'wsd' in request.form
		
		if content.strip():
			content += '\n'
			
			with open(TEMP_UPLOAD, 'w') as f:
				f.write(content)
		else:
			return redirect('/')
		
		to_xml(TEMP_UPLOAD, TEMP_XML, use_wsd)
		
		return parse_xml(TEMP_XML)
	
	return '''
	<!doctype html>
	<title>Upload Text</title>
	<h1>Upload content to parse</h1>
	<form action="" method=post enctype=application/x-www-form-urlencoded>
		<br><h3>Upload text:</h3>
			<textarea rows=10 cols=100 name=input></textarea><br>
			<input type=checkbox name=wsd value=true>Use word-sense
				disambiguation<br><br>
			<input type=submit value=Submit>
	</form>
	'''

# Runs MetaMap given in- and out-filenames and the WSD option.
def to_xml(fin, fout, use_wsd):
	# Wipe the XML file
	with open(fout, 'w') as f:
		f.write('')
	
	if use_wsd:
		mm = Popen([os.path.join(METAMAP_PATH, METAMAP_VERSION),
			'--XMLf -y', fin, fout])
	else:
		mm = Popen([os.path.join(METAMAP_PATH, METAMAP_VERSION),
			'--XMLf', fin, fout])
	mm.wait()

# Ensures that the specified directory exists. If it does not exist,
# it is created.
def ensure_dir(d):
	if not os.path.exists(d):
		os.makedirs(d)

# Setup and teardown for the server
if __name__ == '__main__':
	skr = Popen(os.path.join(METAMAP_PATH, 'skrmedpostctl_start.bat'))
	wsd = Popen(os.path.join(METAMAP_PATH, 'wsdserverctl_start.bat'))
	
	try:
		app.run(debug=True)
	except:
		skr.terminate()
		wsd.terminate()
		traceback.print_exc()
	else:
		skr.terminate()
		wsd.terminate()
