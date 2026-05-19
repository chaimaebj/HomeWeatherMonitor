from flask import Flask
from air_quality_levels import air_quality_bp

app = Flask(__name__)
app.register_blueprint(air_quality_bp)
 
if __name__ == '__main__':
    app.run(debug=True) 