import json
import sys

def compare_and_update_json(file1, file2):
    # Read the contents of both JSON files
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # Check if first file already contains data from second file
    if contains_data(data1, data2):
        print("The first JSON file already contains the data from the second JSON file. No update required.")
        return

    # Update the first JSON object with the missing objects from the second object
    updated_data = update_json(data1, data2)

    # Write the updated JSON object back to the first file
    with open(file1, 'w') as f1:
        json.dump(updated_data, f1, indent=4)
    print("Updated the first JSON file with extra information.")

def contains_data(obj1, obj2):
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        for key, value in obj2.items():
            if key not in obj1 or not contains_data(obj1[key], value):
                return False
        return True
    elif isinstance(obj1, list) and isinstance(obj2, list):
        return all(any(contains_data(obj1_item, obj2_item) for obj1_item in obj1) for obj2_item in obj2)
    else:
        return obj1 == obj2

def update_json(obj1, obj2):
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        updated_obj = obj1.copy()
        for key, value in obj2.items():
            if key not in updated_obj:
                updated_obj[key] = value
            else:
                updated_obj[key] = update_json(updated_obj[key], value)
        return updated_obj
    elif isinstance(obj1, list) and isinstance(obj2, list):
        for item in obj2:
            if item not in obj1:
                obj1.append(item)
        return obj1
    else:
        return obj2


# Provide the paths to the JSON files
# file1 = 'json/ES_9_log_copy_2.json'
# file2 = 'json/ES_9_log_copy.json'

file1 = sys.argv[1]
file2 = sys.argv[2]

# Call the function to compare and update the JSON files
compare_and_update_json(file1, file2)