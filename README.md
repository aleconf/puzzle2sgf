# puzzle2sgf
A simple python script to export OGS (online-go.com) puzzles as sgf files.
Tested somewhat with Python 3.8. Fails if the collection/puzzle name is not a valid folder/file name.
The puzzle or collection to be downloaded can be specified at the top of the script.

# Changelog for this forked repository

### The 2nd of October 2025.
- Added file `requirements.txt`.
- If the collection/puzzle name is not a valid folder/file name, it gets modified into a unique name, so now the script works even in this case. Tested with [puzzle 15904](https://online-go.com/puzzle/15904).
- All input data are now inserted at runtime and not hard-coded in the Python source file.
- The authentication section has not been tested in this forked repository.
