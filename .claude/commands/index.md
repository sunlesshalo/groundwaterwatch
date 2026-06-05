Generate a structural index for a markdown file for section-by-section reading.

## Steps

1. Get the file path from $ARGUMENTS. If not provided, ask the user.

2. Extract all headings from the `.md` file using Bash:
   ```
   grep -n "^#" <file_path>
   ```

3. Display the index in this format:
   ```
   L{line_number}  {heading text}
   ```

4. Tell the user how to read sections:
   > Use Read with `offset` and `limit` to fetch sections by line number.
