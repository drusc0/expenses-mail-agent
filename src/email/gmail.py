import os
import base64
import asyncio
from pprint import pprint

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List

from src.models.email_models import ChaseExpense


# Define the scopes (permissions) needed
SCOPES = [
       'https://www.googleapis.com/auth/gmail.readonly',
        # 'https://www.googleapis.com/auth/gmail.modify',
        ]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'  # We'll still use this to store/retrieve refresh token info


def authenticate_gmail_api():
    """Authenticates with the Gmail API, attempting to refresh if needed."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(os.path.dirname(__file__), TOKEN_FILE)):
        creds = Credentials.from_authorized_user_file(os.path.join(os.path.dirname(__file__), TOKEN_FILE), SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # print("Attempting to refresh the access token...")
            try:
                creds.refresh(Request())
                # print("Access token refreshed successfully.")
            except Exception as e:
                print(f"Error refreshing token: {e}. Re-authenticating.")
                creds = None  # Force re-authentication
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(os.path.dirname(__file__), CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(os.path.dirname(__file__), TOKEN_FILE), 'w') as token:
                token.write(creds.to_json())
                print(f"New token saved to {TOKEN_FILE}")
    return creds


def get_gmail_client():
    """Create a fresh Gmail API client instance."""
    creds = authenticate_gmail_api()
    if creds and creds.valid:
        try:
            # Create a new service instance with fresh HTTP connection
            service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
            return service
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Failed to authenticate with Gmail API")
        return None


def _search_emails_sync(service, query, max_results=None):
    """Search for emails with pagination support.
    
    Args:
        service: Gmail API service instance
        query: Search query string
        max_results: Maximum number of results to fetch (None = fetch all)
    """
    try:
        all_messages = []
        page_token = None
        
        while True:
            # Fetch up to 500 messages per page (API maximum)
            if max_results and len(all_messages) >= max_results:
                break
                
            results = service.users().messages().list(
                userId='me', 
                q=query,
                maxResults=min(500, max_results - len(all_messages)) if max_results else 500,
                pageToken=page_token
            ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                break
                
            all_messages.extend(messages)
            print(f"Fetched {len(messages)} emails (total: {len(all_messages)})")
            
            # Check if there are more pages
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        if not all_messages:
            print("No emails found.")
            return []
            
        print(f"Total emails found: {len(all_messages)}")
        return all_messages
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

async def search_emails(service, query, max_results=None):
    """Async wrapper for email search with pagination.
    
    Args:
        service: Gmail API service instance
        query: Search query string
        max_results: Maximum number of results to fetch (None = fetch all)
    """
    return await asyncio.to_thread(_search_emails_sync, service, query, max_results)


def _get_email_content_sync(message_id):
    """Get email content with a fresh service instance to avoid SSL issues."""
    try:
        # Create a fresh service instance for this request
        service = get_gmail_client()
        if not service:
            print(f"Failed to create Gmail client for message {message_id}")
            return None
        
        # Get the email content using the message ID
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        
        if msg['payload']['body']['data']:
            return base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        return None
    except Exception as e:
        print(f"Error fetching email content for message {message_id}: {e}")
        return None


async def get_email_content(message_id):
    """Async wrapper for getting email content."""
    return await asyncio.to_thread(_get_email_content_sync, message_id)


# delete_email function to move the email to trash
async def delete_email(service, message_id):
    try:
        await asyncio.to_thread(lambda : service.users().messages().trash(userId='me', id=message_id).execute())
        print(f"Email with ID {message_id} has been moved to trash.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Extract and parse the necessary details from the email
def parse_html_email(html_content: str) -> ChaseExpense:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # use pydantic to define the structure of the data we want to extract
    extracted_info = {
        'account': '',
        'date': '',
        'merchant': '',
        'amount': 0.0
    }

    # Search for table rows, and extract the desired fields
    rows = soup.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:  # Ensure the row has exactly two cells for key-value pairing
            label = cells[0].text.strip()
            value = cells[1].text.strip()
            if label.lower() in extracted_info:
                extracted_info[label.lower()] = value
    
    if extracted_info['amount']:
        # Remove the dollar sign and convert to float
        extracted_info['amount'] = float(extracted_info['amount'].replace('$', '').replace(',', ''))

    return ChaseExpense(**extracted_info)


async def get_chase_expenses(_=None) -> List[ChaseExpense]:
    """Fetch Chase expenses from Gmail."""
    # Initialize the Gmail client
    print("Authenticating with Gmail API...")
    service = get_gmail_client()
    if not service:
        print("Failed to authenticate with Gmail API")
        return []
    
    # Customize the search query for your emails
    print("Searching for emails...")
    query = 'from:no.reply.alerts@chase.com'
    emails = await search_emails(service, query)
    if not emails:
        print("No emails found.")
        return []
    
    print(f"Found {len(emails)} emails to process...")
    chase_expenses = []
    
    # Process emails with fresh connections and error handling
    contents = await asyncio.gather(*[get_email_content(email['id']) for email in emails], return_exceptions=True)
    
    for i, content in enumerate(contents):
        if isinstance(content, Exception):
            print(f"Error processing email {emails[i]['id']}: {content}")
            continue
        if content:
            try:
                info = parse_html_email(content)
                pprint(info)
                # Optionally, delete the email after processing
                # delete_email(service, emails[i]['id'])
                chase_expenses.append(info)
            except Exception as e:
                print(f"Error parsing email {emails[i]['id']}: {e}")
                continue

    print(f"Found {len(chase_expenses)} Chase expenses.")
    return chase_expenses

async def get_latest_unread_emails(_=None) -> List[str]:
    print("Authenticating with Gmail API...")
    service = get_gmail_client()
    if not service:
        print("Failed to authenticate with Gmail API")
        return []
    
    # Customize the search query for your emails
    print("Searching for emails...")
    # search for unread emails today
    query = 'newer_than:1d is:unread'
    emails = await search_emails(service, query)
    if not emails:
        print("No emails found.")
        return []
    
    processed_emails = []
    tasks = [get_email_content(email['id']) for email in emails]
    contents = await asyncio.gather(*tasks, return_exceptions=True)
    
    for content in contents:
        if isinstance(content, Exception):
            print(f"Error processing email: {content}")
            continue
        if content:
            try:
                processed_emails.append(parse_html_email(content))
            except Exception as e:
                print(f"Error parsing email: {e}")
                continue

    return processed_emails

if __name__ == "__main__":
    print("Fetching Chase expenses...")
    asyncio.run(get_chase_expenses())
