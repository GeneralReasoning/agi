# AGI Client

A Python client library for interacting with the General Reasoning platform API.

## Installation

You can install the package using pip:

```bash
pip install agi
```

## Making API Calls

Obtain an API key from [the website](https://gr.inc). Then:

```python
import agi

client = agi.Client(api_key=YOUR_API_KEY)

# Download reasoning traces and verifications as a .jsonl
client.data.get(task='math-word-problems', model='DeepSeek-R1')
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
