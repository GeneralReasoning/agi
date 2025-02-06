from .consts import GR_API_URL
import requests
import os

class Client:
    questions_endpoint = "get_data/task-data"

    def __init__(self, api_key: str, download_dir: str = "gr_data"):
        """
        Client for interacting with the AGI API to fetch and download .jsonl files for a specific task.

        Args:
            api_key (str): Authentication key for accessing the API endpoints.
            download_dir (str): Local directory to save downloaded .jsonl files.
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)  # Create directory if it doesn't exist

    def get_data(self, task: str, save_as: str = None) -> str:
        """
        Fetches the .jsonl file for a given task and saves it locally.

        Args:
            task (str): The task identifier to fetch data for.
            save_as (str, optional): Custom filename for the downloaded .jsonl file. 
                                     If not provided, defaults to '<task>.jsonl'.

        Returns:
            str: The path to the downloaded .jsonl file.
        """
        # Construct the API URL with the task parameter
        api_url = f"{GR_API_URL}{self.questions_endpoint}/?task={task}"
        print(f"Requesting data from: {api_url}")

        try:
            # Make the GET request to fetch TaskData
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the JSON response
            data = response.json()
            if not data:
                raise ValueError("No 'download_url' found in the API response.")

            # Extract the download_url from the response
            download_url = data[0].get('download_url')
            if not download_url:
                raise ValueError("No 'download_url' found in the API response.")

            print(f"Download URL found: {download_url}")

            # Make a GET request to the download_url to fetch the .jsonl file
            download_response = requests.get(download_url, stream=True)
            download_response.raise_for_status()

            # Determine the filename
            if not save_as:
                # Attempt to extract the filename from the download URL
                filename = os.path.basename(download_url.split("?")[0])  # Remove query params
                if not filename.endswith('.jsonl'):
                    filename += '.jsonl'
            else:
                filename = save_as

            # Define the full path to save the file
            file_path = os.path.join(self.download_dir, filename)

            # Write the content to the file in chunks to handle large files
            with open(file_path, 'wb') as f:
                for chunk in download_response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)

            print(f"Downloaded .jsonl file saved to: {file_path}")
            return file_path

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - {response.text}")
            raise
        except Exception as err:
            print(f"An error occurred: {err}")
            raise
