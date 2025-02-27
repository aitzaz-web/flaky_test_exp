import os
import pandas as pd
import random
import subprocess
import time
from task3results.static_instrumentation import instrument_test_file

def run_test_multiple_times(instrumented_file, test_name, iterations=10):
    """
    Executes the specified test multiple times using pytest and captures logs.
    Log files are stored in the same directory as this script.
    
    Parameters:
    - instrumented_file (str): Path to the instrumented test file.
    - test_name (str): Name of the test function to execute.
    - iterations (int): Number of times to execute the test (default is 10).
    """
    log_file = os.path.join(os.getcwd(), f"test_logs_{test_name}.txt")

    with open(log_file, "w") as log:
        for i in range(iterations):
            print(f"Executing test {test_name} - Iteration {i+1}/{iterations}")
            
            result = subprocess.run(
                ["pytest", instrumented_file, "-k", test_name, "-s"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            log.write(f"Iteration {i+1}:
")
            log.write(result.stdout)
            log.write(result.stderr)
            log.write("\n" + "=" * 80 + "\n")

            time.sleep(0.1)  # Introduce a slight delay between test runs

    print(f"Test execution completed. Logs have been saved to {log_file}.")

def select_random_assertions(csv_file, num_assertions=10):
    """
    Selects a random subset of assertions from the specified CSV file.
    
    Parameters:
    - csv_file (str): Path to the CSV file containing assertion data.
    - num_assertions (int): Number of assertions to select (default is 10).
    
    Returns:
    - pandas.DataFrame: A DataFrame containing the randomly selected assertions.
    """
    df = pd.read_csv(csv_file)
    num_assertions = min(num_assertions, len(df))
    return df.sample(n=num_assertions, random_state=42)

def process_assertions(csv_file):
    """
    Processes assertions from the specified CSV file, instruments the corresponding test files,
    and executes the instrumented tests.
    
    Parameters:
    - csv_file (str): Path to the CSV file containing assertion data.
    """
    selected_assertions = select_random_assertions(csv_file)

    for assertion in selected_assertions.to_dict(orient="records"):
        raw_file_path = assertion["filepath"]
        test_name = assertion["testname"]
        assertion_line = assertion["line_number"]

        if not os.path.exists(raw_file_path):
            print(f"Error: Test file {raw_file_path} not found. Skipping this test.")
            continue
        else:
            print(f"Test file located: {raw_file_path}")

        instrumented_file_path = os.path.join(
            os.path.dirname(raw_file_path),
            f"instrumented_{os.path.basename(raw_file_path)}"
        )

        instrument_test_file(raw_file_path, test_name, assertion_line, output_file=instrumented_file_path)
        run_test_multiple_times(instrumented_file_path, test_name)

if __name__ == "__main__":
    csv_file = "task2results/allennlp_assertions.csv"
    process_assertions(csv_file)
