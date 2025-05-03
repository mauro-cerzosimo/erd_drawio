import os
import xml.etree.ElementTree as ET
import uuid
from collections import defaultdict
from typing import Dict, List, Tuple
import re
from typing import Optional

# Allowed edge types
EDGES = [
    "ERmandOne",
    "ERmany",
    "ERone",
    "ERoneToMany",
    "ERzeroToMany",
    "ERzeroToOne",
]


class CreateDrawio:
    def __init__(self):
        self.output_dir = "output"
        self.input_dir = "input"

    def import_file(self, file_name: str):
        self.path_file_name = os.path.join(self.input_dir, file_name)
        self.tables, self.references, self.positions = self._parse_dsl_file(
            self.path_file_name
        )

    ## Parse DSL FILE
    def _parse_dsl_file(self, path_file_name: str) -> Tuple[
        Dict[str, List[Tuple[str, str]]],
        Dict[str, List[Dict[str, str]]],
        Dict[str, Tuple[Optional[int], Optional[int]]],
    ]:
        tables = defaultdict(list)
        references = defaultdict(list)
        positions = {}

        current_table = None

        with open(path_file_name) as file:
            for line in file:
                line = line.strip()
                line = re.sub(r"\s+", " ", line)
                if not line or line.startswith("#"):
                    continue

                if self._is_reference_line(line):
                    self._parse_reference_line(line, tables, references)
                elif self._is_position_line(line):
                    self._parse_positions(line, positions, tables)
                if self._is_table_line(line):
                    current_table = self._parse_table_line(line)
                    # positions[current_table] = pos
                elif current_table:
                    self._parse_column_line(line, current_table, tables)

        return tables, references, positions

    def _is_table_line(self, line: str) -> bool:
        return line.startswith("TABLE")

    def _is_reference_line(self, line: str) -> bool:
        return line.startswith("REFERENCE")

    def _is_position_line(self, line: str) -> bool:
        return line.startswith("ARRANGE")

    def _parse_table_line(
        self, line: str
    ) -> Tuple[str, Tuple[Optional[int], Optional[int]]]:
        match = re.match(r"^TABLE (\w+)(?:\s*)?", line)
        table_name = match.group(1)
        return table_name

    def _parse_column_line(
        self,
        line: str,
        current_table: str,
        tables: Dict[str, List[Tuple[str, str]]],
    ):
        if m := re.match(r"^(\w+)\s+PK$", line):
            self._add_primary_key(m, current_table, tables)
        elif m := re.match(r"^(\w+)$", line):
            self._add_regular_column(m, current_table, tables)

    def _add_primary_key(self, match, table: str, tables):
        col = match.group(1)
        tables[table].append((col, "PK"))

    def _add_regular_column(self, match, table: str, tables):
        col = match.group(1)
        tables[table].append((col, ""))

    def _parse_reference_line(self, line, tables, references):
        # Compile regex
        reference_re = re.compile(
            r"^REFERENCE (\w+)\.(\w+)\s*->\s*(\w+)\.(\w+)(?:\s*\[(\w+),\s*(\w+)\])?$"
        )
        match = reference_re.match(line)
        if match:
            src_table, src_col, tgt_table, tgt_col, start_arrow, end_arrow = (
                match.groups()
            )
            references[src_table].append(
                {
                    "column_name": src_col,
                    "table_reference": tgt_table,
                    "column_reference": tgt_col,
                    "start_arrow": start_arrow or "",
                    "end_arrow": end_arrow or "",
                }
            )
            self._add_foreign_key(src_table, src_col, tables)
            self._add_foreign_key(tgt_table, tgt_col, tables)
        else:
            print(f"Warning: line could not be parsed → {line}")

    def _add_foreign_key(self, table_name, column_name, tables):
        # Check if OPPORTUNITY_ID exists in reference_list

        has_column = any(col == column_name for col, _ in tables[table_name])

        if has_column:
            # Update OPPORTUNITY_ID in source_list to FK
            updated_list = [
                (col, "FK" if col == column_name and key != "PK" else key)
                for col, key in tables[table_name]
            ]
            tables[table_name] = updated_list

    def _parse_positions(self, line, positions, tables):
        positions_re = re.compile(r"^ARRANGE (\w+)\s*\(\s*(\d+),\s*(\d+)\s*\)$")
        match = positions_re.match(line)
        if match:
            src_table, x, y = match.groups()
            positions[src_table] = (x, y)
        else:
            print(f"Warning: line could not be parsed → {line}")

    # Create XML
    def _create_id(self) -> str:
        """Generates a unique ID."""
        return uuid.uuid4().hex

    def _create_root(self) -> ET.Element:
        """Creates the root mxCell elements."""
        root = ET.Element("root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")
        return root

    def _create_erd_xml(self) -> ET.Element:
        """Generates the ERD XML structure from tables."""
        root = self._create_root()
        x_offset = 0
        for table_name, columns in self.tables.items():
            if table_name in self.positions:
                x, y = self.positions[table_name]
                root, x_offset = self._create_table_xml(root, table_name, columns, x, y)
            else:
                root, width = self._create_table_xml(
                    root, table_name, columns, x_offset
                )
                x_offset += width + 10
        return root

    def _create_table_xml(
        self,
        root: ET.Element,
        table_name: str,
        columns: List[Tuple[str, str]],
        x: int = 0,
        y: int = 100,
        base_width: int = 170,
        height: int = 30,
    ) -> Tuple[ET.Element, int]:
        table_id = table_name
        max_col_len = max(len(name) for name, _ in columns)
        width = max(base_width, 30 + max_col_len * 9, 30 + len(table_name) * 8)

        style_str = self._dict_to_style_string(
            {
                "shape": "table",
                "startSize": "30",
                "container": "1",
                "collapsible": "1",
                "childLayout": "tableLayout",
                "rounded": "1",
                "arcSize": "6",
                "fixedRows": "1",
                "rowLines": "0",
                "fontStyle": "0",
                "align": "center",
                "resizeLast": "1",
                "resizeParent": "1",
                "fillColor": "#F4AC9F",
                "strokeColor": "default",
            }
        )

        table_cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": table_id,
                "value": table_name,
                "style": style_str,
                "vertex": "1",
                "parent": "1",
            },
        )
        ET.SubElement(
            table_cell,
            "mxGeometry",
            {
                "x": str(x),
                "y": str(y),
                "width": str(width),
                "height": str(height * (len(columns) + 1)),
                "as": "geometry",
            },
        )

        self._add_columns(root, table_id, columns, width, height)
        return root, width

    def _add_columns(self, root, table_id, columns, width, height):
        y_offset = 30
        for idx, (col_name, key) in enumerate(columns, start=1):
            row_id = f"{table_id}-{idx}"
            icon_id = f"{table_id}-icon-{idx}"
            col_id = f"{table_id}-col-{idx}"
            fill_color = "#DADADA" if idx % 2 == 0 else "#ffffff"

            self._create_row(
                root, row_id, table_id, fill_color, key, width, height, y_offset
            )
            self._create_icon_cell(root, icon_id, row_id, key, height)
            self._create_column_cell(root, col_id, row_id, col_name, key, width, height)

            y_offset += height

    def _create_row(
        self, root, row_id, parent_id, fill_color, key, width, height, y_offset
    ):
        style_row = self._dict_to_style_string(
            {
                "shape": "tableRow",
                "horizontal": "0",
                "startSize": "0",
                "swimlaneHead": "0",
                "swimlaneBody": "0",
                "fillColor": fill_color,
                "collapsible": "0",
                "dropTarget": "0",
                "portConstraint": "eastwest",
                "strokeColor": "inherit",
                "top": "0",
                "left": "0",
                "right": "0",
                "bottom": "1" if key == "PK" else "0",
            }
        )
        row = ET.SubElement(
            root,
            "mxCell",
            {
                "id": row_id,
                "value": "",
                "style": style_row,
                "vertex": "1",
                "parent": parent_id,
            },
        )
        ET.SubElement(
            row,
            "mxGeometry",
            {
                "y": str(y_offset),
                "width": str(width),
                "height": str(height),
                "as": "geometry",
            },
        )

    def _create_icon_cell(self, root, icon_id, parent_id, key, height):

        style_icon = self._dict_to_style_string(
            {
                "shape": "partialRectangle",
                "overflow": "hidden",
                "connectable": "0",
                "fillColor": "none",
                "strokeColor": "inherit",
                "top": "0",
                "left": "0",
                "bottom": "0",
                "right": "0",
                "fontStyle": "1" if key == "PK" else "",
            }
        )

        ET.SubElement(
            root,
            "mxCell",
            {
                "id": icon_id,
                "value": key,
                "style": style_icon,
                "vertex": "1",
                "parent": parent_id,
            },
        ).append(
            ET.Element(
                "mxGeometry", {"width": "30", "height": str(height), "as": "geometry"}
            )
        )

    def _create_column_cell(
        self, root, col_id, parent_id, col_name, key, width, height
    ):
        style_column = self._dict_to_style_string(
            {
                "shape": "partialRectangle",
                "overflow": "hidden",
                "connectable": "0",
                "fillColor": "none",
                "align": "left",
                "strokeColor": "inherit",
                "top": "0",
                "left": "0",
                "bottom": "0",
                "right": "0",
                "spacingLeft": "6",
                "fontStyle": "5" if key == "PK" else "",
            }
        )

        ET.SubElement(
            root,
            "mxCell",
            {
                "id": col_id,
                "value": col_name,
                "style": style_column,
                "vertex": "1",
                "parent": parent_id,
            },
        ).append(
            ET.Element(
                "mxGeometry",
                {
                    "x": "30",
                    "width": str(width - 30),
                    "height": str(height),
                    "as": "geometry",
                },
            )
        )

    def _dict_to_style_string(self, style_dict: Dict[str, str]) -> str:
        def camel_case(s):
            parts = s.split("_")
            return parts[0] + "".join(p.capitalize() for p in parts[1:])

        return ";".join(f"{camel_case(k)}={v}" for k, v in style_dict.items()) + ";"

    # ADD EDGE
    def _add_edge(
        self,
        root: ET.Element,
        edge_id: str,
        source_id: str,
        target_id: str,
        start_arrow: str,
        end_arrow: str,
    ) -> ET.Element:
        """Adds an edge between two columns."""

        style_edge = self._dict_to_style_string(
            {
                "edgeStyle": "entityRelationEdgeStyle",
                "fontSize": "12",
                "html": "1",
                "endArrow": end_arrow,
                "startArrow": start_arrow,
            }
        )
        if start_arrow and start_arrow not in EDGES:
            raise ValueError(
                f"Invalid start_arrow '{start_arrow}'. Allowed: {EDGES} or blank."
            )
        if end_arrow and end_arrow not in EDGES:
            raise ValueError(f"Invalid end_arrow '{end_arrow}'.")

        edge = ET.SubElement(
            root,
            "mxCell",
            {
                "id": edge_id,
                "value": "",
                "style": style_edge,
                "edge": "1",
                "parent": "1",
                "source": source_id,
                "target": target_id,
            },
        )

        geometry = ET.SubElement(
            edge,
            "mxGeometry",
            {"width": "100", "height": "100", "relative": "1", "as": "geometry"},
        )
        ET.SubElement(geometry, "mxPoint", {"x": "310", "y": "98", "as": "sourcePoint"})
        ET.SubElement(
            geometry, "mxPoint", {"x": "420", "y": "230", "as": "targetPoint"}
        )

        return root

    def _create_row_id(
        self,
        tables: Dict[str, List[Tuple[str, str]]],
        table_name: str,
        column_name: str,
    ) -> str:
        """Generates the row ID for a given column."""
        try:
            idx = [col for col, _ in tables[table_name]].index(column_name) + 1
            return f"{table_name}-{idx}"
        except ValueError as err:
            raise ValueError(
                f"Column '{column_name}' not found in table '{table_name}'."
            ) from err

    def _create_edges(self, root: ET.Element) -> ET.Element:
        """Creates edges between referenced columns."""
        for table, refs in self.references.items():
            for ref in refs:
                source_id = self._create_row_id(self.tables, table, ref["column_name"])
                target_id = self._create_row_id(
                    self.tables, ref["table_reference"], ref["column_reference"]
                )
                edge_id = self._create_id()
                root = self._add_edge(
                    root,
                    edge_id,
                    source_id,
                    target_id,
                    ref["start_arrow"],
                    ref["end_arrow"],
                )
        return root

    # ADD TITLE
    def add_title(self, root: ET.Element, title: str):
        style_title = self._dict_to_style_string(
            {
                "shape": "text",
                "strokeColor": "none",
                "fillColor": "none",
                "html": "1",
                "fontSize": "63",
                "fontStyle": "1",
                "verticalAlign": "middle",
                "align": "left",
            }
        )
        row = ET.SubElement(
            root,
            "mxCell",
            {
                "id": "title",
                "value": title,
                "style": style_title,
                "vertex": "1",
                "parent": "1",
            },
        )
        ET.SubElement(
            row,
            "mxGeometry",
            {
                "x": str(100),
                "y": str(20),
                "width": str(len(title * 25)),
                "height": str(40),
                "as": "geometry",
            },
        )
        return root

    def write_mxgraph(self, file_name: str = "output.drawio") -> None:
        """Writes the XML tree to a file."""
        graph_model = ET.Element(
            "mxGraphModel",
            {
                "dx": "3247",
                "dy": "533",
                "grid": "0",
                "gridSize": "10",
                "guides": "1",
                "tooltips": "1",
                "connect": "1",
                "arrows": "1",
                "fold": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": "850",
                "pageHeight": "1100",
                "math": "0",
                "shadow": "0",
            },
        )
        os.makedirs(self.output_dir, exist_ok=True)
        path_file_name = os.path.join(self.output_dir, file_name)
        root = self._create_erd_xml()
        root = self._create_edges(root)
        # add_title_root = add_title(erd_with_edges, "ERD Star HR Diagram")
        graph_model.append(root)
        ET.ElementTree(graph_model).write(
            path_file_name, encoding="utf-8", xml_declaration=True
        )
