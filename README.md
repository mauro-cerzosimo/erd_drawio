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
INPUT_FILE_NAME_PATH="input/orders.dsl"
OUTPUT_FILE_NAME="orders.drawio"
```

---

## 📂 Create input folder

Make sure you have an `input` folder in your project directory, and place your `.dsl` files (like `orders.dsl`) inside it:

```bash
mkdir input
```

Example:

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

  TABLE DIM_PRODUCTS {
      PRODUCT_ID PK
      PRODUCT_NAME

  }
    
  TABLE DIM_CUSTOMERS {
      CUSTOMER_ID PK
      CUSTOMER_NAME
  }
  ```

* **References / relationships**

  ```dsl
  REFERENCE FACT_ORDERS.PRODUCT_ID -> DIM_ORDERS.PRODUCT_ID
  REFERENCE FACT_ORDERS.CUSTOMER_ID -> DIM_CUSTOMERS.CUSTOMER_ID [ERmany, ERone]
  ```

* **Arrangement (x, y) positions on the canvas**

  ```dsl
  ARRANGE FACT_ORDERS (30, 200)
  ARRANGE DIM_PRODUCTS (50, 400)
  ```

* **Possible arrow types**
  (these control the relationship arrows on the diagram)

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
 TABLE FACT_ORDERS {
      ORDER_ID PK
      PRODUCT_ID
  }

 TABLE DIM_PRODUCTS {
      PRODUCT_ID PK
      PRODUCT_NAME
  }

 TABLE DIM_CUSTOMERS {
      CUSTOMER_ID PK
      CUSTOMER_NAME
  }

 REFERENCE DIM_ORDERS.PRODUCT_ID -> DIM_ORDERS.PRODUCT_ID
 REFERENCE FACT_ORDERS.CUSTOMER_ID -> DIM_CUSTOMERS.CUSTOMER_ID [ERmany, ERone]

 ARRANGE DIM_ORDERS (30, 200)
 ARRANGE DIM_PRODUCTS (50, 400)
```

---

## 🔄 Watch and auto-run script (watchmedo)

Run this command to automatically update the `.drawio` file whenever the `.dsl` file changes:

```bash
poetry run watchmedo shell-command \
  --patterns="${INPUT_FILE_NAME_PATH}" \
  --command='poetry run python run.py' \
  --wait
```

✅ Make sure your script loads the `.env` file using **python-dotenv**:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## ✅ Pre-commit checks

Run all pre-commit hooks:

```bash
poetry run pre-commit run --all-files
```

