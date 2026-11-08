from pathlib import Path

from ui_state import main


def test_read_file():
    file_path = Path("test/test_file.txt")
    expected_content = "This is a test file.\nIt has multiple lines.\n"

    # Create a test file with the expected content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(expected_content)

    # Read the file using the _read_file function
    actual_content = main.read_file(file_path)

    # Assert that the content read from the file matches the expected content
    assert actual_content == expected_content


def test_regex_match():
    string = "Hello, this is a test string."
    pattern = r"test"
    expected_result = ("test", 17)

    # Use the regex_match function to find the pattern in the string
    actual_result = main.regex_match(pattern, string)

    # Assert that the result matches the expected result
    assert actual_result == expected_result


def test_find_func_definition():
    file_content = """
static ULONG my_function_foo(int a, int b) {
    // function body
}

static ULONG my_function(int a, int b) {
    // function body
}
"""

    func_name = "my_function"
    expected_result = (
        "static ULONG my_function(int a, int b) {\n    // function body\n}\n",
        70,
    )

    # Use the find_func_definition function to find the function definition in the file content
    actual_result = main.find_func_definition(file_content, func_name)

    assert actual_result is not None, "Function definition not found"

    print(f"Expected: \n{expected_result[0]}--\n, Actual: \n{actual_result[0]}--\n")
    # Assert that the result matches the expected result
    assert actual_result[0] == expected_result[0]
