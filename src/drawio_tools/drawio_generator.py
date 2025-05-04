import os
import xml.etree.ElementTree as ET
import uuid
from collections import defaultdict
from typing import Dict, List, Tuple
import re
from typing import Optional
import logging
from datetime import date
from src.drawio_tools.styles import (
    TABLE_DATE_COL_STYLE,
    TABLE_DATE_ROW_STYLE,
    TABLE_DATE_STYLE,
    TABLE_STYLE,
    TITLE_STYLE,
    ICON_CELL_STYLE,
    COLUMN_CEL_STYLE,
    EDGE_STYLE,
    ROW_STYLE,
)

logger = logging.getLogger(__name__)

# Allowed edge types
EDGES = [
    "ERmandOne",
    "ERmany",
    "ERone",
    "ERoneToMany",
    "ERzeroToMany",
    "ERzeroToOne",
]


class DrawioGenerator:
    def __init__(self):
        self.output_dir = "output"
        self.input_dir = "input"

    def import_file(self, file_name: str):
        self.path_file_name = os.path.join(self.input_dir, file_name)
        (
            self.tables,
            self.references,
            self.positions,
            self.title,
            self.created_at_string,
        ) = self._parse_dsl_file(self.path_file_name)

    ## Parse DSL FILE
    def _parse_dsl_file(self, path_file_name: str) -> Tuple[
        Dict[str, List[Tuple[str, str]]],
        Dict[str, List[Dict[str, str]]],
        Dict[str, Tuple[Optional[int], Optional[int]]],
    ]:
        tables = defaultdict(list)
        references = defaultdict(list)
        positions = {}
        title = None
        created_at = None

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
                elif self._is_title_line(line):
                    title = self._parse_title(line)
                elif self._is_create_date(line):
                    created_at = self._parse_create_date(line)
                elif self._is_table_line(line):
                    current_table = self._parse_table_line(line)
                elif current_table:
                    self._parse_column_line(line, current_table, tables)
        # Remove keys with empty lists
        keys_to_remove = [key for key, value in tables.items() if not value]
        for key in keys_to_remove:
            del tables[key]
            logger.warning(f"Removed Table {keys_to_remove} because without columns")
        return tables, references, positions, title, created_at

    def _is_title_line(self, line):
        return line.startswith("TITLE")

    def _is_create_date(self, line):
        return line.startswith("CREATEDAT")

    def _is_table_line(self, line: str) -> bool:
        return line.startswith("TABLE")

    def _is_reference_line(self, line: str) -> bool:
        return line.startswith("REFERENCE")

    def _is_position_line(self, line: str) -> bool:
        return line.startswith("ARRANGE")

    def _parse_title(self, line):
        match = re.match(r"TITLE\s+(.*)", line)
        if match:
            title_name = match.group(1).strip()
            return title_name
        else:
            logger.warning("No TITLE found in line")
            return None

    def _parse_create_date(self, line):
        match = re.match(r"CREATEDAT\s+(.*)", line)
        if match:
            created_at = match.group(1).strip()
            return created_at
        else:
            logger.warning("No CREATEDAT found in line")
            return None

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
        if m := re.match(r"^\*\s*(\w+)", line):
            self._add_primary_key(m, current_table, tables)
        elif m := re.match(r"^\+\s*(\w+)", line):
            self._add_foreign_key(m, current_table, tables)
        elif m := re.match(r"^(\w+)$", line):
            self._add_regular_column(m, current_table, tables)

    def _add_primary_key(self, match, table: str, tables):
        col = match.group(1)
        tables[table].append((col, "PK"))

    def _add_foreign_key(self, match, table: str, tables):
        col = match.group(1)
        tables[table].append((col, "FK"))

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
            self._add_reference_foreign_key(src_table, src_col, tables)
            self._add_reference_foreign_key(tgt_table, tgt_col, tables)
        else:
            logger.warning(f"line could not be parsed → {line}")

    def _add_reference_foreign_key(self, table_name, column_name, tables):
        # Check if OPPORTUNITY_ID exists in reference_list

        has_column = any(col == column_name for col, _ in tables[table_name])

        if has_column:
            # Update OPPORTUNITY_ID in source_list to FK
            updated_list = [
                (col, "FK" if col == column_name and key != "PK" else key)
                for col, key in tables[table_name]
            ]
            tables[table_name] = updated_list
        else:
            raise ValueError(
                f"Column '{column_name}' not found in table '{table_name} or {table_name} doesn't exist'."
            )


    def _parse_positions(self, line, positions, tables):
        positions_re = re.compile(r"^ARRANGE (\w+)\s*\(\s*(\d+),\s*(\d+)\s*\)$")
        match = positions_re.match(line)
        if match:
            src_table, x, y = match.groups()
            positions[src_table] = (x, y)
        else:
            logger.warning(f"Warning: line could not be parsed → {line}")

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

    def _create_mxcell(self, root, id, value, style, parent, vertex, geom_attrs):
        """Helper to create mxCell with geometry."""
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": id,
                "value": value,
                "style": style,
                "vertex": vertex,
                "parent": parent,
            },
        )
        ET.SubElement(cell, "mxGeometry", geom_attrs)

    def _create_erd_xml(self) -> ET.Element:
        """Generates the ERD XML structure from tables."""
        root = self._create_root()
        x_offset = 1
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

        self._create_mxcell(
            root,
            id=table_id,
            value=table_name,
            style=self._dict_to_style_string(TABLE_STYLE),
            parent=str(1),
            vertex=str(1),
            geom_attrs={
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
        row_style = ROW_STYLE.copy()

        row_style.update(
            {
                "fillColor": fill_color,
                "bottom": "1" if key == "PK" else "0",
            }
        )

        self._create_mxcell(
            root,
            id=row_id,
            value="",
            style=self._dict_to_style_string(row_style),
            parent=parent_id,
            vertex=str(1),
            geom_attrs={
                "y": str(y_offset),
                "width": str(width),
                "height": str(height),
                "as": "geometry",
            },
        )

    def _create_icon_cell(self, root, icon_id, parent_id, key, height):

        icon_cell_style = ICON_CELL_STYLE.copy()
        icon_cell_style["fontStyle"] = "1" if key == "PK" else ""

        self._create_mxcell(
            root,
            id=icon_id,
            value=key,
            style=self._dict_to_style_string(icon_cell_style),
            parent=parent_id,
            vertex=str(1),
            geom_attrs={"width": "30", "height": str(height), "as": "geometry"},
        )

    def _create_column_cell(
        self, root, col_id, parent_id, col_name, key, width, height
    ):
        column_cell_style = COLUMN_CEL_STYLE.copy()
        column_cell_style["fontStyle"] = "5" if key == "PK" else ""

        self._create_mxcell(
            root,
            id=col_id,
            value=col_name,
            style=self._dict_to_style_string(column_cell_style),
            parent=parent_id,
            vertex=str(1),
            geom_attrs={
                "x": "30",
                "width": str(width - 30),
                "height": str(height),
                "as": "geometry",
            },
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

        edge_style = EDGE_STYLE.copy()
        edge_style["endArrow"] = end_arrow
        edge_style["startArrow"] = start_arrow

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
                "style": self._dict_to_style_string(edge_style),
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
                f"Column '{column_name}' not found in table '{table_name} or {table_name} doesn't exist'."
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

    def _add_title(self, root: ET.Element):

        self._create_mxcell(
            root,
            id="title",
            value=self.title,
            style=self._dict_to_style_string(TITLE_STYLE),
            parent="1",
            vertex="1",
            geom_attrs={
                "x": "186",
                "y": "10",
                "width": "125",
                "height": "40",
                "as": "geometry",
            },
        )
        return root

    # ADD Date
    def _add_date(self, root):
        self._create_mxcell(
            root,
            id="table-date",
            value="",
            style=self._dict_to_style_string(TABLE_DATE_STYLE),
            parent="1",
            vertex="1",
            geom_attrs={
                "x": "1",
                "y": "6",
                "width": "175.75",
                "height": "48",
                "as": "geometry",
            },
        )

        for r in range(2):
            self._create_mxcell(
                root,
                id=f"table-date-{r}",
                value="",
                style=self._dict_to_style_string(TABLE_DATE_ROW_STYLE),
                parent="table-date",
                vertex="1",
                geom_attrs={
                    "width": "175.75",
                    "height": "24",
                    "as": "geometry",
                    **({"y": "24"} if r == 1 else {}),
                },
            )

            for c in range(2):
                if c == 0:
                    geo = {"width": "82"}
                    align = "right"
                else:
                    geo = {"x": "82", "width": "94"}
                    align = "left"
                if r == 0 and c == 0:
                    cell_value = "CreatedAt:"
                elif r == 0 and c == 1:
                    cell_value = self.created_at_string
                elif r == 1 and c == 0:
                    cell_value = "UpdatedAt:"
                elif r == 1 and c == 1:
                    cell_value = date.today().isoformat()

                self._create_mxcell(
                    root,
                    id=f"table-date-{r}-{c}",
                    value=cell_value,
                    style=self._dict_to_style_string(
                        {**TABLE_DATE_COL_STYLE, "align": align}
                    ),
                    parent=f"table-date-{r}",
                    vertex="1",
                    geom_attrs={"height": "24", "as": "geometry", **geo},
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
        if self.title:
            root = self._add_title(root)
        if self.created_at_string:
            root = self._add_date(root)
        graph_model.append(root)
        ET.ElementTree(graph_model).write(
            path_file_name, encoding="utf-8", xml_declaration=True
        )
