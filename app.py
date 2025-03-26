from flask import Flask, render_template
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to Flask!'

if __name__ == '__main__':
    app.run(debug=True) 