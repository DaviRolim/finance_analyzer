import pandas as pd
from financial_analyzer.dashboard import create_dashboard

def main():
    # Load the CSV file
    df = pd.read_csv('reports/reports.csv')
    
    # Print column names
    print("Columns in the DataFrame:", df.columns.tolist())
    
    # Convert date to datetime if 'date' column exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        print("Warning: 'date' column not found in the CSV file")
    
    # Create and run the dashboard
    create_dashboard(df)

if __name__ == "__main__":
    main()