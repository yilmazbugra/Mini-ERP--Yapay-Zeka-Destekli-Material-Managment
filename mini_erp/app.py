from app import create_app, db
from app.models import *

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'app': app}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)
