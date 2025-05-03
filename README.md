# ERD Drawio

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

Make sure you have an `input` folder in your project directory and place your `.dsl` files (like `orders.dsl`) inside it:

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

* **Tables**

  ```dsl
  TABLE FACT_ORDERS {
      ORDER_ID PK
      PRODUCT_ID
      CUSTOMER_ID
  }
<<<<<<< HEAD

  TABLE DIM_PRODUCTS {
      PRODUCT_ID PK
      PRODUCT_NAME
  }

  TABLE DIM_CUSTOMERS {
      CUSTOMER_ID PK
      CUSTOMER_NAME
  }
=======
>>>>>>> 21b2dc516dce8ae07ce686f6cdec25dbb7ffc74a
  ```

* **References / relationships**

  ```dsl
  REFERENCE FACT_ORDERS.PRODUCT_ID -> DIM_PRODUCTS.PRODUCT_ID
<<<<<<< HEAD
  REFERENCE FACT_ORDERS.CUSTOMER_ID -> DIM_CUSTOMERS.CUSTOMER_ID [ERmany, ERone]
=======
  REFERENCE DIM_CUSTOMERS.CUSTOMER_ID -> FACT_ORDERS.CUSTOMER_ID [ERmany, ERone]
>>>>>>> 21b2dc516dce8ae07ce686f6cdec25dbb7ffc74a
  ```

* **Arrangement (x, y) positions on the canvas**

  ```dsl
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

**Example snippet:**

```dsl
TABLE FACT_ORDERS {
    ORDER_ID PK
    PRODUCT_ID
<<<<<<< HEAD
=======
    CUSTOMER_ID
>>>>>>> 21b2dc516dce8ae07ce686f6cdec25dbb7ffc74a
}

TABLE DIM_PRODUCTS {
    PRODUCT_ID PK
    PRODUCT_NAME
}

TABLE DIM_CUSTOMERS {
    CUSTOMER_ID PK
    CUSTOMER_NAME
}

REFERENCE FACT_ORDERS.PRODUCT_ID -> DIM_PRODUCTS.PRODUCT_ID
<<<<<<< HEAD
REFERENCE FACT_ORDERS.CUSTOMER_ID -> DIM_CUSTOMERS.CUSTOMER_ID [ERmany, ERone]

ARRANGE FACT_ORDERS (30, 200)
ARRANGE DIM_PRODUCTS (50, 400)
=======
REFERENCE DIM_CUSTOMERS.CUSTOMER_ID -> FACT_ORDERS.CUSTOMER_ID [ERmany, ERone]

ARRANGE DIM_PRODUCTS (50, 400)
ARRANGE DIM_CUSTOMERS (30, 200)
```

---

## 🔄 Watch and auto-run script (watchmedo)

Run this command to automatically update the `.drawio` file whenever the `.dsl` file changes:

```bash
poetry run watchmedo shell-command \
  --patterns="*.dsl" \
  --recursive \
  --command='poetry run python run.py' \
  input/
```

✅ Notes:

* This watches the `input/` folder for any `.dsl` file changes.
* Make sure your script loads the `.env` file using **python-dotenv**:

```python
from dotenv import load_dotenv
load_dotenv()
>>>>>>> 21b2dc516dce8ae07ce686f6cdec25dbb7ffc74a
```

---

## ✅ Pre-commit checks

Run all pre-commit hooks:

```bash
poetry run pre-commit run --all-files
```

---

## ⚡ Makefile for common tasks

Add this `Makefile` to your project root:

```makefile
.PHONY: watch lint format

watch:
	poetry run watchmedo shell-command \
		--patterns="*.dsl" \
		--recursive \
		--command='poetry run python run.py' \
		input/

lint:
	poetry run ruff check .

format:
	poetry run black .
```

---

### 🚀 Usage

* **Watch and auto-run script on DSL changes**

  ```bash
  make watch
  ```

  ✅ Make sure your script loads the `.env` file using **python-dotenv**:

  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

* **Run lint checks**

  ```bash
  make lint
  ```

* **Auto-format code**

  ```bash
  make format
  ```
