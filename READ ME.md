.venv\Scripts\Activate.ps1

## Install database and create admin user ##
In terminal enter the following: 
Flask shell
>>> from app.extensions import db, bcrypt
>>> from app.models.models import User, reserve
>>> db.create_all()
>>> admin=User(username='admin', registration = 'ADMIN', password=bcrypt.generate_password_hash('password'), role='admin', authorised= 'Y')
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()

stop special chars
oninput="this.value=this.value.replace(/[^a-zA-Z0-9]/g, '')"

time out ref 
https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask

loggin
https://betterstack.com/community/guides/logging/how-to-start-logging-with-flask/