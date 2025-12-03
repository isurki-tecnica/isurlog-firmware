import influxdb_client
from datetime import datetime

# --- Connection Parameters (Provided by Isurki) ---

URL = "https://influxisurdash.isurki.com"
ORG = "isurki"
TOKEN = "YOUR_UNIQUE_API_TOKEN_HERE" # Replace with the client's private token
BUCKET = "YOUR_UNIQUE_BUCKET_HERE" # Replace with the client's dedicated bucket name

def get_isurlog_readings(device_id: str, days_range: int = 7) -> list:
    """
    Connects to InfluxDB and queries ALL recorded values within a specified range
    for a given device and returns them as a structured list of dictionaries.

    Args:
        device_id: The unique identifier (e.g., EUI) of the Isurlog device.
        days_range: The number of past days to query data from.

    Returns:
        A list of dictionaries, where each dictionary represents one reading record,
        or an empty list if no data is found or an error occurs.
    """
    
    # It is recommended to create one client instance and reuse it.
    with influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
        query_api = client.query_api()

        # Flux query to get ALL values within the range for a device
        # We query for ALL fields that exist in the measurement (by removing the field filter)
        query = f'''
        from(bucket: "{BUCKET}")
          |> range(start: -{days_range}d)
          |> filter(fn: (r) => r["isurlog_id"] == "{device_id}")
        '''
        
        all_records = []
        
        try:
            tables = query_api.query(query, org=ORG)
            
            # Temporary dictionary to group measurements by timestamp (using the datetime object)
            grouped_readings = {}

            for table in tables:
                for record in table.records:
                    # The record.get_time() returns a native Python datetime object
                    time_dt = record.get_time() 
                    field = record.get_field()
                    value = record.get_value()
                    
                    # Use the raw datetime object as the key for grouping
                    if time_dt not in grouped_readings:
                        # Store the datetime object directly
                        grouped_readings[time_dt] = {"Time": time_dt} 
                    
                    grouped_readings[time_dt][field] = value

            # Convert dictionary into a sorted list of records
            for time in sorted(grouped_readings.keys()):
                all_records.append(grouped_readings[time])
                
        except Exception as e:
            print(f"An error occurred while querying InfluxDB: {e}")
            return []
            
        return all_records

def print_data_as_table(data: list):
    """Imprime los datos recuperados en un formato tabular limpio."""
    if not data:
        return

    # 1. Collect all unique column headers
    headers = set()
    for record in data:
        headers.update(record.keys())
    
    # Ensure "Time" is the first header
    sorted_headers = ["Time"] + sorted([h for h in headers if h != "Time"])

    # 2. Print Header Row
    print("\n| " + " | ".join(sorted_headers) + " |")
    print("|" + "---|" * len(sorted_headers))

    # 3. Print Data Rows
    for record in data:
        row_values = []
        for header in sorted_headers:
            value = record.get(header)
            
            if header == "Time" and isinstance(value, datetime):
                # Format the native datetime object directly
                row_values.append(value.strftime("%Y-%m-%d %H:%M:%S"))
            elif value is not None:
                # Format float/int values
                row_values.append(f"{value:.2f}" if isinstance(value, float) else str(value))
            else:
                row_values.append("-") # Use dash for missing values

        print("| " + " | ".join(row_values) + " |")


# --- Example Usage ---
if __name__ == "__main__":
    target_device = "c-123" # Example device ID
    data = get_isurlog_readings(target_device, days_range=7)
    
    if data:
        print(f"--- Retrieved Data for device '{target_device}' (Last 7 Days) ---")
        print_data_as_table(data)
    else:
        print(f"No data found for device '{target_device}' or an error occurred.")