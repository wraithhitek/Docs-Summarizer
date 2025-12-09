# File Input Support

The Content Summarizer now supports reading content from files in addition to direct string input.

## Features

- **UTF-8 Encoding**: Files are read with proper UTF-8 encoding
- **Error Handling**: Clear error messages for file not found, permission denied, and encoding issues
- **Equivalence**: File input produces the same summary results as string input
- **Flexible Input**: Accepts both `Path` objects and string file paths

## Usage Examples

### Using the `summarize_file()` method

```python
from pathlib import Path
from src.summarizer import BedrockSummarizer
from src.config import Config

# Initialize the summarizer
config = Config.from_env()
summarizer = BedrockSummarizer(config)

# Summarize content from a file using Path object
result = summarizer.summarize_file(Path("example_article.txt"))
print(result.summary)

# Or using a string path
result = summarizer.summarize_file("example_article.txt")
print(result.summary)
```

### Using the `summarize()` method with file content

```python
# Read the file content yourself and pass it to summarize()
with open("example_article.txt", "r", encoding="utf-8") as f:
    content = f.read()

result = summarizer.summarize(content)
print(result.summary)
```

## Error Handling

The file input functionality provides clear error messages for common issues:

```python
from src.summarizer import FileReadError

try:
    result = summarizer.summarize_file("nonexistent.txt")
except FileReadError as e:
    print(f"Error: {e}")
    # Output: Error: File not found: nonexistent.txt. Please check the file path and try again.
```

### Possible Errors

- **FileNotFoundError**: File doesn't exist at the specified path
- **PermissionError**: Insufficient permissions to read the file
- **UnicodeDecodeError**: File is not encoded in UTF-8
- **IsADirectoryError**: Path points to a directory instead of a file

## Implementation Details

- Files are read with UTF-8 encoding by default
- Line endings are normalized during file reading (platform-specific)
- The `summarize_file()` method is a convenience wrapper around `summarize()`
- Both methods produce equivalent summary results for the same content

## Testing

The file input functionality is tested with property-based tests to ensure:
- File content and string content produce equivalent summaries
- Error handling works correctly for various failure scenarios
- UTF-8 encoding is properly handled
