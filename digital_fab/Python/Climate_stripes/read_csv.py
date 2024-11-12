# Initialize an empty list to hold the CSV data as floats
csv_data = []


with open('tr_data.csv', 'r') as file:
    
    for line in file:
        
        row = float( line.strip())
        
        csv_data.append(row)

