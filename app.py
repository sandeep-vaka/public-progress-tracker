from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from routes.authRoutes import auth_bp
from routes.trackerRoutes import tracker_bp

load_dotenv()

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(tracker_bp)

@app.route('/')
def index():
    return jsonify({"message": "Public Progress Tracker API Running"})

@app.route('/public')
def public():
    return render_template('public.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)