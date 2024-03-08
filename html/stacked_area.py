import json
import argparse
import csv
import os

def create_stacked_area_chart(input_csv):
    
    if not os.path.isfile(input_csv):
        print(f"Error: Input CSV file '{input_csv}' not found")
        return

    # Read data from the input CSV file and transform it
    data = []
    with open(input_csv, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(dict(row))
     
    # Write data to a JSON file
    with open("data.json", "w") as json_file:
        json.dump(data, json_file)

    print("Stacked area chart data saved to data.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a stacked area chart using D3.js")
    parser.add_argument("--input-csv", required=True, help="Path to input CSV file")
    args = parser.parse_args()

    if not os.path.isfile(args.input_csv):
        print(f"Error: Input CSV file '{args.input_csv}' not found")
    else:
        create_stacked_area_chart(args.input_csv)
