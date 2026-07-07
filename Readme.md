# Real-Time Sales Intelligence Dashboard

A Python + MySQL + Streamlit project that simulates a live sales feed
and visualizes it on an auto-refreshing dashboard.

## What this project demonstrates
- Python ↔ MySQL connectivity (using `mysql-connector-python`)
- Reading a CSV with `pandas` and loading it into a relational database
- Writing SQL-backed aggregate queries (grouping, filtering) from Python
- A simulated real-time data stream (new rows inserted on a timer)
- An interactive, auto-refreshing web dashboard built with Streamlit

## Project files
| File | Purpose |
|---|---|
| `sales_data.csv` | Historical sales dataset (6 months, ~3000 records) |
| `setup_database.sql` | Creates the MySQL database and `sales` table |
| `config.py` | Your MySQL connection settings (edit this first!) |
| `load_data.py` | One-time script: loads the CSV into MySQL |
| `generate_live_sales.py` | Simulates live incoming sales (run while dashboard is open) |
| `dashboard.py` | The Streamlit dashboard itself |
| `requirements.txt` | Python package dependencies |

## Setup steps (do these in order)

### 1. Install Python dependencies
```
pip install -r requirements.txt
```

### 2. Create the database and table
Open MySQL (e.g. via MySQL Workbench, or the `mysql` command line) and run:
```
mysql -u root -p < setup_database.sql
```
This creates a database called `sales_intelligence` with a `sales` table inside it.

### 3. Edit config.py
Open `config.py` and put in your real MySQL username and password:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_ACTUAL_PASSWORD",
    "database": "sales_intelligence",
}
```

### 4. Load the historical data
```
python load_data.py
```
You should see: `Inserted 2971 rows into the 'sales' table.`

### 5. Run the dashboard
```
streamlit run dashboard.py
```
This opens in your browser, usually at `http://localhost:8501`.

### 6. (Optional but recommended) Simulate live sales
Open a **second terminal** (keep the dashboard running in the first one) and run:
```
python generate_live_sales.py
```
This inserts one new random sale every 5 seconds. Since the dashboard
auto-refreshes every 5 seconds too, you'll watch the KPIs and charts
update on their own — that's your "real-time" element.

Press `Ctrl+C` in that terminal to stop the simulation whenever you like.

## How to explain "real-time" if your mam asks
Be upfront about it: this isn't connected to an actual live store feed
(no student project realistically has that). Instead, `generate_live_sales.py`
acts as a stand-in for a real point-of-sale system — it's the same idea,
just simulated. The dashboard side (querying MySQL fresh every few seconds
and re-rendering) is exactly what a real production dashboard would do;
only the data source is simulated, not the real-time mechanism itself.

## Possible extensions (if you want to go further)
- Add a "low stock alert" by tracking inventory and subtracting quantities sold
- Add anomaly detection (e.g. flag if a day's revenue drops >30% vs average)
- Deploy the dashboard online (Streamlit Community Cloud) so it's accessible via a link
- Add user authentication so only certain people can view it
- Switch the simulation to pull from a public real-time API instead of random data