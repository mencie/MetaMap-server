import os
from subprocess import Popen
from flask import Flask, request, redirect, url_for, send_from_directory
from Settings import METAMAP_PATH, METAMAP_VERSION

app = Flask(__name__)

UPLOAD_FOLDER = 'Uploads'
OUTPUT_FOLDER = 'Outputs'

app = Flask(__name__)

# Front page. Gets a file to parse and passes it to the MetaMap program
@app.route('/', methods = ['POST', 'GET'])
def get_input_file():
	if request.method == 'POST':
		orig = request.files['file']
		if orig:
			ensure_dir(UPLOAD_FOLDER)
			ensure_dir(OUTPUT_FOLDER)
			orig.save(os.path.join(UPLOAD_FOLDER, orig.filename))
			fin = os.path.join(UPLOAD_FOLDER, orig.filename)
			fout = os.path.join(OUTPUT_FOLDER, orig.filename)
			
			save_output_values(fin, fout)
			
			return redirect(url_for('display_output', filename=fout))
	return '''
	<!doctype html>
	<title>Parse New File</title>
	<h1>Choose file to parse:</h1>
	<form action="" method=post enctype=multipart/form-data>
		<p><input type=file name=file>
			<input type=submit value=Upload>
	</form>
	'''

# Displays the output from the MetaMap program
@app.route('/<filename>')
def display_output(filename):
	f = open(filename, 'r')
	content = ''
	for line in f:
		content += line + '<br>'
	return '''
	<!doctype html>
	<form action="/" method=get>
		<p><input type=submit value="Choose new file">
	</form>
	<br><br>
	''' + content

# Runs the MetaMap program using the given in- and out-filenames, returning the output in formatted XML
def save_output_values(fin, fout):
	skr = Popen(os.path.join(METAMAP_PATH,'skrmedpostctl_start.bat'))
	mm = Popen([os.path.join(METAMAP_PATH, METAMAP_VERSION), '--XMLf', fin, fout])
	mm.wait()
	skr.terminate()

# Ensures that the specified directory exists. If it does not exist, it is created.
def ensure_dir(d):
	if not os.path.exists(d):
		os.makedirs(d)

if __name__ == '__main__': app.run()