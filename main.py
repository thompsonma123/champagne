from flask import Flask, render_template, request, redirect, url_for
from flaskext.markdown import Markdown
import pickle
from os import path as os_path, mkdir as os_mkdir, remove as os_remove
from datetime import datetime
import sys, getopt

app = Flask("Notebook")
Markdown(app)

noteList = []

noteDir = "notes"

# create note directory if it doesn't exist
if not os_path.exists(noteDir):
		os_mkdir(noteDir)

noteListFileName = os_path.join(noteDir, "notes.pkl")

# check for existing file with note metadata
if os_path.exists(noteListFileName):
	with open(noteListFileName, 'rb') as notesFile:
		noteList = pickle.load(notesFile)


@app.route("/")
def home():
	return render_template("home.html", notes=noteList)

@app.route("/addNote")
def addNote():
	return render_template("noteForm.html", headerLabel="New Note", submitAction="createNote", cancelUrl=url_for('home'))

@app.route("/createNote", methods=["post"])
def createNote():
	# get next note id
	if len(noteList):
		idList = [ int(i['id']) for i in noteList ]
		noteId = str(max(idList)+1)
	else:
		noteId = "1"

	noteFileName = os_path.join(noteDir, noteId+".pkl")
	
	lastModifiedDate = datetime.now()
	lastModifiedDate = lastModifiedDate.strftime("%d-%b-%Y %H:%M:%S")
	
	noteTitle = request.form['noteTitle']
	noteMessage = request.form['noteMessage']
	
	note = {'id': noteId, 'title': noteTitle, 'lastModifiedDate': lastModifiedDate, 'message': noteMessage}

	# save the note
	with open(noteFileName, 'wb') as noteFile:
		pickle.dump(note, noteFile)

	# add metadata to list of notes for display on home page
	noteList.append({'id': noteId, 'title': noteTitle, 'lastModifiedDate': lastModifiedDate})
	
	# save changes to the file containing the list of note metadata
	with open(noteListFileName, 'wb') as notesFile:
		pickle.dump(noteList, notesFile)
		
	return redirect(url_for('viewNote', noteId=noteId))

@app.route("/viewNote/<noteId>")
def viewNote(noteId):
	noteFileName = os_path.join(noteDir, noteId+".pkl")
	with open(noteFileName, 'rb') as noteFile:
		note = pickle.load(noteFile)
	
	return render_template("viewNote.html", note=note, submitAction="/saveNote")

@app.route("/editNote/<noteId>")
def editNote(noteId):
	noteFileName = os_path.join(noteDir, noteId+".pkl")
	with open(noteFileName, 'rb') as noteFile:
		note = pickle.load(noteFile)
	
	cancelUrl = url_for('viewNote', noteId=noteId)
	return render_template("noteForm.html", headerLabel="Edit Note", note=note, submitAction="/saveNote", cancelUrl=cancelUrl)

@app.route("/saveNote", methods=["post"])
def saveNote():
	lastModifiedDate = datetime.now()
	lastModifiedDate = lastModifiedDate.strftime("%d-%b-%Y %H:%M:%S")
	
	noteId = request.form['noteId']
	noteTitle = request.form['noteTitle']
	noteMessage = request.form['noteMessage']
	
	noteFileName = os_path.join(noteDir, noteId+".pkl")
	
	note = {'id': noteId, 'title': noteTitle, 'lastModifiedDate': lastModifiedDate, 'message': noteMessage}

	# save the note
	with open(noteFileName, 'wb') as noteFile:
		pickle.dump(note, noteFile)

	# remove the old version of the note from the list of note metadata and add the new version
	global noteList
	newNoteList = [ i for i in noteList if not (i['id'] == noteId) ]
	noteList = newNoteList

	# add metadata to list of notes for display on home page
	noteList.append({'id': noteId, 'title': noteTitle, 'lastModifiedDate': lastModifiedDate})
	
	# save changes to the file containing the list of note metadata
	with open(noteListFileName, 'wb') as notesFile:
		pickle.dump(noteList, notesFile)

	return redirect(url_for('viewNote', noteId=noteId))

@app.route("/deleteNote/<noteId>")
def deleteNote(noteId):
	# delete the note file
	noteFileName = os_path.join(noteDir, noteId+".pkl")
	os_remove(noteFileName)
	
	# remove the note from the list of note metadata
	global noteList
	newNoteList = [ i for i in noteList if not (i['id'] == noteId) ]
	noteList = newNoteList
	
	# save changes to the file containing the list of note metadata
	with open(noteListFileName, 'wb') as notesFile:
		pickle.dump(noteList, notesFile)

	return redirect("/")

if __name__ == "__main__":
	debug = False
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["debug"])
	except getopt.GetoptError:
		print('usage: main.py [--debug]')
		sys.exit(2)
	
	for opt, arg in opts:
		if opt == '-h':
			print('usage: main.py [--debug]')
			sys.exit()
		elif opt == "--debug":
			debug = True

	app.run(host="0.0.0.0", port="5000", debug=debug)