from flask import Flask

from src.document_parser.document_parser import document_parser

app = Flask(__name__)
app.register_blueprint(document_parser, url_prefix="/document-parser")


@app.route("/")
def initial_page():
    return "<div>Hi There</div>"


if __name__ == "__main__":
    app.run(debug=True)
