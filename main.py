import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time
import datetime

# Load environment variables from .env file
load_dotenv()

# Get credentials from .env file
client_id = os.getenv('STRAVA_CLIENT_ID')
client_secret = os.getenv('STRAVA_CLIENT_SECRET')
refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')

def get_access_token():
    """Get a fresh access token using the refresh token"""
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(auth_url, data=payload)
    response_data = response.json()
    
    return response_data['access_token']

def get_all_activities(access_token):
    """Get all activities from Strava API by paginating through results"""
    all_activities = []
    page = 1
    per_page = 100  # Maximum allowed by Strava API
    
    while page < 2:
        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'per_page': per_page, 'page': page}
        
        response = requests.get(activities_url, headers=headers, params=params)
        activities_page = response.json()
        
        # If we get an empty page, we've reached the end
        if not activities_page:
            break
            
        all_activities.extend(activities_page)
        print(f"Retrieved page {page} with {len(activities_page)} activities")
        
        # Strava API has rate limits, so let's be nice and add a small delay
        time.sleep(0.2)
        
        # Move to the next page
        page += 1
    
    print(f"Total activities retrieved: {len(all_activities)}")
    return all_activities

def seconds_to_hms(total_seconds):
    return str(datetime.timedelta(seconds=total_seconds))

def clean_dataframe(df):
    # 1. Select columns
    df = df[['id', 'start_date_local', 'distance', 'moving_time', 'start_latlng', 'average_speed', 'max_speed', 'type']]

    # 2. Renaming columns
    df = df.rename(columns={'moving_time': 'moving_time_seconds'})

    # 3. Clean columns
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])

    # 4. Nieuwe kolommen
    df['moving_time'] = df['moving_time_seconds'].apply(seconds_to_hms)
    df['distance_km'] = df['distance'] / 1000
    df['start_date'] = df['start_date_local'].dt.date
    df['start_time'] = df['start_date_local'].dt.strftime('%H:%M')
    df['average_speed_kmh'] = df['average_speed'] * 3.6
    df['max_speed_kmh'] = df['max_speed'] * 3.6
    

    return df

# Get access token
access_token = get_access_token()

# Get all activities
all_activities = get_all_activities(access_token)

# Convert to DataFrame
df = pd.DataFrame(all_activities)
clean_df = clean_dataframe(df)

# You can also save the DataFrame to a CSV file
clean_df.to_csv('output/strava_activities.csv', index=False, sep=";")