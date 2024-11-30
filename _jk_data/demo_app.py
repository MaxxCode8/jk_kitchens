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

def main():
    st.title("Data Fetching Demo")

    st.header("1. Categories")
    categories = get_categories()
    st.write(categories)

    selected_category = st.selectbox("Select a category", categories)

    st.header("2. Product Types")
    product_types = get_product_types(selected_category)
    st.write(product_types)

    selected_product_type = st.selectbox("Select a product type", product_types)

    st.header("3. Product Features")
    features = get_product_features(selected_category, selected_product_type)
    st.write(features)

    selected_feature = st.selectbox("Select a feature", features)

    st.header("4. Sub-Features")
    sub_features = get_sub_features(selected_category, selected_product_type, selected_feature)
    st.write(sub_features)

    if sub_features != ['']:
        selected_sub_feature = st.selectbox("Select a sub-feature", sub_features)
    else:
        selected_sub_feature = None

    st.header("5. Quantity/Size/Dimensions")
    dimensions = get_quantity_size_dimensions(selected_category, selected_product_type, selected_feature, selected_sub_feature)
    st.write(dimensions)

    st.header("6. Algorithm Codes")
    algorithm_codes = get_algorithm_codes(selected_category, selected_product_type, selected_feature, selected_sub_feature)
    
    if algorithm_codes:
        selected_algorithm_type = st.radio("Select Algorithm Type", ["SS202", "SS304"])
        sr_no = algorithm_codes[selected_algorithm_type]
        st.write(sr_no)

        st.header("7. Algorithm Steps")
        algorithm_steps = get_algorithm_steps(sr_no)
        
        # Check if algorithm steps exist
        if algorithm_steps and any(step.strip() for step in algorithm_steps):
            st.write("Formula found:")
            st.write(algorithm_steps)
            
            st.header("8. Parsed Algorithm")
            input_variables, cost_codes, intermediate_values = parse_algorithm(algorithm_steps)
            st.write("Input Variables:", input_variables)
            st.write("Cost Codes:", cost_codes)
            st.write("Intermediate Values:", intermediate_values)

            st.header("9. Cost Values")
            cost_values, missing_variables = get_cost_values(cost_codes)
            st.write("Found Cost Values:", cost_values)
            if missing_variables:
                st.warning(f"Missing values for variables: {', '.join(missing_variables)}")

            st.header("10. Cost Estimation")
            if missing_variables:
                st.error("Cannot proceed with cost estimation due to missing cost values")
            else:
                st.write("Enter dimensions:")
                input_values = {}
                for var in input_variables:
                    if var == 'QTY':
                        input_values[var] = st.number_input(f"{var}", min_value=1, step=1)
                    else:
                        input_values[var] = st.number_input(f"{var}", min_value=0.0, step=0.1)

                if st.button("Estimate Cost"):
                    final_result, intermediate_results, step_by_step = evaluate_formula_steps(
                        algorithm_steps, 
                        input_values, 
                        cost_values
                    )
                    
                    st.subheader("Step-by-step Calculation:")
                    for step in step_by_step:
                        st.write(step)
                    
                    st.subheader("Intermediate Results:")
                    for key, value in intermediate_results.items():
                        st.write(f"{key}: {value}")
                    
                    if final_result is not None:
                        st.subheader("Final Estimated Cost:")
                        st.write(f"{final_result:.2f}")
                    else:
                        st.error("Could not calculate final result. Please check the calculation steps for errors.")

        else:
            st.warning(f"""No formula found for this combination:
                            - Category: {selected_category}
                            - Product Type: {selected_product_type}
                            - Feature: {selected_feature}
                            - Sub-Feature: {selected_sub_feature or 'None'}
                            - Algorithm Type: {selected_algorithm_type}
                            - SR NO: {sr_no}""")

    st.header("11. Individual Cost Data")
    code_no = st.text_input("Enter CODE NO for individual cost data")
    if code_no:
        cost_data = get_cost(code_no)
        st.write(cost_data)

if __name__ == "__main__":
    main()
