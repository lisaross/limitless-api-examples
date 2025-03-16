import os
import requests
import tzlocal

def get_lifelogs(api_key, api_url=os.getenv("LIMITLESS_API_URL") or "https://api.limitless.ai", endpoint="v1/lifelogs", limit=50, batch_size=10, includeMarkdown=True, includeHeadings=False, date=None, timezone=None, direction="asc"):
    all_lifelogs = []
    cursor = None
    
    # If limit is None, fetch all available lifelogs
    # Otherwise, set a batch size (e.g., 10) and fetch until we reach the limit
    if limit is not None:
        batch_size = min(batch_size, limit)
    
    while True:
        params = {  
            "limit": batch_size,
            "includeMarkdown": "true" if includeMarkdown else "false",
            "includeHeadings": "false" if includeHeadings else "true",
            "date": date,
            "direction": direction,
            "timezone": timezone if timezone else str(tzlocal.get_localzone())
        }
        
        # Add cursor for pagination if we have one
        if cursor:
            params["cursor"] = cursor
            
        url = f"{api_url}/{endpoint}"
        print(f"\nMaking request to: {url}")
        print(f"With parameters: {params}")
            
        response = requests.get(
            url,
            headers={"X-API-Key": api_key},
            params=params,
        )

        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response body: {response.text}")

        if not response.ok:
            raise Exception(f"HTTP error! Status: {response.status_code}")

        data = response.json()
        print(f"Response data: {data}")
        
        lifelogs = data.get("data", {}).get("lifelogs", [])
        
        # Add transcripts from this batch
        for lifelog in lifelogs:
            all_lifelogs.append(lifelog)
        
        # Check if we've reached the requested limit
        if limit is not None and len(all_lifelogs) >= limit:
            return all_lifelogs[:limit]
        
        # Get the next cursor from the response
        next_cursor = data.get("meta", {}).get("lifelogs", {}).get("nextCursor")
        
        # If there's no next cursor or we got fewer results than requested, we're done
        if not next_cursor or len(lifelogs) < batch_size:
            break
            
        print(f"Fetched {len(lifelogs)} lifelogs, next cursor: {next_cursor}")
        cursor = next_cursor
    
    return all_lifelogs
