import os
import xml.etree.ElementTree as ET
from typing import Dict, Tuple  # ✅ needed for the type hints

EXCLUDE_TABLES = ["table-date", "title"]


class DrawioTableLocator:
    def __init__(self) -> None:
        self.output_dir = "output"

    def read_file(self, file_name: str) -> None:
        """Reads the contents of a file and returns it as a string."""
        file_path_name = os.path.join(self.output_dir, file_name)
        with open(file_path_name, "r", encoding="utf-8") as f:
            xml_content = f.read()
            self.positions = self._extract_table_positions(xml_content)  # 🚨 typo here

    def _extract_table_positions(self, xml_content: str) -> Dict[str, Tuple[int, int]]:
        """Parses Drawio XML content and extracts table names with x, y positions."""
        root = ET.fromstring(xml_content)
        positions = {}

        for cell in root.iter("mxCell"):
            value = cell.attrib.get("value")
            id = cell.attrib.get("id")
            geometry = cell.find("mxGeometry")
            if value and geometry is not None:
                x = geometry.attrib.get("x")
                y = geometry.attrib.get("y")
                if (x is not None) and (y is not None) and id not in EXCLUDE_TABLES:
                    positions[value] = (int(x), int(y))
        return positions

    def print_positions(self) -> None:
        # Print results
        for table, (x, y) in self.positions.items():
            print(f"ARRANGE {table} ({x}, {y})")
