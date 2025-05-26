from textwrap import dedent

SQL_GENERATION_SYSTEM_PROMPT = dedent("""
    ### Instructions:
    Your task is to convert a question into a SQL query, given a Postgres database schema.
    Adhere to these rules:
    - **Deliberately go through the question and database schema word by word** to appropriately answer the question
    - **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
    - When creating a ratio, always cast the numerator as float

    ### Input:
    Generate a SQL query that answers the question `{question}`.
    This query will run on a database whose schema is represented in this string:
    -- 1. Geographies

    CREATE TABLE countries (
      country_id   INT             PRIMARY KEY,
      country_name VARCHAR(100)    NOT NULL
    );

    CREATE TABLE states (
      state_id   INT             PRIMARY KEY,
      state_name VARCHAR(100)    NOT NULL,
      region     VARCHAR(100),
      country_id INT             NOT NULL,
      CONSTRAINT fk_states_country
        FOREIGN KEY(country_id)
          REFERENCES countries(country_id)
    );

    CREATE TABLE cities (
      city_id    INT             PRIMARY KEY,
      city_name  VARCHAR(100)    NOT NULL,
      latitude   NUMERIC(9,6),
      longitude  NUMERIC(9,6),
      state_id   INT             NOT NULL,
      CONSTRAINT fk_cities_state
        FOREIGN KEY(state_id)
          REFERENCES states(state_id)
    );

    -- 2. Addresses

    CREATE TABLE addresses (
      address_id INT          PRIMARY KEY,
      street     VARCHAR(255),
      zipcode    VARCHAR(20),
      city_id    INT          NOT NULL,
      CONSTRAINT fk_addresses_city
        FOREIGN KEY(city_id)
          REFERENCES cities(city_id)
    );

    -- 3. Customers & lookups

    CREATE TABLE customers (
      customer_id        INT       PRIMARY KEY,
      first_name         VARCHAR(50),
      last_name          VARCHAR(50),
      email              VARCHAR(100) UNIQUE,
      password           VARCHAR(255),
      segment            VARCHAR(50),
      sales_per_customer FLOAT,
      address_id         INT       NOT NULL,
      CONSTRAINT fk_customers_address
        FOREIGN KEY(address_id)
          REFERENCES addresses(address_id)
    );

    CREATE TABLE payment_types (
      payment_type_id INT      PRIMARY KEY,
      name            VARCHAR(50) NOT NULL
    );

    CREATE TABLE delivery_statuses (
      delivery_status_id INT      PRIMARY KEY,
      name               VARCHAR(50) NOT NULL
    );

    CREATE TABLE shipping_modes (
      shipping_mode_id INT      PRIMARY KEY,
      name             VARCHAR(50) NOT NULL
    );

    CREATE TABLE markets (
      market_id INT           PRIMARY KEY,
      name      VARCHAR(100)  NOT NULL
    );

    -- 4. Product hierarchy

    CREATE TABLE categories (
      category_id INT           PRIMARY KEY,
      name        VARCHAR(100)  NOT NULL
    );

    CREATE TABLE departments (
      department_id INT           PRIMARY KEY,
      name          VARCHAR(100)  NOT NULL
    );

    CREATE TABLE products (
      product_id    INT           PRIMARY KEY,
      name          VARCHAR(100)  NOT NULL,
      description   TEXT,
      image_url     VARCHAR(255),
      price         FLOAT         NOT NULL,
      status        VARCHAR(50),
      category_id   INT           NOT NULL,
      department_id INT           NOT NULL,
      CONSTRAINT fk_products_category
        FOREIGN KEY(category_id)
          REFERENCES categories(category_id),
      CONSTRAINT fk_products_department
        FOREIGN KEY(department_id)
          REFERENCES departments(department_id)
    );

    -- 5. Orders & items

    CREATE TABLE orders (
      order_id            INT        PRIMARY KEY,
      customer_id         INT        NOT NULL,
      order_date          DATE       DEFAULT CURRENT_DATE,
      shipping_date       DATE,
      scheduled_days      INT,
      actual_days         INT,
      benefit_per_order   FLOAT,
      late_delivery_risk  BOOLEAN,
      payment_type_id     INT        NOT NULL,
      delivery_status_id  INT        NOT NULL,
      shipping_mode_id    INT        NOT NULL,
      market_id           INT,
      shipping_address_id INT        NOT NULL,
      CONSTRAINT fk_orders_customer
        FOREIGN KEY(customer_id)
          REFERENCES customers(customer_id),
      CONSTRAINT fk_orders_payment_type
        FOREIGN KEY(payment_type_id)
          REFERENCES payment_types(payment_type_id),
      CONSTRAINT fk_orders_delivery_status
        FOREIGN KEY(delivery_status_id)
          REFERENCES delivery_statuses(delivery_status_id),
      CONSTRAINT fk_orders_shipping_mode
        FOREIGN KEY(shipping_mode_id)
          REFERENCES shipping_modes(shipping_mode_id),
      CONSTRAINT fk_orders_market
        FOREIGN KEY(market_id)
          REFERENCES markets(market_id),
      CONSTRAINT fk_orders_address
        FOREIGN KEY(shipping_address_id)
          REFERENCES addresses(address_id)
    );

    CREATE TABLE order_items (
      order_item_id   INT     PRIMARY KEY,
      order_id        INT     NOT NULL,
      product_id      INT     NOT NULL,
      product_price   FLOAT,
      quantity        INT,
      discount_amount FLOAT,
      discount_rate   FLOAT,
      sales           FLOAT,
      total           FLOAT,
      profit_ratio    FLOAT,
      CONSTRAINT fk_items_order
        FOREIGN KEY(order_id)
          REFERENCES orders(order_id),
      CONSTRAINT fk_items_product
        FOREIGN KEY(product_id)
          REFERENCES products(product_id)
    );



    ### Response:
    Based on your instructions, here is the SQL query I have generated to answer the question `{question}`:
    ```sql
""")
