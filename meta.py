import os
from subprocess import Popen
from flask import Flask, request, redirect, url_for
from parse import parse_xml
from settings import METAMAP_PATH, METAMAP_VERSION


app = Flask(__name__)

TEMP_UPLOAD = 'tmp_up.txt'
TEMP_XML = 'tmp_xml.txt'
OUTPUT_FOLDER = 'Outputs'
DEFAULT_OUTPUT_FILE = 'tmp_out.txt'

# Front page. Gets either text or a file to parse
@app.route('/', methods=['POST', 'GET'])
def get_input():
	if request.method == 'POST':
		content = request.form['input']
		title = request.form['title']
		upload = request.files['file']
		if content:
			if title: name = title + ".txt"
			else: name = DEFAULT_OUTPUT_FILE
			
			tmp = open(TEMP_UPLOAD, 'w')
			tmp.write(content)
			tmp.close()
		elif upload:
			name = upload.filename
			upload.save(TEMP_UPLOAD)
		else:
			return redirect('/')
		
		ensure_dir(OUTPUT_FOLDER)
		
		to_xml(TEMP_UPLOAD, TEMP_XML)
		parse_xml(TEMP_XML, os.path.join(OUTPUT_FOLDER, name))
		
		return redirect(url_for('display_output', filename=name))
	return '''
	<!doctype html>
	<title>Upload Text</title>
	<h1>Upload content to parse</h1>
	<form action="" method=post enctype=multipart/form-data>
		<br><h3>Upload text:</h3>
			Title:<br><input type=text name=title><br>
			Content:<br>
			<textarea rows=10 cols=100 name=input></textarea><br>
			<input type=submit value=Submit>
		<br><br><br>
		<h3>Upload File:</h3>
			<input type=file name=file>
			<input type=submit value=Upload>
	</form>
	'''

# Displays output from a given text input
@app.route('/<filename>')
def display_output(filename):
	f = open(os.path.join(OUTPUT_FOLDER, filename))
	content = ''
	for line in f:
		content += line.replace(' ', '&nbsp') + '<br>'
	
	return '''
	<!doctype html>
	<form action="/" method=get>
		<p><input type=submit value="Choose new file">
	</form>
	<br><br>
	''' + content

# Runs MetaMap given in- and out-filenames. Returns output in formatted
# XML.
def to_xml(fin, fout):
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
	
	try:
		app.run(debug=True)
	except:
		skr.terminate()
	else:
		skr.terminate()
