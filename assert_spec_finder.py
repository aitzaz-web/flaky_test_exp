import ast
import csv
import os

class ApproximateAssertionVisitor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.approx_assertions = []

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.generic_visit(node)

    def visit_Assert(self, node):
        if self.is_approximate_assertion(node.test):
            self.approx_assertions.append({
                'filepath': self.filename,
                'testclass': getattr(self, 'current_class', ''),
                'testname': getattr(self, 'current_function', ''),
                'assertion_type': 'assert_allclose',
                'line_number': node.lineno,
                'assert_string': ast.unparse(node)
            })
        self.generic_visit(node)
    
    def visit_Call(self, node):
        assertion_types = {
            'allclose': 'assert_allclose',
            'assert_allclose': 'assert_allclose',
            'assertAlmostEqual': 'assert_almost_equal',
            'assert_approx_equal': 'assert_approx_equal',
            'assert_array_almost_equal': 'assert_array_almost_equal',
            'assert_array_less': 'assert_array_less',
            'assertTrue': 'assertTrue',
            'assertFalse': 'assertFalse',
            'assertGreater': 'assertGreater',
            'assertGreaterEqual': 'assertGreaterEqual',
            'assertLess': 'assertLess',
            'assertLessEqual': 'assertLessEqual',
            'assertAllClose': 'assertAllClose',
            'assert expr < | > | <= | >= threshold': 'assert_comparison'
        }

        if isinstance(node.func, ast.Attribute) and node.func.attr in assertion_types:
            self.approx_assertions.append({
                'filepath': self.filename,
                'testclass': getattr(self, 'current_class', ''),
                'testname': getattr(self, 'current_function', ''),
                'assertion_type': assertion_types[node.func.attr],
                'line_number': node.lineno,
                'assert_string': ast.unparse(node)
            })
        
        self.generic_visit(node)
        

    

        
    def is_approximate_assertion(self, test):
        return (isinstance(test, ast.Call) and 
                isinstance(test.func, ast.Attribute) and 
                test.func.attr in {'allclose', 'assert_allclose', 'assertAlmostEqual', 'assert_approx_equal', 
                                   'assert_array_almost_equal', 'assert_array_less', 'assertAllClose'})

def analyze_file(filepath):
    print(f"DEBUG: Analyzing file: {filepath}") 

    with open(filepath, 'r', encoding="utf-8") as file:
        source_code = file.read()

    if not source_code.strip():
        print(f"ERROR: {filepath} is empty or not readable")
        return []

    print(f"DEBUG: Source code length = {len(source_code)} characters") 

    try:
        tree = ast.parse(source_code, filename=filepath)
        print(f"DEBUG: Successfully parsed {filepath}")  

        visitor = ApproximateAssertionVisitor(filepath)
        visitor.visit(tree)  
        return visitor.approx_assertions
    except SyntaxError as e:
        print(f"Syntax error while parsing {filepath}: {e}")
        return []



def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['filepath', 'testclass', 'testname', 'assertion_type', 'line_number', 'assert_string']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

import os

if __name__ == "__main__":
    project_name = 'allennlp'
    test_file = os.path.join('allennlp', 'tests', 'modules', 'elmo_test.py') 
    output_csv = f"{project_name}_assertions.csv"

    # Confirm the script is running on the correct file
    print(f"DEBUG: Checking file {test_file}")

    if not os.path.exists(test_file):
        print(f"ERROR: File {test_file} not found!")
    else:
        all_assertions = analyze_file(test_file)  
        write_to_csv(all_assertions, output_csv)
        print(f"Analysis complete. Results saved to {output_csv}")

