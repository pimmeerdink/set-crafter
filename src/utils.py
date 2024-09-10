import requests
from bs4 import BeautifulSoup
import json
import logging
import demjson3


def get_json_from_html(url, debugging=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    if debugging:
        logging.basicConfig(level=logging.DEBUG)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return None

    try:
        soup = BeautifulSoup(response.text, "lxml")
    except:
        soup = BeautifulSoup(response.text, "html.parser")

    if debugging:
        logging.debug("Extracting JSON from HTML...")

    json_data = []

    # Get pagedata
    pagedata = soup.find("div", {"id": "pagedata"})
    if pagedata and "data-blob" in pagedata.attrs:
        json_data.append(pagedata["data-blob"])

    # Get application/ld+json script
    ld_json_script = soup.find("script", {"type": "application/ld+json"})
    if ld_json_script:
        json_data.append(ld_json_script.string)

    # Get data-tralbum scripts
    for script in soup.find_all("script"):
        if script.has_attr("data-tralbum"):
            json_data.append(script["data-tralbum"])

    # Convert all found data to JSON
    page_json = {}
    for data in json_data:
        try:
            # Use demjson3 to handle potential JS objects
            decoded_js = demjson3.decode(data)
            encoded_json = demjson3.encode(decoded_js)
            page_json.update(json.loads(encoded_json))
        except Exception as e:
            if debugging:
                logging.warning(f"Failed to parse JSON: {str(e)}")

    if debugging:
        logging.debug("JSON extraction complete.")

    return page_json


# Example usage
if __name__ == "__main__":
    url = "https://holdinghandsrecords.bandcamp.com/track/noise-protocol"
    result = get_json_from_html(url, debugging=True)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No JSON data found or error occurred.")
