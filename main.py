from flask import Flask, render_template

# Initialize the Flask app
app = Flask(__name__)

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('de4uth.html')

# For Vercel, the app must be served via `app`
if __name__ == '__main__':
    app.run(debug=True)
