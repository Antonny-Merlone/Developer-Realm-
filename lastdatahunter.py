import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# 1. Start a session to maintain cookies and headers
session = requests.Session()

# 2. URL of the page where the CSRF token is located
login_url = "https://portal.sha.go.ke/edi/claims?claims_workflow_state=SUBMITTED"

# 3. Initial GET request to fetch the CSRF token
response = session.get(login_url)

# Check if the GET request was successful
if response.status_code == 200:
    print("Successfully fetched the page.")

    # Parse the HTML to extract the CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')

    # Example of extracting CSRF token (assume it's in a hidden input field)
    csrf_token = soup.find('input', {'name': 'csrf_token'})['']
    print("Extracted CSRF Token:", csrf_token)
else:
    print("Failed to fetch the login page.")

# 4. Set up the headers for the POST request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",  # Some websites expect this header
    "Origin": "https://portal.sha.go.ke",  # Some websites check the origin
    "Referer": login_url,  # Include the referer header (optional but often necessary)
    "Access-Control-Allow-Origin": "*",  # Allow CORS if necessary
}

# 5. The data to send in the POST request, including the CSRF token
post_data = {
    'username': 'joccytanui@gmail.com',
    'password': 'Tanui@2024',
    'csrf_token': csrf_token,  # Include the CSRF token in the data
}

# 6. Send the POST request to log in
post_url = "https://accounts.provider.sha.go.ke/login/"
login_response = session.post(post_url, data=post_data, headers=headers)

# Check if the login was successful
if login_response.status_code == 200:
    print("Successfully logged in!")
    # Now, you can continue scraping or accessing protected resources
else:
    print(f"Failed to log in. Status code: {login_response.status_code}")


def get_sha_data(base_url):
    all_data = []

    # Calculate the date range for the past three months
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)

    # Loop through each month to get data
    for month_offset in range(3):
        month_date = start_date + timedelta(days=month_offset * 30)  # Adjust days based on months
        formatted_date = month_date.strftime('%Y-%m-%d')

        # Send a GET request to fetch the page for the specified date
        response = requests.get(f"{base_url}?date={formatted_date}")
        
        if response.status_code != 200:
            print(f"Failed to retrieve data for {formatted_date}")
            continue

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the rows in the table that contain the data (adjust tag and class as per your target website)
        rows = soup.find_all('tr', class_='data-row')  # Modify based on actual website structure

        for row in rows:
            try:
                # Extract name, amount, and date (adjust selectors according to actual HTML structure)
                name = row.find('td', class_='name').text.strip()
                amount = row.find('td', class_='amount').text.strip()
                date = row.find('td', class_='date').text.strip()

                # Store the data
                all_data.append({
                    'Date': date,
                    'Name': name,
                    'Amount': amount
                })
            except AttributeError:
                # Handle rows that might not contain all the fields or are empty
                continue

    return all_data

def save_to_excel(data, filename):
    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Save DataFrame to an Excel file
    df.to_excel(filename, index=False, engine='openpyxl')

def main():
    # The base URL where the data can be accessed
    base_url = "https://portal.sha.go.ke/edi/claims?claims_workflow_state=SUBMITTED"  # Replace with the actual URL of the SHA website
    data = get_sha_data(base_url)

    # Save the scraped data to an Excel file
    save_to_excel(data, 'sha_health_data.xlsx')
    print("Data successfully saved to sha_health_data.xlsx")

# Run the script
if __name__ == "__main__":
    main()