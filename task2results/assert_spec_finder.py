import ast
import csv
import os

class ApproximateAssertionVisitor(ast.NodeVisitor):
    """
    AST visitor that detects approximate assertions in Python test files.
    """

    def __init__(self, filename):
        self.filename = filename
        self.approx_assertions = []
        self.current_class = ''
        self.current_function = ''

    def visit_FunctionDef(self, node):
        """Visit function definitions and update the current function name."""
        self.current_function = node.name
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definitions and update the current class name."""
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = ''

    def visit_Assert(self, node):
        """Identify assertion statements that check approximate values."""
        if self.is_approximate_assertion(node.test):
            self.approx_assertions.append({
                'filepath': self.filename,
                'testclass': self.current_class,
                'testname': self.current_function,
                'assertion_type': 'assert_allclose',
                'line_number': node.lineno,
                'assert_string': ast.unparse(node)
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        """Identify function calls that are approximate assertions."""
        assertion_types = {
            'assert_allclose': 'assert_allclose',
            'assertAlmostEqual': 'assert_almost_equal',
            'assert_approx_equal': 'assert_approx_equal',
            'assert_array_almost_equal': 'assert_array_almost_equal',
            'assert_array_less': 'assert_array_less',
            'assertTrue': 'assert_true',
            'assertFalse': 'assert_false',
            'assertGreater': 'assert_greater',
            'assertGreaterEqual': 'assert_greater_equal',
            'assertLess': 'assert_less',
            'assertLessEqual': 'assert_less_equal',
            'assertAllClose': 'assert_allclose'
        }

        if isinstance(node.func, ast.Attribute) and node.func.attr in assertion_types:
            self.approx_assertions.append({
                'filepath': self.filename,
                'testclass': self.current_class,
                'testname': self.current_function,
                'assertion_type': assertion_types[node.func.attr],
                'line_number': node.lineno,
                'assert_string': ast.unparse(node)
            })
        
        self.generic_visit(node)

    def is_approximate_assertion(self, test):
        """Determines if an assertion involves approximate comparisons."""
        return (
            isinstance(test, ast.Call) and 
            isinstance(test.func, ast.Attribute) and 
            test.func.attr in {
                'allclose', 'assert_allclose', 'assertAlmostEqual',
                'assert_approx_equal', 'assert_array_almost_equal',
                'assert_array_less', 'assertAllClose'
            }
        )

def analyze_file(filepath):
    """Parses a Python file and extracts approximate assertions."""
    with open(filepath, 'r', encoding="utf-8") as file:
        source_code = file.read()

    if not source_code.strip():
        return []

    try:
        tree = ast.parse(source_code, filename=filepath)
        visitor = ApproximateAssertionVisitor(filepath)
        visitor.visit(tree)
        return visitor.approx_assertions
    except SyntaxError:
        return []

def get_test_files(root_dir):
    """Recursively finds all Python test files that contain 'test' in their filename."""
    test_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if "test" in file.lower() and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    return test_files

def write_to_csv(data, output_file):
    """Writes the extracted assertion data to a CSV file."""
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['filepath', 'testclass', 'testname', 'assertion_type', 'line_number', 'assert_string']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    project_name = 'sonnet'
    test_dir = os.path.join(project_name, 'src')
    output_csv = f"{project_name}_assertions.csv"

    if os.path.exists(test_dir):
        test_files = get_test_files(test_dir)

        if test_files:
            all_assertions = [assertion for test_file in test_files for assertion in analyze_file(test_file)]
            write_to_csv(all_assertions, output_csv)
    else:
        print(f"ERROR: Test directory {test_dir} not found!")
