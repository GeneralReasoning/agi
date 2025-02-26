import os
import requests

from .consts import GR_API_URL


class Data:
    def __init__(self, client: 'Client'):
        self.client = client

    def get(self, task: str, model: str, save_as: str = None, download_dir: str = "gr_data") -> str:
        """
        Fetches the .jsonl file for a given task and saves it locally.

        Args:
            task (str): The task identifier to fetch data for.
            model (str): The model to gather reasoning traces for
            save_as (str, optional): Custom filename for the downloaded .jsonl file. 
                                        If not provided, defaults to '<task>.jsonl'.
            download_dir (str, optional): Directory to save downloaded files. Defaults to "gr_data".

        Returns:
            str: The path to the downloaded .jsonl file.
        """

        os.makedirs(download_dir, exist_ok=True)  # Create directory if it doesn't exist

        # Construct the API URL with the task parameter
        api_url = f"{GR_API_URL}{self.client.questions_endpoint}/?task={task}&model={model}"
        print(f"Requesting data from: {api_url}")

        try:
            # Make the GET request to fetch TaskData
            response = requests.get(api_url, headers=self.client.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the JSON response
            data = response.json()
            if not data:
                raise ValueError("No data found in the API response.")

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
            file_path = os.path.join(download_dir, filename)

            # Create download directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)

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


class Evals:
    def __init__(self, client: 'Client'):
        self.client = client

    def get(self, dataset: str = None, task: str = None, split: str = 'test', n: int = 10000, page: int = 1) -> dict:
        """
        Retrieve questions from a dataset or task.

        Args:
            dataset (str, optional): Name of the dataset (e.g. 'Hendryks/MATH')
            task (str, optional): Name of the task (e.g. 'mathematical-brainteasers')
            split (str): Which split to retrieve ('train' or 'test'). Defaults to 'test'.

        Returns:
            dict: Question data containing id, dataset/task, question text, system prompt, etc.

        Raises:
            ValueError: If neither dataset nor task is provided
        """
        if not dataset and not task:
            raise ValueError("Must provide either dataset or task")

        params = {'split': split, 'n': n, 'page': page}
        if dataset:
            params['dataset'] = dataset
        if task:
            params['task'] = task

        response = requests.get(
            f"{GR_API_URL}evaluation/questions",
            headers=self.client.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_tasks(self) -> list:
        """
        Get a list of all tasks available for evaluation.
        """
        response = requests.get(
            f"{GR_API_URL}evaluation/tasks",
            headers=self.client.headers
        )
        response.raise_for_status()
        return response.json()
    
    def submit(self, question_id: str, model: str, reasoning_trace: str, answer: str, overwrite: bool = False) -> dict:
        """
        Submit a single response.
        """
        payload = {
            "model": model,
            "overwrite": overwrite,
            "responses": [{
                "question_id": question_id,
                "reasoning_trace": reasoning_trace,
                "answer": answer,
            }]
        }
        url = f"{GR_API_URL}evaluation/submissions/"
        response = requests.post(url, headers=self.client.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def submit_batch(self, responses: list, model: str, overwrite: bool = False) -> dict:
        """
        Submit a batch of responses.
        Each item in responses should be a dict with keys: question_id, reasoning_content, and answer_content.
        """
        payload = {
            "model": model,
            "responses": responses,
            "overwrite": overwrite
        }
        url = f"{GR_API_URL}evaluation/submissions/"
        response = requests.post(url, headers=self.client.headers, json=payload)
        response.raise_for_status()
        return response.json()


class Client:
    questions_endpoint = "get_data/task-data"

    def __init__(self, api_key: str):
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
        self.data = Data(self)
        self.evals = Evals(self)
