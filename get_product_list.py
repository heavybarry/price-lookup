import csv
import os

def read_columns_by_name_skip_empty(file_path, column1_name, column2_name):
    """
    Reads two specified columns from a CSV file by their names,
    skipping rows where the second column is empty.

    Args:
        file_path (str): The path to the CSV file.
        column1_name (str): The name of the first column.
        column2_name (str): The name of the second column.
    """

    data = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the column names exist
            if column1_name not in reader.fieldnames or column2_name not in reader.fieldnames:
                raise ValueError(f"Column name(s) not found: {column1_name}, {column2_name}")

            for row in reader:
                stripped_value = row[column2_name].strip()
                # Check if the second column is empty (or contains only whitespace)
                if stripped_value and stripped_value.isdigit():
                    data.append((row[column1_name], row[column2_name]))

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
    except ValueError as e:
        print(f"Error: {e}")

    return data

def read_filenames(folder_path):
    """
    Reads and returns a list of all filenames in a specified folder.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        list: A list of filenames (excluding directories) in the folder.
        If the folder is empty, returns an empty list.
        If the folder does not exist, returns None.
    """
    filenames = []
    try:
        for entry in os.scandir(folder_path):  # Efficiently scan the directory
            if entry.is_file():               # Check if it's a file (not a directory)
                filenames.append(entry.name)  # Append the filename to the list
        return filenames
    except FileNotFoundError:
        print(f"Error: Folder '{folder_path}' not found.")
        return None
    except PermissionError:
        print(f"Error: Permission denied to access '{folder_path}'.")
        return None
    except OSError as e:
        print(f"Error reading folder: {e}")
        return None
    
def read_csv_data_from_folder(folder_path, column1_name, column2_name):
    """
    Reads specified columns from CSV files in a folder.

    Args:
        folder_path (str): The path to the folder containing CSV files.
        column1_name (str): The name of the first column to read.
        column2_name (str): The name of the second column to read.
    """

    all_data = {}  # Dictionary to store data from each file

    filenames = read_filenames(folder_path)
    if filenames is not None:
        for filename in filenames:
            if filename.lower().endswith('.csv'):  # Process only CSV files
                file_path = os.path.join(folder_path, filename)
                
                data = read_columns_by_name_skip_empty(file_path, column1_name, column2_name)
                if data:  # Only store if data was found
                    all_data[filename] = data

    return all_data

# Mainline

PREFERRED_ZIPCODE = "92024"
MAX_REQUESTS_PER_SHEET = 5   # Small value for testing. Normally very large, e.g., 99999

folder_path = 'tests/data'  # Replace with your actual folder path
column1_name = 'Total'  # Replace with the actual column name
column2_name = 'ProdID'    # Replace with the actual column name

new_header = ["type", "url", "page", "max_page", "item_id", "gtin", "sort_by", "search_term", "category_id", "customer_zipcode", "min_price", "max_price", "reviewer_type", "five_star", "four_star", "three_star", "two_star"]

all_csv_data = read_csv_data_from_folder(folder_path, column1_name, column2_name)

if all_csv_data:
    output_filename = 'combined_data_just5per.csv'
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_header)
        writer.writeheader()

        for filename, data in all_csv_data.items():
            count = 0
            for item_name, item_id in data:
                writer.writerow({
                    "type": "product",
                    "item_id": item_id,
                    "customer_zipcode": PREFERRED_ZIPCODE
                })  # Fill only item_id for now
                print(f"  {filename}: Total={item_name}, ProdID={item_id}")  # Display to console
                count += 1
                if (count >= MAX_REQUESTS_PER_SHEET):
                    break

    print(f"CSV output saved to: {output_filename}")