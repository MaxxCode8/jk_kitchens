import os
import pandas as pd
import re
import math

BASE_PATH = '_jk_data/PRODUCTS'
ALGORITHMS_PATH = '_jk_data/ALGORITHMS.xlsx'
COST_DATA_PATH = '_jk_data/COST_DATA.xlsx'

def get_categories():
    """Return a list of all product categories."""
    return [category for category in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, category))]

def get_product_types(category):
    """Return a list of product types for a given category."""
    category_path = os.path.join(BASE_PATH, category)
    return [os.path.splitext(file)[0] for file in os.listdir(category_path) if file.endswith('.xlsx')]

def get_product_features(category, product_type):
    """Return a list of features for a given product type."""
    file_path = os.path.join(BASE_PATH, category, f"{product_type}.xlsx")
    df = pd.read_excel(file_path)
    return df['FEATURES'].dropna().unique().tolist()

def get_sub_features(category, product_type, feature):
    """Return a list of sub-features for a given feature."""
    file_path = os.path.join(BASE_PATH, category, f"{product_type}.xlsx")
    df = pd.read_excel(file_path)
    sub_features = df[df['FEATURES'] == feature]['SUB FEATURES'].dropna().unique().tolist()
    return sub_features if sub_features else ['']

def get_quantity_size_dimensions(category, product_type, feature, sub_feature=None):
    """Return the quantity/size/dimensions for a given feature and sub-feature."""
    file_path = os.path.join(BASE_PATH, category, f"{product_type}.xlsx")
    df = pd.read_excel(file_path)
    if sub_feature:
        filtered_df = df[(df['FEATURES'] == feature) & (df['SUB FEATURES'] == sub_feature)]
    else:
        filtered_df = df[(df['FEATURES'] == feature) & (df['SUB FEATURES'].isna())]
    
    if not filtered_df.empty:
        return filtered_df.iloc[0]['QTY / DIMENSIONS/SIZE']
    else:
        return "No matching data found."

def load_algorithms_data(file_path=ALGORITHMS_PATH):
    """Load and process the algorithms data."""
    df = pd.read_excel(file_path)
    df = df.dropna(how='all')
    df['SR NO'] = df['SR NO'].ffill()
    return df

def get_algorithm(sr_no):
    """Return the algorithm steps for a given SR NO."""
    algorithms_df = load_algorithms_data()
    return algorithms_df[algorithms_df['SR NO'] == sr_no]['ALGORITHMS'].tolist()

def load_cost_data(file_path=COST_DATA_PATH):
    """Load the cost data."""
    return pd.read_excel(file_path)

def get_cost(code_no):
    """Return the cost data for a given CODE NO."""
    cost_df = load_cost_data()
    cost_data = cost_df[cost_df['CODE NO'] == code_no].to_dict('records')
    return cost_data[0] if cost_data else None

def get_features(category, product_type):
    """Return a list of features for a given product type."""
    file_path = os.path.join(BASE_PATH, category, f"{product_type}.xlsx")
    df = pd.read_excel(file_path)
    return df['FEATURES'].dropna().unique().tolist()

def get_algorithm_codes(category, product_type, feature, sub_feature=None):
    """Return the algorithm codes (SS202 and SS304) for a given feature and sub-feature."""
    file_path = os.path.join(BASE_PATH, category, f"{product_type}.xlsx")
    df = pd.read_excel(file_path)
    if sub_feature:
        filtered_df = df[(df['FEATURES'] == feature) & (df['SUB FEATURES'] == sub_feature)]
    else:
        filtered_df = df[(df['FEATURES'] == feature) & (df['SUB FEATURES'].isna())]
    
    if not filtered_df.empty:
        ss202 = filtered_df.iloc[0]['ALGORITHMS SS202']
        ss304 = filtered_df.iloc[0]['ALGORITHMS SS304']
        
        # Check if algorithms are empty/NaN
        return {
            'SS202': ss202 if pd.notna(ss202) else None,
            'SS304': ss304 if pd.notna(ss304) else None
        }
    else:
        return None

def get_algorithm_steps(sr_no):
    """Return the algorithm steps for a given SR NO or formula of SR NOs."""
    if not sr_no or pd.isna(sr_no):
        return []
    
    algorithms_df = load_algorithms_data()
    
    # If sr_no contains '+', it's a formula
    if '+' in str(sr_no):
        all_steps = []
        # Split by '+' and strip whitespace
        sr_codes = [code.strip() for code in str(sr_no).split('+')]
        
        for code in sr_codes:
            # If code contains alternatives (separated by '/'), take the first one for now
            if '/' in code:
                code = code.split('/')[0].strip()
            
            # Get steps for this code
            steps = algorithms_df[algorithms_df['SR NO'] == code]['ALGORITHMS'].dropna().tolist()
            # Remove any empty strings or whitespace-only strings
            steps = [step for step in steps if step.strip()]
            all_steps.extend(steps)
        
        return all_steps
    else:
        # Original behavior for single SR NO
        steps = algorithms_df[algorithms_df['SR NO'] == sr_no]['ALGORITHMS'].dropna().tolist()
        # Remove any empty strings or whitespace-only strings
        steps = [step for step in steps if step.strip()]
        return steps

def parse_algorithm(algorithm_steps):
    """
    Parse the algorithm steps and extract variables, cost codes, and intermediate values.
    
    Conventions:
    - Input variables: 
        * Single letters: L, B, H
        * Any variable containing underscore: SINK_TOP_L, BOWL_WIDTH etc.
    - Intermediate values: VALUE1, VALUE2, ..., RESULT
    - Cost codes: Any alphanumeric starting with S or L, followed by digits/letters
    """
    input_variables = set()
    cost_codes = set()
    intermediate_values = set()
    
    # Define regex patterns based on validation functions
    input_vars_pattern = r'\b(L|B|H|QTY)\b|[A-Z]+(?:_[A-Z]+)+'  # Single letters or contains underscore
    intermediate_pattern = r'\b(VALUE\d+|RESULT)\b'
    cost_codes_pattern = r'\b[SL][A-Z0-9]+\b'  # Starts with S or L
    
    for step in algorithm_steps:
        if not step or '=' not in step:
            continue
            
        # Extract all variables, excluding numbers and operators
        all_vars = set(var for var in re.findall(r'\b[A-Z][A-Z0-9_]+\b|\b[LBH]\b', step)
                      if not var.isdigit())
        
        # Categorize each variable
        for var in all_vars:
            if re.match(input_vars_pattern, var):
                input_variables.add(var)
            elif re.match(intermediate_pattern, var):
                intermediate_values.add(var)
            elif re.match(cost_codes_pattern, var):
                cost_codes.add(var)
    
    return (sorted(list(input_variables)), 
            sorted(list(cost_codes)), 
            sorted(list(intermediate_values)))

def get_cost_values(cost_codes):
    """
    Get cost values for given cost codes, handling both direct matches and A/B suffix cases.
    
    Returns:
        tuple: (cost_values, missing_variables)
        - cost_values: dict mapping cost codes to their values
        - missing_variables: list of codes that weren't found
    """
    cost_df = load_cost_data()
    cost_values = {}
    missing_variables = []
    
    for code in cost_codes:
        value = None
        
        # First try exact match using RATE (B)
        exact_match = cost_df[cost_df['CODE NO'] == code]
        if not exact_match.empty:
            value = exact_match.iloc[0]['RATE (B)']
        
        # If no exact match, try splitting at last character if it's A or B
        elif len(code) > 1 and code[-1] in ['A', 'B']:
            base_code = code[:-1]
            column = 'SIZE/ REMARKS (A)' if code[-1] == 'A' else 'RATE (B)'
            
            base_match = cost_df[cost_df['CODE NO'] == base_code]
            if not base_match.empty:
                value = base_match.iloc[0][column]
        
        # Store result
        if value is not None:
            cost_values[code] = value
        else:
            missing_variables.append(code)
    
    return cost_values, missing_variables

def estimate_cost(algorithm_steps, input_values, cost_values):
    """Estimate the cost based on the algorithm steps, input values, and cost values."""
    results = {}
    final_result = None
    step_by_step = []

    def safe_eval(expr, variables):
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith('__')
        }
        allowed_names.update(variables)
        return eval(expr, {"__builtins__": {}}, allowed_names)

    for step in algorithm_steps:
        parts = step.split('=')
        if len(parts) == 2:
            left, right = parts
            left = left.strip()
            right = right.strip()

            # Replace cost codes with their values
            for code, value in cost_values.items():
                right = right.replace(code, str(value))

            # Replace variables with their values
            for var, value in input_values.items():
                right = right.replace(var, str(value))

            # Replace previous results
            for key, value in results.items():
                right = right.replace(key, str(value))

            # Evaluate the right side of the equation
            try:
                result = safe_eval(right, results)
                results[left] = result
                if left == 'RESULT':
                    final_result = result
                step_by_step.append(f"{left} = {right} = {result}")
            except Exception as e:
                error_msg = f"Error evaluating step: {step}\nError message: {str(e)}"
                step_by_step.append(error_msg)
                print(error_msg)

    return final_result, results, step_by_step

def evaluate_formula_steps(algorithm_steps, input_values, cost_values):
    """
    Evaluates multi-step formulas by substituting variables and calculating intermediate results.
    
    Args:
        algorithm_steps (list): List of formula steps (each with format "expression = output_var")
        input_values (dict): Dictionary of input variables (e.g., {'L': 10, 'B': 20})
        cost_values (dict): Dictionary of cost variables (e.g., {'S22A': 100, 'S22B': 50, 'L1': 25})
    
    Returns:
        tuple: (final_result, intermediate_results, calculation_steps)
    """
    intermediate_results = {}
    calculation_steps = []
    
    def clean_formula(formula):
        """Cleans the formula by replacing 'X' with '*' and handling other syntax"""
        return formula.replace('X', '*').replace('[', '').replace(']', '').replace('{', '').replace('}', '')
    
    def safe_replace(formula, var, value):
        """Safely replace variables using word boundaries"""
        pattern = r'\b' + re.escape(var) + r'\b'
        return re.sub(pattern, str(value), formula)
    
    for step in algorithm_steps:
        try:
            # Split into expression and output variable
            lhs, output_var = [part.strip() for part in step.split('=')]
            
            # Clean and prepare the formula
            formula = clean_formula(lhs)
            
            # Replace all known variables with their values
            # 1. Cost variables (longer codes first to avoid partial matches)
            for code, value in sorted(cost_values.items(), key=lambda x: len(x[0]), reverse=True):
                formula = safe_replace(formula, code, str(value))
            
            # 2. Input variables
            for var, value in input_values.items():
                formula = safe_replace(formula, var, str(value))
            
            # 3. Previously calculated intermediate values
            for var, value in intermediate_results.items():
                formula = safe_replace(formula, var, str(value))
            
            # Evaluate the formula
            result = eval(formula, {"__builtins__": {}}, {"math": math})
            
            # Store the result in intermediate_results
            intermediate_results[output_var.strip()] = result
            
            # Record the calculation step
            calculation_steps.append(f"{output_var} = {formula} = {result}")
            
        except Exception as e:
            calculation_steps.append(f"Error in step: {step}\nError: {str(e)}")
            return None, intermediate_results, calculation_steps
    
    # The final result should be stored in 'RESULT'
    final_result = intermediate_results.get('RESULT')
    
    return final_result, intermediate_results, calculation_steps
