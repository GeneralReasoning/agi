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

# Get questions, answers and reasoning traces for math word problems
client.get_data("math-word-problems")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
