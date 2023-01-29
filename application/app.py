from flask import Flask, render_template

# Global Variables


# Create Flask App
app = Flask(__name__)


# App routes
@app.route("/", methods=["GET"], endpoint="home")
def home_page():
    return render_template("/home.html")


