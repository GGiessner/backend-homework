import json
import requests
from flask import Flask
from flask import request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import eventlet

eventlet.monkey_patch()


# Usual flask initialization
app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


# Database declaration
db_name = 'notes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name      
db = SQLAlchemy(app)   

@app.route('/')
def fct():
    return "mon serveur fonctionne"


# Define a table in the database
class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    done = db.Column(db.Boolean, default=False)

with app.app_context():     # create the database 
    db.create_all()


@app.route('/api/notes', methods=['POST'])
def create_note():
    try:
        params  = json.loads(request.data)
        title   = params['title']
        content = params['content']
        done    = params.get('done')
        to_bool = lambda x: str(x).lower() in ['true', '1', 'yes', 'on']

        note = Note(
            title   = title,
            content = content,
            done    = to_bool(done) if done is not None else False
        )
        db.session.add(note)
        db.session.commit()
        return {'id': note.id, 'title': note.title, 'content': note.content, 'done': note.done}
    except Exception as exc:
        return {'error': f'{type(exc).__name__}: {exc}'}, 42
    

@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return [dict(id=note.id, title=note.title, content=note.content, done=note.done) for note in notes]


@app.route('/api/notes/<int:note_id>/done', methods=['PATCH'])
def MAJutil(note_id):
    note = Note.query.get_or_404(note_id)
    note.done = not note.done
    db.session.commit()

    # Diffusion en temps réel à tous les navigateurs
    socketio.emit('note_updated', {'id': note.id, 'done': note.done}, broadcast=True)
    return {'id': note.id, 'done': note.done}


# Frontend
@app.route('/front/notes')
def front_users():
    url = request.url_root + '/api/notes'
    request = requests.get(url)
    if not (200 <= request.status_code < 300):
        return dict(error=f"could not request notes list", url=url,
                    status=request.status_code, text=request.text)
    notes = request.json()
    return render_template('notes.html.j2', notes=notes)


#lancement:

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)