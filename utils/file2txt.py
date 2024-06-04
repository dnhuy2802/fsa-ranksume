from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

def file_docx2text(file_path: str):
    # Read the .docx file from file
    loader = UnstructuredWordDocumentLoader(file_path)
    data = loader.load()
    # get page_content
    text = data[0].page_content
    return text

# def load cv from docx file
def file_pdf2text(file_path: str):
    # Read the .pdf file from the BytesIO object
    loader = UnstructuredPDFLoader(file_path)
    data = loader.load()
    # take page_content from data
    page_content  = data[0].page_content
    return page_content

def file_txt2text(file_path: str):
    with open(file_path, "r") as file:
        text = file.read()
    return text