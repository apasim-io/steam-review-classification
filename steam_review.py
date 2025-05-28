import steamreviews
import pandas as pd
import time

# List of App IDs for the games you're interested in
# Example: [CS2, Dota 2, Team Fortress 2]
'''
Games searched: 
- Nine Sols, Star Wars Jedi: Survivor, Elden Ring, Dark Souls: Prepare to Die Edition,
- Dark Souls II, Dark Souls III, Star Wars Jedi: Fallen Order, Hollow Knight, Black Myth: Wukong,
- Blasphemous, Blasphemous 2, Lies of P, Sekiro: Shadows Die Twice
'''
APP_IDS = [1809540, 1774580, 1245620, 211420, 236430, 374320, 1172380,
            367520, 1369630, 774361, 2114740, 1627720, 814380] 

# Request parameters for fetching reviews
request_params = {
    'language': 'english', # Fetch only English reviews
    'filter': 'all',       # Default filter, library handles pagination
    'review_type': 'all',  # Positive and negative reviews
    'purchase_type': 'all',# Steam and non-Steam purchases
    'num_per_page': '100', # Max reviews per API request
    # 'filter_offtopic_activity': '0' # Uncomment to include off-topic reviews
}

# List to store all reviews from all games
all_reviews_list = []
total_reviews_downloaded_overall = 0

print(f"Starting review download for App IDs: {APP_IDS}")

# Loop through each App ID
for app_id in APP_IDS:
    print(f"\n--- Processing App ID: {app_id} ---")
    try:
        # Download reviews for the current App ID
        review_dict, query_count = steamreviews.download_reviews_for_app_id(
            app_id=app_id,
            chosen_request_params=request_params
        )

        # Extract the actual reviews dictionary for the current game
        # 'reviews' key contains a dict: {recommendationid: review_data}
        reviews = review_dict.get('reviews') if review_dict else None

        if reviews:
            num_reviews_game = len(reviews)
            total_reviews_downloaded_overall += num_reviews_game
            print(f"Successfully downloaded {num_reviews_game} English reviews for App ID {app_id} after {query_count} API queries.")

            # Add app_id and recommendationid to each review, then append to the master list
            for rec_id, review_data in reviews.items():
                review_data['app_id'] = app_id          # Add current App ID
                review_data['recommendationid'] = rec_id      # Ensure recommendationid is a field
                all_reviews_list.append(review_data)
        else:
            print(f"No English reviews were downloaded for App ID {app_id}.")
            if review_dict and 'query_summary' in review_dict:
                print(f"Query Summary for App ID {app_id}: {review_dict.get('query_summary')}")
    
    except Exception as e:
        print(f"An error occurred while processing App ID {app_id}: {e}")
    
    # Optional: Add a small delay between processing different App IDs to be respectful to the API
    if len(APP_IDS) > 1 and app_id != APP_IDS[-1]: # if not the last app_id
        time.sleep(5) # 5-second delay

# After processing all App IDs, create the master DataFrame
if all_reviews_list:
    print(f"\n--- Consolidating all {total_reviews_downloaded_overall} reviews into a DataFrame ---")
    master_df = pd.DataFrame(all_reviews_list)

    # Set 'app_id' and 'recommendationid' as a MultiIndex
    # This addresses "store the games app id as an index as well"
    if 'app_id' in master_df.columns and 'recommendationid' in master_df.columns:
        master_df.set_index(['app_id', 'recommendationid'], inplace=True)
    else:
        print("Warning: 'app_id' or 'recommendationid' column missing, cannot set MultiIndex.")


    # Flatten the 'author' column (which contains dictionaries)
    if 'author' in master_df.columns:
        try:
            # Ensure 'author' column contains dicts, replace non-dicts (e.g. NaN) with empty dict
            author_series = master_df['author'].apply(lambda x: x if isinstance(x, dict) else {})
            author_df = pd.json_normalize(author_series)
            author_df = author_df.add_prefix('author.') # Add prefix to avoid column name conflicts
            
            master_df = master_df.drop(columns=['author']) # Drop original 'author' column
            master_df = pd.concat([master_df, author_df], axis=1) # Concatenate new author columns
        except Exception as e_author:
            print(f"Error processing 'author' column: {e_author}")

    # Convert Unix timestamps to human-readable datetime objects
    timestamp_columns = [
        'timestamp_created', 
        'timestamp_updated', 
        'timestamp_dev_responded', # Might not always be present
        'author.last_played'      # From flattened author data
    ]
    for col in timestamp_columns:
        if col in master_df.columns:
            try:
                # Convert to datetime; 'coerce' will turn errors (e.g., 0 or missing) into NaT (Not a Time)
                master_df[col] = pd.to_datetime(master_df[col], unit='s', errors='coerce')
            except Exception as e_time:
                 print(f"Error converting timestamp column '{col}': {e_time}")

    # Define the name for the single Excel file
    excel_filename = "all_steam_game_reviews_english.xlsx"
    
    try:
        # Save the master DataFrame to the Excel file
        # The MultiIndex (app_id, recommendationid) will be written
        master_df.to_excel(excel_filename, index=True) 
        print(f"\nAll {total_reviews_downloaded_overall} English reviews successfully saved to {excel_filename}")
    except Exception as e_excel:
        print(f"Error saving to Excel: {e_excel}")
        print("Please ensure you have the 'openpyxl' library installed (pip install openpyxl).")
else:
    print("\nNo reviews were downloaded")

