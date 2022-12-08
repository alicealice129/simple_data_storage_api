from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Datamodel for object storage, repository and filname will be used to retrive data on filesystem
# could also replace filesystem by a blob column
class StorageObject(db.Model):
    __tablename__ = 'StorageObject'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    oid = db.Column(
        db.String(255),
        nullable=False
    )
    size = db.Column(
        db.Integer
    )
    repository = db.Column(
        db.String(255),
        nullable=False
    )
    name = db.Column(
        db.String(255),
        nullable=False
    )
    
    def __init__(self, oid, size, repository, name):
        self.oid = oid
        self.size = size
        self.repository = repository
        self.name = name