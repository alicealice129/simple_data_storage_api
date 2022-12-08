import os
import hashlib
from werkzeug.utils import secure_filename
from flask import Flask, render_template, make_response, jsonify, request, send_file
from .models import StorageObject, db

app = Flask(__name__)

#Assigning a sqlite database to ORM
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datastorage.db'
#Data storage root path
app.config['UPLOAD_FOLDER'] = 'upload'
db.init_app(app)

#creating the database model
with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():  # put application's code here
    # return 'Hello World!'
    return render_template('index.html')

#Route for adding object to the data storage
# The request needs to be a multipart/form-data with file data attached
# returns oid and size of the stored object
@app.route('/data/<repository>', methods=['PUT'])
def upload_object(repository):
    #checking request consistency
    if 'file' not in request.files:
        return make_response('bad request', 400)

    file = request.files['file']
    if file.filename == '':
        return make_response('No selected file', 601)

    #hashing the file content to create a unique object id (with very low collision rate)
    oid = hashlib.sha3_256(file.read()).hexdigest()

    #creating the repository if it does not exist
    secure_repo = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(repository))
  
    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    
    if not os.path.isdir(secure_repo):
        os.mkdir(secure_repo)
    
    #de-duplicate: checking if a file with the same oid exists in the repository
    if len(StorageObject.query.filter_by(repository=repository, oid=oid).all())>0:
        return make_response('File content already exists', 603)
    
    #getting back to the start of the file stream after read()
    file.seek(0)
    
    #saving file in filesystem
    rel_path = os.path.join(secure_repo, secure_filename(file.filename))
    if os.path.isfile(rel_path):
        return make_response('Filename already exists', 602)
    file.save(rel_path)
    
    #getting file size on filesystem
    size=os.stat(rel_path).st_size

    #writing the object metadata in the database
    try:
        storage_object = StorageObject(oid=oid,size=size,repository=repository, name=file.filename)
        db.session.add(storage_object)
        db.session.commit()
    except:
        return make_response('Database error', 601)

    #formatting response output
    resp = jsonify({
            "oid": storage_object.oid,
            "size": storage_object.size
    })
    
    return make_response(resp, 201)

#Route to get a stored object with his repository and oid
# returns the file data as Bytes
@app.route('/data/<repository>/<object_id>', methods=['GET'])
def download_object(repository, object_id):
    #getting the object metadata from the database
    try:
        resp = StorageObject.query.filter_by(repository=repository, oid=object_id).all()
    except:
        return make_response('Database error', 601)

    if len(resp) < 1:
        return make_response('Object not found', 404)
    
    #getting the object from the filesystem
    filename = os.path.join(app.config['UPLOAD_FOLDER'], resp[0].repository, resp[0].name)
    
    if not os.path.isfile(filename):
        return make_response('File not found', 404)

    return make_response(send_file(filename), 200)

#Route to delete an object from the data storage by providing its location (repository) and oid
# returns Ok if successful
@app.route('/data/<repository>/<object_id>', methods=['DELETE'])
def delete_object(repository, object_id):
    #deleting object in database
    try:
        objs = StorageObject.query.filter_by(repository=repository, oid=object_id).all()
    except:
        return make_response('Database error', 602)

    if len(objs) < 1:
        return make_response('Not found', 404)
    
    filename = os.path.join(app.config['UPLOAD_FOLDER'], objs[0].repository, objs[0].name) #getting filename to erase later
    
    try:
        StorageObject.query.filter_by(repository=repository, oid=object_id).delete()
        db.session.commit()
    except:
        return make_response('Database error', 602)

    #If database object deletion is successful, remove the file in the repository
    try:
        if len(StorageObject.query.filter_by(repository=repository, oid=object_id).all()) < 1:
            if os.path.isfile(filename):
                os.remove(filename)
            return make_response('OK', 200)
        else:
            return make_response('Error while deleting object', 601)
    except:
        return make_response('Error while deleting object', 601)

if __name__ == '__main__':
    app.run(port=8282)
