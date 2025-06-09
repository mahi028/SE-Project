from app import create_app
from app.models import db

application = create_app()

if __name__ == "__main__":
    with application.app_context():
        db.create_all()
        
    application.run()