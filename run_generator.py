import os
import logging
from dotenv import load_dotenv
from drawio_tools.drawio_generator import DrawioGenerator

load_dotenv()
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    logging.info("Loading environment variables...")

    file_name = os.environ.get("INPUT_FILE_NAME_PATH")
    output_file_name = os.environ.get("OUTPUT_FILE_NAME")

    if not file_name or not output_file_name:
        logging.error(
            "Environment variables INPUT_FILE_NAME_PATH "
            "or OUTPUT_FILE_NAME are missing."
        )
        exit(1)

    path_file_name = os.path.join("input", file_name)
    logging.info("Starting drawio generation...")
    logging.info("Input DSL file: ./input/%s", path_file_name)
    logging.info("Output Drawio file: ./output/%s", output_file_name)

    try:
        create_drawio = DrawioGenerator()
        create_drawio.import_file(path_file_name)
        create_drawio.write_mxgraph(output_file_name)
        logging.info("Successfully generated: ./output/%s", output_file_name)
    except Exception as e:
        logging.exception("An error occurred during Drawio generation: %s", e)
        exit(1)
