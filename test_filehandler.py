from pathlib import Path
from src.file_handler import FileHandler

# Create a handler pointing at the uploads folder
handler = FileHandler("uploads")

# Create a dummy text file to test with
sample = Path("uploads/sample.txt")
sample.write_text("John Doe\nSoftware Engineer\nPython, Flask, SQL")

# Test is_allowed
print(handler.is_allowed("resume.pdf"))   # True
print(handler.is_allowed("resume.docx"))  # False

# Test extract_text
text = handler.extract_text(sample)
print(text)  # John Doe\nSoftware Engineer\n...

# Test cleanup
handler.cleanup(sample)
print(sample.exists())  # False — file is deleted