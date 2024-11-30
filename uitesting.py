import streamlit as st
from get_data import (
    get_categories,
    get_product_types,
    get_product_features,
    get_sub_features,
    get_quantity_size_dimensions,
    get_algorithm,
    get_cost,
    get_algorithm_codes,
    get_algorithm_steps,
    parse_algorithm,
    get_cost_values,
    evaluate_formula_steps
)
from file_explorer import file_explorer


def create_form(form_id):
    with st.expander(f"Form {form_id}", expanded=True):
        # Add delete button at the top right of each form
        if st.button("🗑️ Delete Form", key=f"delete_{form_id}"):
            st.session_state.form_count -= 1
            for field in ['category', 'name', 'email', 'age', 'dob', 'comments']:
                if f"{field}_{form_id}" in st.session_state:
                    del st.session_state[f"{field}_{form_id}"]
            st.rerun()
        
        # Rest of the form fields
        st.selectbox(
            "Select Category",
            ["Option 1", "Option 2", "Option 3"],
            key=f"category_{form_id}"
        )
        
        st.text_input("Full Name", key=f"name_{form_id}")
        st.text_input("Email", key=f"email_{form_id}")
        st.number_input("Age", min_value=0, max_value=120, key=f"age_{form_id}")
        st.date_input("Date of Birth", key=f"dob_{form_id}")
        st.text_area("Comments", key=f"comments_{form_id}")

def invoice_generator_tab():
    st.header("Invoice Generator")
    
    # Add fixed quotation details at the top
    col1, col2 = st.columns(2)
    with col1:
        if 'customer_name' not in st.session_state:
            st.session_state.customer_name = ""
        st.text_input(
            "Customer Name",
            value=st.session_state.customer_name,
            key="customer_name"
        )
        
        if 'subject' not in st.session_state:
            st.session_state.subject = ""
        st.text_input(
            "Subject/Project Name",
            value=st.session_state.subject,
            key="subject"
        )
    
    with col2:
        if 'quotation_date' not in st.session_state:
            st.session_state.quotation_date = None
        st.date_input(
            "Quotation Date",
            value=st.session_state.quotation_date,
            key="quotation_date"
        )
    
    st.markdown("---")  # Add a separator line
    
    # Debug information at the top
    if st.checkbox("Show Debug Info"):
        st.write("Session State Products:", st.session_state.products)
        st.write("Session State Product Costs:", st.session_state.product_costs)
    
    # Initialize session states
    if 'products' not in st.session_state:
        st.session_state.products = [{}]
    if 'product_costs' not in st.session_state:
        st.session_state.product_costs = {}
    
    for i, product in enumerate(st.session_state.products):
        with st.expander(f"Product {i+1}", expanded=True):
            # Main form content and action buttons in columns
            main_col, action_col = st.columns([3, 1])
            
            with action_col:
                # Action buttons stacked vertically on the right
                if len(st.session_state.products) > 1:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        # st.write("Debug: Removing product", i)  # Debug
                        st.session_state.products.pop(i)
                        if f"cost_{i}" in st.session_state.product_costs:
                            del st.session_state.product_costs[f"cost_{i}"]
                        st.rerun()
                
                # Cost display
                if f"cost_{i}" in st.session_state.product_costs:
                    st.metric(
                        "Product Cost", 
                        f"₹{st.session_state.product_costs[f'cost_{i}']:.2f}"
                    )
            
            with main_col:
                # Selection fields
                categories = get_categories()
                selected_category = st.selectbox(
                    "Select Category", 
                    categories,
                    key=f"category_{i}"
                )
                
                product_types = get_product_types(selected_category)
                selected_product_type = st.selectbox(
                    "Select Product Type", 
                    product_types,
                    key=f"product_type_{i}"
                )
                
                features = get_product_features(selected_category, selected_product_type)
                selected_feature = st.selectbox(
                    "Select Feature", 
                    features,
                    key=f"feature_{i}"
                )
                
                sub_features = get_sub_features(selected_category, selected_product_type, selected_feature)
                selected_sub_feature = None
                if sub_features != ['']:
                    selected_sub_feature = st.selectbox(
                        "Select Sub-feature", 
                        sub_features,
                        key=f"sub_feature_{i}"
                    )
                
                # Algorithm selection
                algorithm_codes = get_algorithm_codes(
                    selected_category, 
                    selected_product_type, 
                    selected_feature, 
                    selected_sub_feature
                )
                
                if algorithm_codes:
                    # st.write("Debug: Algorithm codes found:", algorithm_codes)  # Debug
                    
                    selected_algorithm_type = st.radio(
                        "Select Algorithm Type", 
                        ["SS202", "SS304"],
                        key=f"algorithm_type_{i}"
                    )
                    sr_no = algorithm_codes[selected_algorithm_type]
                    
                    if sr_no:
                        # st.write("Debug: SR NO:", sr_no)  # Debug
                        algorithm_steps = get_algorithm_steps(sr_no)
                        
                        if algorithm_steps and any(step.strip() for step in algorithm_steps):
                            # st.write("Debug: Algorithm steps:", algorithm_steps)  # Debug
                            
                            # Parse algorithm
                            input_variables, cost_codes, _ = parse_algorithm(algorithm_steps)
                            # st.write("Debug: Input variables:", input_variables)  # Debug
                            # st.write("Debug: Cost codes:", cost_codes)  # Debug
                            
                            cost_values, missing_variables = get_cost_values(cost_codes)
                            st.write("Debug: Cost values:", cost_values)  # Debug
                            
                            if not missing_variables:
                                # Input fields
                                input_values = {}
                                for var in input_variables:
                                    if var in ['L', 'B', 'H', 'LENGTH', 'BREADTH', 'HEIGHT', 'WIDTH', 'DEPTH']:  # Add any other dimension variables
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            input_val = st.number_input(
                                                f"{var}",
                                                min_value=0.0, 
                                                step=0.1,
                                                key=f"{var}_{i}"
                                            )
                                        with col2:
                                            unit = st.radio(
                                                "Unit",
                                                options=["mm", "inches"],
                                                key=f"{var}_unit_{i}",
                                                horizontal=True
                                            )
                                        # Convert to mm if input is in inches
                                        input_values[var] = input_val * 25.4 if unit == "inches" else input_val
                                        if unit == "inches":
                                            st.caption(f"Converting to mm: {input_val} inches = {input_val * 25.4:.2f} mm")
                                    elif var == 'QTY':
                                        input_values[var] = st.number_input(
                                            f"{var}", 
                                            min_value=1, 
                                            step=1,
                                            key=f"{var}_{i}"
                                        )
                                    else:
                                        input_values[var] = st.number_input(
                                            f"{var}", 
                                            min_value=0.0, 
                                            step=0.1,
                                            key=f"{var}_{i}"
                                        )
                                
                                with action_col:
                                    if st.button("Calculate Cost", key=f"calc_{i}"):
                                        # st.write("Debug: Calculating cost for product", i)  # Debug
                                        # st.write("Debug: Input values:", input_values)  # Debug
                                        
                                        final_result, intermediate_results, calculation_steps = evaluate_formula_steps(
                                            algorithm_steps,
                                            input_values,
                                            cost_values
                                        )
                                        
                                        # st.write("Debug: Final result:", final_result)  # Debug
                                        # st.write("Debug: Intermediate results:", intermediate_results)  # Debug
                                        # st.write("Debug: Calculation steps:", calculation_steps)  # Debug
                                        
                                        if final_result is not None:
                                            st.session_state.product_costs[f"cost_{i}"] = final_result
                                            st.session_state.products[i] = {
                                                'category': selected_category,
                                                'product_type': selected_product_type,
                                                'feature': selected_feature,
                                                'sub_feature': selected_sub_feature,
                                                'algorithm_type': selected_algorithm_type,
                                                'cost': final_result
                                            }
                                            st.rerun()
                            else:
                                st.error("Cannot proceed with cost estimation due to missing cost values")
                                st.warning(f"Missing values for variables: {', '.join(missing_variables)}")
                        else:
                            st.warning(f"""No formula found for this combination:
                                - Category: {selected_category}
                                - Product Type: {selected_product_type}
                                - Feature: {selected_feature}
                                - Sub-Feature: {selected_sub_feature or 'None'}
                                - Algorithm Type: {selected_algorithm_type}
                                - SR NO: {sr_no}""")
                    else:
                        st.warning(f"""No SR NO found for:
                                - Category: {selected_category}
                                - Product Type: {selected_product_type}
                                - Feature: {selected_feature}
                                - Sub-Feature: {selected_sub_feature or 'None'}
                                - Algorithm Type: {selected_algorithm_type}""")
                else:
                    st.warning(f"""No algorithm codes found for:
                            - Category: {selected_category}
                            - Product Type: {selected_product_type}
                            - Feature: {selected_feature}
                            - Sub-Feature: {selected_sub_feature or 'None'}""")
    
    # Add new product button
    if st.button("➕ Add Another Product"):
        st.session_state.products.append({})
        st.rerun()
    
    # Total calculation
    if st.session_state.product_costs:
        st.markdown("---")
        total_cost = sum(st.session_state.product_costs.values())
        st.metric("Total Cost", f"₹{total_cost:.2f}")

def file_explorer_tab():
    st.header("File Explorer")
    file_explorer()

def settings_tab():
    st.header("Settings")
    st.write("Settings functionality will be implemented here.")
    # Add your settings functionality here

def main():
    st.set_page_config(page_title="JK Kitchens App")
    
    # Add centered header image with custom CSS for larger size
    st.markdown(
        """
        <style>
        [data-testid="stImage"] {
            width: 100%;
            max-width: 10000px;  # Adjust this value to control maximum width
            margin: auto;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Simplified column structure for larger image
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        st.image("jklogo.png", use_column_width=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📄 Invoice Generator", 
        "📁 File Explorer", 
        "⚙️ Settings"
    ])
    
    # Content for each tab
    with tab1:
        invoice_generator_tab()
    
    with tab2:
        file_explorer_tab()
    
    with tab3:
        settings_tab()

if __name__ == "__main__":
    main()