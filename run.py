import os
from src.create_drawio.drawio_generator import CreateDrawio
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    path_file_name = os.environ.get("INPUT_FILE_NAME_PATH")
    output_file_name = os.environ.get("OUTPUT_FILE_NAME")
    create_drawio = CreateDrawio()
    create_drawio.import_file(path_file_name)
    create_drawio.write_mxgraph(output_file_name)
