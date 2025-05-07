# ERD Drawio

## 📊 Example ERD Diagram

![Order ERD Diagram](docs/erd_diagram.drawio.svg)

---


## ⚙️ Setup environment and install Poetry

1. **Create a Python virtual environment**

```bash
pyenv virtualenv 3.11.0 .erd-drawio
```

2. **Activate the virtual environment**

```bash
pyenv activate .erd-drawio
```

3. **Install Poetry inside the virtual environment**

```bash
pip install poetry
```

4. **Install project dependencies**

```bash
poetry install
```

---

## 🌱 Create environment variables

Create a `.env` file in the project root with the following content:

```env
INPUT_FILE_NAME_PATH="orders.dsl"
OUTPUT_FILE_NAME="orders.drawio"
```

---

## 📂 Create input folder

Make sure you have an `input` folder in your project directory, and place your `.dsl` files (like `orders.dsl`) inside it:

```bash
mkdir input
```

Example file path:

```
input/orders.dsl
```

---

## 📏 DSL file format and rules

The `.dsl` file defines your data model and should follow these conventions:

* **Title**

  ```dsl
  TITLE Order Erd Diagram
  ```

* **Create At**
  ```dsl
  CREATEDAT 2025-05-01
  ```

* **Tables**
* Use `*` after the column name for primary keys (PK)

* Use `+` after the column name for foreign keys (FK)

* Use no symbol for regular columns

  ```dsl
  TABLE FACT_ORDERS {
      ORDER_ID *
      PRODUCT_ID +
      CUSTOMER_ID
  }

  TABLE DIM_PRODUCTS {
      PRODUCT_ID *
      PRODUCT_NAME
  }

  TABLE DIM_CUSTOMERS {
      CUSTOMER_ID *
      CUSTOMER_NAME
  }
  ```

* **References / relationships**

  ```dsl
  REFERENCE FACT_ORDERS.PRODUCT_ID -> DIM_PRODUCTS.PRODUCT_ID
  REFERENCE FACT_ORDERS.CUSTOMER_ID -> DIM_CUSTOMERS.CUSTOMER_ID [ERmany, ERone]
  ```

* **Arrangement (x, y) positions on the canvas**

  ```dsl
  ARRANGE FACT_ORDERS (30, 200)
  ARRANGE DIM_PRODUCTS (50, 400)
  ```

* **Possible arrow types**

  ```dsl
  # -- Possible Arrow
  # ERmany
  # ERmandOne
  # ERone
  # ERoneToMany
  # ERzeroToMany
  # ERzeroToOne
  ```

Example snippet:

```dsl
TITLE Order Erd Diagram
CREATEDAT 2025-05-01

TABLE FACT_ORDERS {
    ORDER_ID *
    PRODUCT_ID +
    CUSTOMER_ID 
}

TABLE DIM_PRODUCTS {
    PRODUCT_ID *
    PRODUCT_NAME +
}

TABLE DIM_CUSTOMERS {
    CUSTOMER_ID *
    CUSTOMER_NAME
}

REFERENCE FACT_ORDERS.PRODUCT_ID -> DIM_PRODUCTS.PRODUCT_ID
REFERENCE FACT_ORDERS.CUSTOMER_ID -> DIM_CUSTOMERS.CUSTOMER_ID [ERmany, ERone]

ARRANGE FACT_ORDERS (409, 154)
ARRANGE DIM_PRODUCTS (112, 149)
ARRANGE DIM_CUSTOMERS (108, 316)
```

---

## ✅ Pre-commit checks

Run all pre-commit hooks:

```bash
poetry run pre-commit run --all-files
```

---

## ⚡ Makefile for common tasks


```makefile
.PHONY: watch drawio arrange lint format typecheck

# Watch for changes in input/ and output/ using watcher.py
watch:
	poetry run python watcher.py

# Run the Draw.io generator script manually
drawio:
	poetry run python run_generator.py

# Run the table locator script manually
arrange:
	poetry run python run_table_locator.py

# Run ruff linter
lint:
	poetry run ruff check .

# Run black code formatter
format:
	poetry run black .

# Run mypy type checking
typecheck:
	poetry run mypy .
```

---

### 🚀 Usage

* **Watch and auto-run script on DSL changes**

  ```bash
  make watch
  ```

* **Generate Drawio**
  ```bash
  make drawio
  ```

* **Print Arrange coordinates**
  ```bash
  make arrange
  ```

* **Run lint checks**

  ```bash
  make lint
  ```

* **Auto-format code**

  ```bash
  make format
  ```
* **Run typecheck checks**

  ```bash
  make typecheck
  ```
