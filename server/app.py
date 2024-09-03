from flask import Flask, request, make_response, send_from_directory, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from model import User
from werkzeug.utils import secure_filename
from flask_cors import CORS
import traceback
from config import db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
FRONTEND_URL = os.getenv("FRONTEND_URL")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

migrate = Migrate(app, db)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
db.init_app(app)

def allowed_extensions(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

class Home(Resource):
    def post(self):
        try:
            print("Request form:", request.form)
            print("Request files:", request.files)

            new_user = User(
                name=request.form['name'],
                phone_number=request.form['phone_number'],
                identity=request.form['identity'],
                profile_photo=None
            )

            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and allowed_extensions(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    print(f"Saving file to {filepath}")
                    try:
                        file.save(filepath)
                        new_user.profile_photo = filename
                    except Exception as e:
                        print("Error saving file:", str(e))
                        return make_response(jsonify({'error': str(e)}), 500)

            try:
                db.session.add(new_user)
                db.session.commit()
                return make_response(jsonify({'message': 'User created successfully'}), 201)
            except Exception as e:
                print("Error saving user to database:", str(e))
                db.session.rollback()
                return make_response(jsonify({'error': 'Error saving user to database'}), 500)

        except Exception as e:
            traceback.print_exc()
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 500)
        
api.add_resource(Home, '/home')

class Test(Resource):
    def get(self):
        response = {'message': 'Test endpoint working'}
        return make_response(jsonify(response), 200)
api.add_resource(Test, '/test')

    

if __name__ == '__main__':
    app.run(debug=True)
