import streamlit as st
import os
import pandas as pd
from streamlit_file_browser import st_file_browser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '_jk_data/')

def file_explorer():

    # Set the root directory for the file explorer
    root_dir = DATA_DIR # Change this to your desired root directory

    # Use the st_file_browser component
    event = st_file_browser(
        root_dir,
        key="file_explorer",
        show_choose_file=True,
        show_download_file=True,
        show_delete_file=False,
        show_new_folder=False,
        show_upload_file=False,
    )

    # Store the selected file in session state
    if event and event.get("type") == "SELECT_FILE":
        st.session_state.selected_file = root_dir+event['target']['path']

    # Display and edit the selected file
    if hasattr(st.session_state, 'selected_file'):
        selected_file = st.session_state.selected_file
        #st.write(f"Selected file: {selected_file}")

        if selected_file.endswith(('.xlsx', '.xls')):
            # Read the Excel file
            df = pd.read_excel(selected_file)
            
            # Display the dataframe and allow editing
            st.subheader("Edit Excel File")
            edited_df = st.data_editor(df, use_container_width=True,num_rows="dynamic")
            
            # Add a button to save changes
            if st.button("Save Changes"):
                try:
                    edited_df.to_excel(selected_file, index=False)
                    st.success("Changes saved successfully!")
                except Exception as e:
                    st.error(f"Error saving file: {str(e)}")
        
        elif selected_file.endswith('.csv'):
            # Read the CSV file
            df = pd.read_csv(selected_file)
            
            # Display the dataframe and allow editing
            st.subheader("Edit CSV File")
            edited_df = st.data_editor(df, use_container_width=True,num_rows="dynamic")
            
            # Add a button to save changes
            if st.button("Save Changes"):
                try:
                    edited_df.to_csv(selected_file, index=False)
                    st.success("Changes saved successfully!")
                except Exception as e:
                    st.error(f"Error saving file: {str(e)}")
        
        else:
            # For non-Excel/CSV files, display content as before
            try:
                with open(selected_file, "r") as file:
                    content = file.read()
                st.text_area("File Content", content, height=300)
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    # You can add more functionality here, such as file management operations
