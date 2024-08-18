import pandas as pd
import json
import os

def analyze_report(df: pd.DataFrame, selected_months: list = None) -> dict:
    """
    Analyze the financial report and return a dictionary of results.
    """
    print(f"Input DataFrame shape: {df.shape}")
    print(f"Selected months: {selected_months}")

    # Check if 'date' column exists
    if 'date' not in df.columns:
        print("Warning: 'date' column not found in the DataFrame")
        df['date'] = pd.to_datetime('today')  # Use today's date as a fallback
    else:
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])

    # Filter by selected months if provided
    if selected_months:
        df = df[df['date'].dt.strftime('%Y-%m').isin(selected_months)]

    print(f"Filtered DataFrame shape: {df.shape}")

    # Group by month end and category, then sum the amounts
    monthly_category_totals = df.groupby([df['date'].dt.to_period('M'), 'category'])['amount'].sum().reset_index()
    monthly_category_totals['date'] = monthly_category_totals['date'].dt.strftime('%Y-%m')

    # Calculate total amount by category
    category_totals = df.groupby('category')['amount'].sum().reset_index()

    # Get top 5 most expensive items for each month
    top_5_items_by_month = df.groupby(df['date'].dt.to_period('M')).apply(
        lambda x: x.nlargest(5, 'amount')[['title', 'amount']].to_dict('records')
    ).to_dict()

    results = {
        'total_amount': df['amount'].sum(),
        'monthly_category_totals': monthly_category_totals.to_dict('records'),
        'category_totals': category_totals.to_dict('records'),
        'top_5_items_by_month': top_5_items_by_month,
    }

    print(f"Analysis results: {results}")
    return results

def save_dashboard_config(config: dict):
    """
    Save the dashboard configuration to a JSON file.
    """
    with open('dashboard_config.json', 'w') as f:
        json.dump(config, f)

def load_dashboard_config() -> dict:
    """
    Load the dashboard configuration from a JSON file.
    """
    if os.path.exists('dashboard_config.json'):
        with open('dashboard_config.json', 'r') as f:
            return json.load(f)
    return {}
