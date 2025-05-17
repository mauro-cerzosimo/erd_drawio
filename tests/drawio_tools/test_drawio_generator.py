import pytest
from drawio_tools.drawio_generator import DrawioGenerator, EDGES
from typing import List, Tuple, Dict

import xml.etree.ElementTree as ET
import pathlib

from unittest.mock import patch
from datetime import date


DSL_CONTENT = """
TITLE TEST ERD
CREATEDAT 2024-01-01
TABLE TEST_TABLE {
    COLUMN1 *
    COLUMN2 +
}

TABLE TEST_TABLE2 {
    COLUMN4 *
    COLUMN5
}

TABLE TEST_TABLE3 {
    COLUMN6 *
    COLUMN7
}

REFERENCE TEST_TABLE.COLUMN1 -> TEST_TABLE2.COLUMN5 [ERmany, ERone]
REFERENCE TEST_TABLE.COLUMN2 -> TEST_TABLE3.COLUMN6 [ERmany, ERone]
REFERENCE TEST_TABLE3.COLUMN6 -> TEST_TABLE.COLUMN2

ARRANGE TEST_TABLE (10, 10)
"""


@pytest.fixture
def mock_generator(tmp_path: pathlib.Path) -> DrawioGenerator:
    # Arrange
    dsl_file_path = write_dsl_file(tmp_path, DSL_CONTENT)
    generator = DrawioGenerator()

    # Act
    generator.import_file(dsl_file_path)
    return generator


def test() -> None:
    assert 2 == 2


def write_dsl_file(tmp_path: pathlib.Path, content: str) -> str:
    """Helper to write the DSL file and return its path."""
    dsl_file = tmp_path / "test.dsl"
    dsl_file.write_text(content)
    return str(dsl_file)


def check_generator_attributes(mock_generator: DrawioGenerator) -> None:
    """Ensure generator has all required attributes."""
    for attr in ["tables", "references", "positions", "title", "created_at_string"]:
        assert hasattr(mock_generator, attr), f"Missing attribute: {attr}"


def check_tables_type(mock_generator: DrawioGenerator) -> None:
    """Ensure tables have the correct type: Dict[str, List[Tuple[str, str]]]"""
    assert isinstance(mock_generator.tables, dict), "tables should be a dict"
    for key, value in mock_generator.tables.items():
        assert isinstance(key, str), f"Key '{key}' should be a string"
        assert isinstance(value, list), f"Value for '{key}' should be a list"
        for item in value:
            assert isinstance(item, tuple), f"Item {item} should be a tuple"
            assert len(item) == 2, f"Tuple {item} should have 2 elements"
            assert all(
                isinstance(x, str) for x in item
            ), f"Tuple {item} elements should be strings"


def check_reference_type(mock_generator: DrawioGenerator) -> None:
    """Ensure tables have the correct type: Dict[str, List[Dict[str, str]]]"""
    assert isinstance(mock_generator.references, dict), "references should be a dict"
    for key, value in mock_generator.references.items():
        assert isinstance(key, str), f"Key '{key}' should be a string"
        assert isinstance(value, list), f"Value for '{key}' should be a list"
        for item in value:
            assert isinstance(item, dict), f"Item {item} should be a dict"
            assert "column_name" in item, f"column_name {item} should be in dict"
            assert (
                "table_reference" in item
            ), f"table_reference {item} should be in dict"
            assert (
                "column_reference" in item
            ), f"column_reference {item} should be in dict"
            assert "start_arrow" in item, f"start_arrow {item} should be in dict"
            assert "end_arrow" in item, f"end_arrow {item} should be in dict"
            assert all(
                isinstance(x, str) for x in item.values()
            ), f"All value {item} elements should be strings"


def check_arrange_type(mock_generator: DrawioGenerator) -> None:
    """Ensure tables have the correct type: Dict[str, Tuple[int, int]]"""
    assert isinstance(mock_generator.positions, dict), "positions should be a dict"
    for key, value in mock_generator.positions.items():
        assert isinstance(key, str), f"Key '{key}' should be a string"
        assert isinstance(value, tuple), f"Value for '{value}' should be a tuple"
        assert len(value) == 2, f"Tuple {value} should have 2 elements"
        assert all(
            isinstance(x, int) for x in value
        ), f"Tuple {value} elements should be strings"


def check_table_content(
    mock_generator: DrawioGenerator,
    table_name: str,
    expected_columns: List[Tuple[str, str]],
) -> None:
    """Check that a specific table matches the expected columns."""
    assert table_name in mock_generator.tables, f"{table_name} should exist in tables"
    actual = mock_generator.tables[table_name]
    assert (
        actual == expected_columns
    ), f"TABLE {table_name}: Expected {expected_columns}, got {actual}"


def check_reference_content(
    mock_generator: DrawioGenerator,
    table_name: str,
    expected_references: List[Dict[str, str]],
) -> None:
    """Check that a specific reference matches expected."""
    assert (
        table_name in mock_generator.references
    ), f"{table_name} should exist in references"
    actual = mock_generator.references[table_name]
    assert (
        actual == expected_references
    ), f"REFERENCE {table_name}: Expected {expected_references}, got {actual}"


def check_arrange_content(
    mock_generator: DrawioGenerator,
    table_name: str,
    expected_arrange: Tuple[int, int],
) -> None:
    """Check that a specific arrange matches expected."""
    assert (
        table_name in mock_generator.positions
    ), f"{table_name} should exist in positions"
    actual = mock_generator.positions[table_name]
    assert (
        actual == expected_arrange
    ), f"ARRANGE {table_name}: Expected {expected_arrange}, got {actual}"


def test_import_file(mock_generator: DrawioGenerator) -> None:
    # Assert
    check_generator_attributes(mock_generator)
    check_tables_type(mock_generator)

    # Assert: Tables content
    check_table_content(
        mock_generator, "TEST_TABLE", [("COLUMN1", "PK"), ("COLUMN2", "FK")]
    )

    check_table_content(
        mock_generator, "TEST_TABLE2", [("COLUMN4", "PK"), ("COLUMN5", "FK")]
    )

    check_table_content(
        mock_generator, "TEST_TABLE3", [("COLUMN6", "PK"), ("COLUMN7", "")]
    )

    # Assert: References content
    check_reference_type(mock_generator)
    check_reference_content(
        mock_generator,
        "TEST_TABLE",
        [
            {
                "column_name": "COLUMN1",
                "table_reference": "TEST_TABLE2",
                "column_reference": "COLUMN5",
                "start_arrow": "ERmany",
                "end_arrow": "ERone",
            },
            {
                "column_name": "COLUMN2",
                "table_reference": "TEST_TABLE3",
                "column_reference": "COLUMN6",
                "start_arrow": "ERmany",
                "end_arrow": "ERone",
            },
        ],
    )

    check_reference_content(
        mock_generator,
        "TEST_TABLE3",
        [
            {
                "column_name": "COLUMN6",
                "table_reference": "TEST_TABLE",
                "column_reference": "COLUMN2",
                "start_arrow": "",
                "end_arrow": "",
            }
        ],
    )

    # Assert: Arrange content
    check_arrange_type(mock_generator)
    check_arrange_content(mock_generator, "TEST_TABLE", (10, 10))

    # Assert: Title and Created content
    assert isinstance(mock_generator.title, str)
    assert isinstance(mock_generator.created_at_string, str)


@pytest.mark.parametrize(
    "table_name, expected_color",
    [
        ("DIM_CUSTOMER", "#9CD6EF"),
        ("FACT_SALES", "#F4AC9F"),
    ],
)
def test_create_table_xml(
    mock_generator: DrawioGenerator,
    table_name: str,
    expected_color: List[Tuple[str, str]],
) -> None:
    # Arrange
    # generator = DrawioGenerator()
    root = ET.Element("root")
    columns = [("id", "PK"), ("name", "")]

    # Patch _add_columns to avoid running it fully
    with patch.object(mock_generator, "_add_columns") as mock_add_columns:
        # Act
        updated_root, width = mock_generator._create_table_xml(
            root=root,
            table_name=table_name,
            columns=columns,
            x=10,
            y=20,
            base_width=170,
            height=30,
        )

        # Assert: table_sizes updated
        expected_height = 30 * (len(columns) + 1)
        assert (
            table_name in mock_generator.table_sizes
        ), "table_sizes should contain the table"
        assert mock_generator.table_sizes[table_name] == (width, expected_height)

        # Assert: root has the new table mxCell
        mx_cells = [
            elem
            for elem in updated_root.findall(".//mxCell")
            if elem.get("value") == table_name
        ]
        assert mx_cells, f"Should create mxCell with value={table_name}"
        mx_cell = mx_cells[0]

        # Assert: style has the expected fillColor
        style = mx_cell.get("style")
        assert (
            expected_color in style
        ), f"Expected fillColor {expected_color} in style: {style}"

        # Assert: geometry attributes
        mxGeometrys = [
            elem
            for elem in updated_root.findall(".//mxGeometry")
            if elem.get("as") == "geometry"
        ]
        mxGeometry = mxGeometrys[0]

        geom_attrs = {
            k: v
            for k, v in mxGeometry.attrib.items()
            if k in {"x", "y", "width", "height"}
        }
        assert geom_attrs.get("x") == "10"
        assert geom_attrs.get("y") == "20"
        assert geom_attrs.get("width") == str(width)
        assert geom_attrs.get("height") == str(expected_height)

        # Assert: _add_columns called correctly
        mock_add_columns.assert_called_once_with(
            updated_root, table_name, columns, width, 30
        )


def test_create_erd_xml(mock_generator: DrawioGenerator) -> None:
    root = ET.Element("root")
    result = mock_generator._create_erd_xml(root)

    assert isinstance(result, ET.Element)
    assert result.tag == "root"
    assert len(result) > 0  # It should contain sub-elements
    print(ET.tostring(result, encoding="unicode"))
    assert len(mock_generator.tables) == 3


def test_create_root(mock_generator: DrawioGenerator) -> None:
    root = mock_generator._create_root()
    assert isinstance(root, ET.Element)
    assert root.tag == "root"


def test_create_id_format_and_uniqueness(mock_generator: DrawioGenerator) -> None:

    id1 = mock_generator._create_id()
    id2 = mock_generator._create_id()

    # Assert it's a string
    assert isinstance(id1, str)

    # Assert correct format: 32-character hex
    assert len(id1) == 32
    assert all(c in "0123456789abcdef" for c in id1)

    # Assert uniqueness
    assert id1 != id2


def test_add_edge_creates_correct_xml(mock_generator: DrawioGenerator) -> None:
    root = ET.Element("root")
    edge_id = "e1"
    source_id = "col1"
    target_id = "col2"
    start_arrow = EDGES[0]
    end_arrow = EDGES[1]

    updated_root = mock_generator._add_edge(
        root=root,
        edge_id=edge_id,
        source_id=source_id,
        target_id=target_id,
        start_arrow=start_arrow,
        end_arrow=end_arrow,
    )

    # Check mxCell added
    edge_elem = updated_root.find(f".//mxCell[@id='{edge_id}']")
    assert edge_elem is not None
    assert edge_elem.attrib["source"] == source_id
    assert edge_elem.attrib["target"] == target_id
    assert "startArrow" in edge_elem.attrib["style"]
    assert "endArrow" in edge_elem.attrib["style"]

    # Check mxGeometry child
    geometry = edge_elem.find("mxGeometry")
    assert geometry is not None
    assert geometry.attrib["as"] == "geometry"

    # Check mxPoint elements
    points = geometry.findall("mxPoint")
    assert len(points) == 2
    assert points[0].attrib["as"] == "sourcePoint"
    assert points[1].attrib["as"] == "targetPoint"


def test_create_row_id_valid(mock_generator: DrawioGenerator) -> None:
    tables = {
        "FACT_SALES": [("id", "int"), ("amount", "float")],
        "DIM_DATE": [("date", "date"), ("month", "str")],
    }

    row_id = mock_generator._create_row_id(tables, "FACT_SALES", "amount")
    assert row_id == "FACT_SALES-2"


def test_create_row_id_invalid_column(mock_generator: DrawioGenerator) -> None:
    tables = {"FACT_SALES": [("id", "int"), ("amount", "float")]}

    with pytest.raises(ValueError, match="Column 'price' not found"):
        mock_generator._create_row_id(tables, "FACT_SALES", "price")


def test_create_row_id_invalid_table(mock_generator: DrawioGenerator) -> None:
    tables = {"FACT_SALES": [("id", "int"), ("amount", "float")]}

    with pytest.raises(
        KeyError
    ):  # Because tables["UNKNOWN"] will raise KeyError before ValueError
        mock_generator._create_row_id(tables, "UNKNOWN", "id")


def test_create_edges_adds_expected_edge(mock_generator: DrawioGenerator) -> None:
    root = ET.Element("root")
    updated_root = mock_generator._create_edges(root)

    # Check that an mxCell edge was added
    edge_cells = updated_root.findall(".//mxCell")
    assert len(edge_cells) == 3

    edge = edge_cells[0]
    style = edge.attrib.get("style", "")

    assert edge.attrib["source"].startswith("TEST_TABLE-1")
    assert edge.attrib["target"].startswith("TEST_TABLE2-")
    assert "startArrow" in style
    assert "endArrow" in style

    # Check nested geometry structure
    geometry = edge.find("mxGeometry")
    assert geometry is not None
    assert geometry.find("mxPoint[@as='sourcePoint']") is not None
    assert geometry.find("mxPoint[@as='targetPoint']") is not None


def test_add_date_table_structure(mock_generator: DrawioGenerator) -> None:
    root = ET.Element("root")
    updated_root = mock_generator._add_date(root)

    # Check main date table
    table = updated_root.find(".//mxCell[@id='table-date']")
    assert table is not None
    assert table.attrib["parent"] == "1"
    assert table.attrib["vertex"] == "1"

    # Check rows
    row0 = updated_root.find(".//mxCell[@id='table-date-0']")
    row1 = updated_root.find(".//mxCell[@id='table-date-1']")
    assert row0 is not None
    assert row1 is not None
    assert row0.attrib["parent"] == "table-date"
    assert row1.attrib["parent"] == "table-date"

    # Check cells
    cell_0_0 = updated_root.find(".//mxCell[@id='table-date-0-0']")
    cell_0_1 = updated_root.find(".//mxCell[@id='table-date-0-1']")
    cell_1_0 = updated_root.find(".//mxCell[@id='table-date-1-0']")
    cell_1_1 = updated_root.find(".//mxCell[@id='table-date-1-1']")

    assert cell_0_0.attrib["value"] == "CreatedAt:"
    assert cell_0_1.attrib["value"] == "2024-01-01"
    assert cell_1_0.attrib["value"] == "UpdatedAt:"
    assert cell_1_1.attrib["value"] == date.today().isoformat()


def test_write_mxgraph_creates_file(tmp_path: pathlib.Path) -> None:
    # Arrange
    generator = DrawioGenerator()
    generator.output_dir = tmp_path
    generator.tables = {"TABLE": [("id", "int")]}
    generator.references = {}
    generator.title = "My Diagram"
    generator.created_at_string = "2025-01-01"

    # You may need to stub minimal implementations or mock the following methods
    # if they're not already functional
    generator._create_root = lambda: ET.Element("root")
    generator._create_edges = lambda root: root
    generator._create_erd_xml = lambda root: root
    generator._add_title = lambda root: root
    generator._add_date = lambda root: root

    output_file = tmp_path / "output.drawio"

    # Act
    generator.write_mxgraph("output.drawio")

    # Assert
    assert output_file.exists()

    # Optionally parse and check contents
    tree = ET.parse(output_file)
    root = tree.getroot()
    assert root.tag == "mxGraphModel"
    assert root.find("root") is not None
