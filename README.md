# Simple Data Storage API
## Data store example using Flask, SQLAlchemy, SQLite, Python

I implemented a data storage API organized by repository.
The user can put/get/delete uploaded obects.

I used Flask, SqlAlchemy along with a lightweight sqlite database.
Objects metadata (name, size, oid, path to the file) are stored in a table called StorageObject and the file is stored directly on the filesystem.

The unicity of the data by collection is insured by hashing the content of the file and checking if the object is already in database or not.

I implemented automatic testing using pytest and requests python modules.

The project is in test mode, there is only one database used for tests. There are no production database for now.

## Development Environment
- Language: Python
- Framework: Flask
- Database: SQLAlchemy, SQLite
- Others: Werkzeug, pytest

## HowTo:
- In the root folder of the project:
```
pip install -r requirements.txt
flask run -p 8282
```

- Run the tests in another terminal:
```
pytest
```
