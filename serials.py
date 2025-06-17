import subprocess
import csv
import os
import json

def run_curl_requests(list_file='ip_list.csv', password_file='password.txt', results_file='results.csv'):
    """
    Reads a list of server addresses from `list.csv`, a username and password from `password.txt`,
    executes a curl command for each server, and writes the results to `results.csv`.

    Args:
        list_file (str): The name of the CSV file containing server addresses.
                         Each server address should be in column A (first column).
        password_file (str): The name of the text file containing the username on the first line
                             and the password on the second line.
        results_file (str): The name of the CSV file where results will be saved.
    """

    # --- 1. Read Username and Password from password.txt ---
    username = ""
    password = ""
    try:
        with open(password_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) < 2:
                print(f"Error: The file '{password_file}' must contain at least two lines (username then password).")
                return
            username = lines[0].strip()
            password = lines[1].strip()

            if not username:
                print(f"Error: The first line (username) in '{password_file}' is empty.")
                return
            if not password:
                print(f"Error: The second line (password) in '{password_file}' is empty.")
                return
    except FileNotFoundError:
        print(f"Error: The password file '{password_file}' was not found in the same directory.")
        print("Please create a file named 'password.txt' with the username on the first line and password on the second.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading '{password_file}': {e}")
        return

    # --- 2. Read Server List from ip_list.csv ---
    server_list = []
    try:
        with open(list_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip(): # Ensure row is not empty and first column is not empty
                    server_list.append(row[0].strip())
            if not server_list:
                print(f"Warning: The file '{list_file}' is empty or contains no valid server addresses.")
                return
    except FileNotFoundError:
        print(f"Error: The server list file '{list_file}' was not found in the same directory.")
        print("Please create a file named 'ip_list.csv' and put your server addresses (one per line) in it.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading '{list_file}': {e}")
        return

    # --- 3. Prepare results.csv for writing ---
    # 'w' mode will create the file if it doesn't exist, or overwrite it if it does.
    # newline='' is crucial for csv.writer to prevent extra blank rows.
    try:
        with open(results_file, 'w', newline='', encoding='utf-8') as outfile:
            csv_writer = csv.writer(outfile)
            # Write the header row to the results CSV
            csv_writer.writerow(['Server Address', 'Serial Number'])

            # --- 4. Iterate through the server list and execute curl ---
            for server_address in server_list:
                # Construct the full URL for the API call
                url = f"https://{server_address}/api/v1/systeminfo/?format=json"

                # Construct the curl command as a list of strings
                # -k: --insecure, allows insecure server connections (e.g., self-signed SSL certs)
                # -s: --silent, suppresses progress meter and error messages (from curl itself)
                # -S: --show-error, shows error messages even with -s
                # -u: --user, specifies the user and password for basic authentication
                curl_command = [
                    'curl',
                    '-k',
                    '-s',
                    '-S',
                    '-u', f"{username}:{password}", # Using the username variable here
                    url
                ]

                print(f"Attempting to query: {url}...")
                result_to_write = "" # Initialize variable for the output column

                try:
                    # Execute the curl command using subprocess.run
                    # capture_output=True: captures stdout and stderr
                    # text=True: decodes stdout/stderr as text using default encoding
                    # check=False: prevents subprocess.run from raising CalledProcessError
                    #              if the curl command returns a non-zero exit code.
                    #              We'll handle return codes manually.
                    process = subprocess.run(
                        curl_command,
                        capture_output=True,
                        text=True,
                        check=False
                    )

                    # Get the standard output (where the JSON response should be)
                    api_response = process.stdout.strip()
                    # Get the standard error (where curl errors like connection issues will be)
                    curl_stderr = process.stderr.strip()

                    if process.returncode != 0:
                        # Curl command itself returned an error (e.g., connection refused, DNS error)
                        result_to_write = f"CURL ERROR (Exit Code {process.returncode}): {curl_stderr if curl_stderr else 'Unknown curl error or connection issue.'}"
                        print(f"  FAIL: {result_to_write}")
                    elif api_response:
                        # Curl succeeded and returned output.
                        # Do a basic check to see if it looks like JSON.
                        if api_response.startswith(("{", "[")) and api_response.endswith(("}", "]")):
                            result_to_write = api_response # Save the JSON response
                            print(f"  SUCCESS: JSON response for {server_address} captured.")
                            json_data = json.loads(api_response)
                            # Extract 'sn' from the root of the JSON
                            serial_number = json_data.get('sn', 'SN_NOT_FOUND')
                            result_to_write = str(serial_number) # Convert to string for CSV
                            print(f"  SUCCESS: JSON for {server_address} parsed.")
                        else:
                            # Unexpected non-JSON output
                            result_to_write = f"UNEXPECTED RESPONSE: {api_response}"
                            print(f"  WARNING: Received non-JSON output.")
                    else:
                        # No response, but no curl error code
                        result_to_write = "No API response received (might be empty or timeout)."
                        print(f"  WARNING: No response from API.")

                except FileNotFoundError:
                    result_to_write = "ERROR: 'curl' command not found. Please ensure curl is installed and accessible in your system's PATH."
                    print(f"  CRITICAL ERROR: {result_to_write}")
                except Exception as e:
                    result_to_write = f"SCRIPT EXCEPTION: An error occurred during curl execution: {e}"
                    print(f"  CRITICAL ERROR: {result_to_write}")

                # Write the server address and the determined result to the CSV
                csv_writer.writerow([server_address, result_to_write])

        print(f"\nAll queries processed. Results saved to '{results_file}'")

    except Exception as e:
        print(f"An error occurred while writing to '{results_file}': {e}")


# --- How to Run This Script ---
if __name__ == "__main__":
    # This block will run automatically when you execute the script.
    # It also creates dummy files if they don't exist, for easy testing.

    # Dummy ip_list.csv
    if not os.path.exists('ip_list.csv'):
        print("Creating a dummy 'ip_list.csv' for demonstration. Please edit it with your actual server addresses.")
        with open('ip_list.csv', 'w', encoding='utf-8') as f:
            f.write('192.168.0.122\n')
            f.write('api.example.com\n') # Example of a valid domain
            f.write('nonexistent-server.local\n') # Example of a server that won't respond

    # Dummy password.txt
    if not os.path.exists('password.txt'):
        print("Creating a dummy 'password.txt'. IMPORTANT: Replace 'your_secure_password_here' with your actual password!")
        with open('password.txt', 'w', encoding='utf-8') as f:
            f.write('your_secure_password_here')

    # Run the main function
    run_curl_requests()
