.venv\Scripts\Activate.ps1

## Install database and create admin user ##
In terminal enter the following: 
Flask shell
>>> from app.extensions import db, bcrypt
>>> from app.models.models import User, reserve
>>> db.create_all()
>>> admin=User(username='admin1', registration = 'AD70MIN', password=bcrypt.generate_password_hash('Assignment1/'), role='admin', authorised= 'Y')
>>>admin=User(username='admin', registration = 'AD70MIN', password=bcrypt.generate_password_hash('Assignment1/').decode('utf-8'), role='admin', authorised= 'Y')
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()

stop special chars
oninput="this.value=this.value.replace(/[^a-zA-Z0-9]/g, '')"

time out ref 
https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask

loggin
https://betterstack.com/community/guides/logging/how-to-start-logging-with-flask/

deploy 
https://levelup.gitconnected.com/deploy-a-production-ready-python-web-app-on-render-for-free-from-start-to-finish-in-3-steps-952e4b7e26a4

deploy workflow 
https://www.youtube.com/watch?v=DBlmF91Accg&t=201s
https://github.com/marketplace/actions/render-deploy-action

postsql 
https://www.google.com/search?sca_esv=6459c9e3b5d5a0f2&rlz=1C1ONGR_en-GBGB982GB982&q=how+to+set+up+a+sqlite+database+on+render&tbm=vid&source=lnms&sa=X&ved=2ahUKEwia_rPCvNGEAxVZVEEAHXQjAlgQ0pQJegQIDBAB&biw=1536&bih=695&dpr=1.25#fpstate=ive&vld=cid:ce1f96ab,vid:IBfj_0Zf2Mo,st:0

utf8
https://stackoverflow.com/questions/34548846/flask-bcrypt-valueerror-invalid-salt#:~:text=The%20bcrypt%20package%20(which%20Flask,return%20the%20Invalid%20salt%20error.

https://flask-bcrypt.readthedocs.io/en/latest/
