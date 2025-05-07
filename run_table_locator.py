import os
import logging
from dotenv import load_dotenv
from drawio_tools.drawio_table_locator import DrawioTableLocator

load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":

    drawio_file = os.environ.get("OUTPUT_FILE_NAME")

    if not drawio_file:
        logging.error("Environment variable OUTPUT_FILE_NAME is not set.")
        exit(1)

    logging.info(f"Starting DrawioTableLocator with file: {drawio_file}")
    locator = DrawioTableLocator()

    try:
        # Read the file
        locator.read_file(drawio_file)
        logging.info(f"Successfully read file: {drawio_file}")

        # Print results
        logging.info("Start printing table positions.")
        locator.print_positions()

    except Exception as e:
        logging.exception(f"An error occurred while processing the file: {e}")
