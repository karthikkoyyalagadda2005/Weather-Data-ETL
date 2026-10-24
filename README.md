Cloud Weather Analytics Pipeline
A Python-based weather data engineering project that ingests current weather observations for four Indian cities, stores raw API responses in a data-lake-style directory, transforms the records with Pandas, builds a dimensional analytics model, loads it into a SQLite data warehouse, runs SQL window-function analytics, and requests an executive summary from Google Gemini.
Project status: Local prototype / cloud-oriented data pipeline. The supplied source code does not provision or deploy cloud infrastructure. The raw-data directory and SQLite warehouse are local files. Gemini is the only cloud AI service called by the script.
Contents
    • Project overview
    • Architecture
    • Technology stack
    • Features
    • Project structure
    • Requirements
    • Setup
    • Configuration
    • Run the pipeline
    • Data model
    • Analytics query
    • Output and generated files
    • Verification findings
    • Troubleshooting
    • Security and reliability
    • Cloud deployment roadmap
    • License
Project overview
The pipeline demonstrates an end-to-end analytics workflow:
    1. Ingest: Call the Open-Meteo forecast API for Hyderabad, Bengaluru, Chennai, and Mumbai.
    2. Stage: Save the collected records as a timestamped JSON file in datalake_raw/.
    3. Transform: Flatten weather responses into a Pandas DataFrame, remove rows with missing values, and parse timestamps.
    4. Model: Create city and date dimension tables plus a weather fact table.
    5. Load: Write the analytical tables to a local SQLite database.
    6. Analyze: Execute a Common Table Expression (CTE) and SQL window functions.
    7. Generate insight: Send the analytics results to Google Gemini and print a concise executive summary.
Project goals
    • Understand the ETL/ELT pipeline lifecycle.
    • Work with REST APIs and JSON data.
    • Use Python and Pandas for data cleaning and transformation.
    • Apply dimensional modeling concepts, including fact and dimension tables.
    • Practice SQL joins, CTEs, aggregate window functions, and ranking.
    • Integrate a generative AI API into an analytics workflow.
Architecture
Open-Meteo Forecast API
          |
          v
Python requests client
          |
          v
Raw JSON staging
datalake_raw/weather_raw_<timestamp>.json
          |
          v
Pandas transformation and data cleansing
          |
          v
Dimensional model
  +------------------+
  | dim_city         |
  | dim_date         |
  | fact_weather     |
  +------------------+
          |
          v
SQLite analytics warehouse
cloud_analytics_dw.db
          |
          v
SQL CTE + window functions
          |
          v
Analytics records serialized as JSON
          |
          v
Google Gemini API
          |
          v
Executive summary printed in terminal
Deployment distinction: datalake_raw/ is a local directory and cloud_analytics_dw.db is a local SQLite file. They are useful for a prototype but are not managed cloud storage or a cloud data warehouse.
Technology stack
Component	Technology	Purpose
Language	Python	Pipeline orchestration
API client	requests	Retrieve weather data
Source API	Open-Meteo	Current weather observations
Transformation	Pandas	Flatten, clean, and reshape data
Raw staging	JSON files	Retain source API responses
Analytical storage	SQLite	Store fact and dimension tables
SQL analytics	SQLite SQL	CTEs, joins, ranking, window calculations
AI integration	Google Gen AI Python SDK	Generate an executive summary
Configuration	python-dotenv	Load environment variables from .env

Features
    • Fetches current weather information for four configured cities.
    • Records latitude and longitude with each source observation.
    • Retains raw API responses in timestamped JSON files.
    • Converts source records into a tabular format.
    • Removes rows containing null values before modeling.
    • Builds dim_city, dim_date, and fact_weather tables.
    • Uses SQL window functions to calculate a global average and temperature rank.
    • Passes analytics results to Gemini for a short natural-language summary.
    • Handles Gemini-related errors by printing an error message rather than terminating silently.
Project structure
The supplied archive contains the following files:
cloud_proj/
├── cloud.py          # Complete ingestion, ETL, warehouse, SQL, and AI workflow
└── .cloud.py.swp     # Editor swap file; not part of the application
When the script runs successfully, it creates additional files in the current working directory:
datalake_raw/
└── weather_raw_YYYYMMDD_HHMMSS.json

cloud_analytics_dw.db
The .cloud.py.swp file is a Vim/editor swap file and should not be treated as source code. Remove it from a cleaned project copy only after confirming that no editor session needs it.
Recommended project layout after adding configuration and dependency files:
cloud_proj/
├── cloud.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── datalake_raw/             # Runtime output; normally git-ignored
└── cloud_analytics_dw.db     # Runtime output; normally git-ignored
Requirements
    • Python 3.10 or newer is recommended.
    • Internet access to reach the Open-Meteo API.
    • A Google Gemini API key for AI summary generation.
    • A Python environment in which the dependencies can be installed.
Check the Python version:
python3 --version
Setup
1. Open the project directory
Extract the archive and enter the directory:
unzip cloud_proj.zip
cd cloud_proj
If it is already extracted, change into the extracted project folder.
2. Create and activate a virtual environment
Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
Windows PowerShell:
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
3. Install dependencies
Install the libraries imported by the supplied script:
python -m pip install requests pandas python-dotenv google-genai
Create a dependency manifest after verifying the environment:
python -m pip freeze > requirements.txt
On a later installation, restore dependencies with:
python -m pip install -r requirements.txt
For a team or production deployment, maintain a reviewed, pinned dependency manifest rather than relying on whichever package versions happen to be installed.
4. Configure the Gemini API key
Create a local .env file in the same directory as cloud.py:
GEMINI_API_KEY=replace_with_your_gemini_api_key
Get an API key from Google AI Studio. Do not commit the real .env file to version control.
The script calls load_dotenv() and reads the key using os.getenv("GEMINI_API_KEY"). The current code attempts to initialize Gemini even when the key is missing; configure the key before running if you want AI summaries to work.
Configuration
The current script hard-codes the city list and their coordinates:
City	Latitude	Longitude
Hyderabad	17.3850	78.4867
Bengaluru	12.9716	77.5946
Chennai	13.0827	80.2707
Mumbai	19.0760	72.8777

The following settings are currently embedded in the code rather than exposed as configuration:
    • Weather API URL and request parameters.
    • City coordinates.
    • Raw-data output directory.
    • SQLite database filename.
    • Gemini model identifier.
    • AI prompt and expected summary length.
For easier maintenance, consider moving these settings into environment variables or a configuration file. Validate the Gemini model identifier against the models enabled for the API key and account before running the AI step.
Run the pipeline
From the project directory, with the virtual environment activated and .env configured:
python cloud.py
The script is a single-run batch pipeline. It is not a continuously running service or scheduled job.
The terminal output is organized into steps:
    1. Live API ingestion and raw JSON staging.
    2. Data processing and dimensional modeling.
    3. Loading tables into SQLite.
    4. Running SQL analytics.
    5. Requesting a Gemini-generated insight.
Verify generated files
After a successful run:
ls -lh datalake_raw/
ls -lh cloud_analytics_dw.db
Inspect the SQLite tables:
python - <<'PY'
import sqlite3

conn = sqlite3.connect("cloud_analytics_dw.db")
for row in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
):
    print(row[0])
conn.close()
PY
Expected table names are:
    • dim_city
    • dim_date
    • fact_weather
The actual row counts and results depend on API availability and the observations returned at run time.
Data model
The script attempts to create a basic star schema.
dim_city
One row per distinct city and coordinate pair.
Column	Meaning
city_name	City name
latitude	Latitude used in the API request
longitude	Longitude used in the API request
city_id	Generated integer identifier

dim_date
Intended to represent distinct observation timestamps and their calendar attributes.
Column	Meaning
timestamp	Observation timestamp
year	Calendar year
month	Calendar month
day	Day of month
hour	Hour component
date_id	Generated integer identifier

Verification note: the current construction of dim_date needs correction. It combines a deduplicated timestamp Series with non-deduplicated date-part Series. When multiple cities share a timestamp, Pandas aligns those Series by index, which can introduce null timestamps and create incorrect date-key mappings. See Verification findings.
fact_weather
Intended to store weather measurements linked to the city and date dimensions.
Column	Meaning
record_id	Generated fact-row identifier
city_id	Reference to dim_city.city_id
date_id	Intended reference to dim_date.date_id
temperature_celsius	Temperature returned by the source API
windspeed_kmh	Wind speed returned by the source API
weather_condition_code	Weather code returned by the source API

The source script assumes the API's current-weather fields are available and uses the provider's units. Confirm the Open-Meteo response and units before treating the measurements as production data.
Analytics query
The script runs a CTE that joins the weather fact table to the city dimension and computes:
    • global_avg_temp using AVG(...) OVER().
    • temp_rank using RANK() OVER(ORDER BY ... DESC).
Simplified form:
WITH WeatherMetrics AS (
    SELECT
        c.city_name,
        f.temperature_celsius,
        f.windspeed_kmh,
        AVG(f.temperature_celsius) OVER() AS global_avg_temp,
        RANK() OVER(ORDER BY f.temperature_celsius DESC) AS temp_rank
    FROM fact_weather f
    JOIN dim_city c ON f.city_id = c.city_id
)
SELECT * FROM WeatherMetrics;
RANK() assigns rank 1 to the highest temperature and gives tied values the same rank, leaving gaps after ties. Despite the prompt's request for the city with the “most extreme weather,” this query ranks temperature only; it does not define a comprehensive extreme-weather score or compare wind speed and weather condition codes.
Output and generated files
Raw JSON staging
Each successful API response contributes a record containing:
    • City name.
    • Latitude and longitude.
    • The API's current_weather object.
The file name includes the run timestamp. This is a useful raw-ingestion pattern, but the script currently does not log failed city requests into a separate error file.
SQLite warehouse
The script uses if_exists="replace" for all three tables. That means each run replaces the existing tables rather than appending a history of observations. The raw JSON files accumulate by run, but the analytical database represents the latest successful load only.
AI summary
The AI prompt asks Gemini for a concise three-line executive summary based on the SQL result rows. The summary is printed in the terminal and is not saved to the database or a report file.
Verification findings
The source was reviewed statically from the supplied archive. These findings are based on the code, not a claim that the full pipeline was executed successfully against live services.
1. Date dimension construction can corrupt joins — high priority
The code creates dim_date from a deduplicated timestamp series and date-part series derived from the full DataFrame. Pandas aligns Series by index, so the columns may no longer represent the same rows. Shared timestamps across cities are a likely case.
Recommendation: build the dimension from a deduplicated DataFrame first, then derive all date attributes from that DataFrame. Create a stable mapping from each unique timestamp to its date key and merge that mapping into the fact rows.
2. No request timeout or exception handling for weather ingestion — high priority
requests.get(url) has no timeout, and connection exceptions are not caught. A slow or unavailable endpoint can hang the run or stop the pipeline.
Recommendation: use explicit connect/read timeouts, call raise_for_status(), validate the response schema, and handle each city's failure independently. Record failures in structured logs.
3. Empty or incomplete ingestion is not handled explicitly — high priority
Failed HTTP responses are silently skipped. If every request fails, later DataFrame and date-processing operations may fail or produce empty tables.
Recommendation: validate that at least one usable observation exists before starting ETL. Define whether partial city results are acceptable, and stop with a clear error if required data is missing.
4. Gemini model availability is not verified — high priority for the AI stage
The source hard-codes gemini-3.8-flash. Model names and availability depend on the current Google Gen AI API and account. This review does not confirm that this exact model identifier is available.
Recommendation: check the current Google Gen AI model documentation and the models available to the configured API key. Make the model name configurable, and test the AI call independently.
5. Missing API key is not validated before client creation — medium priority
The code can attempt genai.Client(api_key=None) if GEMINI_API_KEY is absent. The exception is caught in the AI block, but the error will be less clear than a direct configuration message.
Recommendation: validate the environment variable before creating the client. Decide whether AI is required or optional and reflect that choice in the exit status and logs.
6. The date table's date_id represents timestamps, not necessarily calendar dates — medium priority
The dimension includes an hour attribute and is generated from observation timestamps. This behaves more like a timestamp dimension than a conventional calendar-date dimension.
Recommendation: either rename it to dim_datetime and define a timestamp key, or model a separate calendar-date dimension with one row per date and a distinct timestamp/observation dimension if needed.
7. Warehouse tables are replaced on every run — medium priority
Using if_exists="replace" discards the previous analytical tables. This is acceptable for a demo, but it does not preserve historical observations in the warehouse.
Recommendation: for historical analysis, use append/upsert semantics, stable primary keys, deduplication, and explicit retention policies.
8. Generated IDs are not stable across runs — medium priority
city_id, date_id, and record_id are assigned using row order. These values can change when data ordering or source records change.
Recommendation: define primary keys and stable business keys, enforce foreign keys where supported, and use deterministic key mapping or database-generated identifiers.
9. SQL analysis does not fully measure “extreme weather” — medium priority
The SQL ranks temperature and calculates an overall average, but the AI prompt asks for the city with the most extreme weather. Temperature alone may not capture the intended meaning.
Recommendation: define an explicit metric or report separate extremes, such as highest temperature, strongest wind, and relevant weather codes. Make the prompt describe exactly what the data supports.
10. Limited observability and testing — medium priority
The pipeline primarily uses print() statements and has no supplied automated tests, retry policy, metrics, or persistent error report.
Recommendation: use Python logging, unit tests for transformations and schema validation, integration tests with mocked API responses, and a clear non-zero exit status for critical failures.
Verification summary
Area	Static review result
Python source structure	A single-file pipeline is present
API ingestion	Implemented; resilience needs improvement
Raw staging	Implemented using timestamped JSON files
Pandas transformation	Implemented; date dimension bug identified
Dimensional model	Intended star schema present; key mapping needs correction
SQLite warehouse	Implemented with table replacement
SQL analytics	CTE and window functions are present
Gemini integration	Implemented; key and model need runtime validation
Cloud infrastructure	Not provisioned by the supplied code
Automated tests	Not included in the supplied archive
End-to-end runtime verification	Not established by static inspection

Troubleshooting
ModuleNotFoundError
Activate the intended virtual environment and install dependencies:
python -m pip install requests pandas python-dotenv google-genai
Weather API request fails
    • Confirm internet connectivity.
    • Check whether Open-Meteo is reachable.
    • Inspect the HTTP status and response body.
    • Add request timeouts, retries, and per-city exception handling.
    • Verify that the API response includes the expected current_weather fields.
Gemini authentication or model error
    • Check that .env is in the directory from which load_dotenv() can find it.
    • Confirm that GEMINI_API_KEY is set and valid.
    • Check API access, quota, and the exact model identifier.
    • Test Gemini separately from the ETL pipeline to isolate errors.
SQLite database appears empty or has unexpected rows
    • Check whether any weather requests succeeded.
    • Inspect the raw JSON file.
    • Inspect dim_city, dim_date, and fact_weather row counts.
    • Fix the date dimension before trusting fact-to-dimension joins.
    • Remember that the script replaces the tables on each successful load.
Security and reliability
    • Keep .env and real API keys out of Git.
    • Commit .env.example with placeholder values only.
    • Avoid printing secrets or full sensitive request metadata in logs.
    • Add timeouts, retries with backoff, response validation, and structured logging.
    • Treat API responses and AI-generated summaries as external, untrusted data.
    • Validate and constrain any AI-generated claims against warehouse metrics.
    • Add tests before changing the ETL schema or warehouse loading behavior.
    • Back up the SQLite database if its data becomes important.
    • For production, use a secrets manager and managed storage/warehouse services rather than a local .env and SQLite file.
Example .gitignore:
.venv/
__pycache__/
.env
*.swp
datalake_raw/
cloud_analytics_dw.db
Cloud deployment roadmap
To evolve this prototype into a cloud data engineering project, consider the following staged approach:
    1. Object storage: replace or supplement datalake_raw/ with Amazon S3, Azure Blob Storage, or Google Cloud Storage.
    2. Orchestration: schedule the ingestion and transformation with Airflow, a cloud workflow service, or a managed data orchestration tool.
    3. Compute: package the pipeline for a container or managed batch execution environment.
    4. Warehouse: migrate SQLite to a managed analytical warehouse such as BigQuery, Amazon Redshift, Snowflake, or Azure Synapse, depending on the target cloud.
    5. Secrets: store Gemini credentials in a cloud secret manager and use least-privilege identity permissions.
    6. Observability: add structured logs, metrics, alerts, retry policies, and failure notifications.
    7. Data quality: validate schemas, ranges, uniqueness, timestamp consistency, and referential integrity.
    8. Testing and CI/CD: add unit/integration tests, linting, and a pipeline for safe deployment.
    9. Governance: document source attribution, data retention, cost limits, and API usage terms.
    10. AI output validation: verify generated summaries against query results and preserve the metrics used to create each report.
These are recommendations, not features already present in the supplied code.
License
No license file was included in the supplied archive. Add a LICENSE file before distributing the project if you want to grant others explicit reuse rights.
