import os

from dotenv import load_dotenv
from flask import Blueprint, Response, jsonify, render_template, request
from flask_cors import CORS, cross_origin

from ..utils.chatbot import LLMAgent
from ..utils.textract import DocParser

load_dotenv()

file_upload_path = os.environ.get("DOC_UPLOAD_PATH")
xml_output_path = os.environ.get("XML_OUTPUT_PATH")
image_output_path = os.environ.get("IMAGE_OUTPUT_PATH")

document_parser = Blueprint("document-parser", __name__, template_folder="templates")
CORS(document_parser)


@document_parser.route("/extract", methods=["POST"])
def extract():
    if "documents" not in request.files:
        return jsonify({"error": "No file part"}), 400

    doc_parser = DocParser()
    llm_agent = LLMAgent()

    documents = request.files.getlist("documents")

    xml_text_data = []

    print("Saving Documents...")
    for doc in documents:
        print(doc.filename)
        print(file_upload_path)
        path = os.path.join(file_upload_path, doc.filename)
        with open(path, "wb") as file:
            file.write(doc.read())

        print("PATH", path)
        parsed_data = doc_parser.extract_content(path=path)

        for data in parsed_data:
            chatbot_response = llm_agent.query(query=data["content"])
            xml_data = chatbot_response.replace("```xml", "").replace("```", "").strip()
            name = data["file_name"] + ".xml"

            xml_file_path = os.path.join(xml_output_path, name)

            with open(xml_file_path, "w", encoding="utf-8") as file:
                print(
                    f'Chatbot response done. Creating the XML file: {data["file_name"]}'
                )

                xml_text_data.append(xml_data)
                file.write(xml_data)

    return Response(xml_text_data, mimetype="application/xml")
