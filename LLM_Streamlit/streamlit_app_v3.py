import streamlit as st
import pandas as pd
import difflib

# Initialize the application and set the title
st.title("Model and Excel Data Interaction App")

# Part A: Model Interaction
st.header("Model Interaction")

# File path variables for three models
model_paths = {
    "Set Model": "path_to_set_model",
    "Move Model": "path_to_move_model",
    "Use Model": "path_to_use_model"
}

# Dropdown to select a model
model_choice = st.selectbox("Select a Model", options=list(model_paths.keys()))

# Text input for the model
model_input = st.text_area("Enter text for the model:")

# Convert button with warning for empty input
if st.button("Convert"):
    if model_input:
        # Placeholder for model processing code
        model_output = "Processed output based on the model"
        st.write(model_output)
    else:
        st.warning("Please enter some text to convert.")

# Clear button functionality
if st.button("Clear"):
    # Code to clear the text input and output
    st.experimental_rerun()

# Part B: Excel File Interaction
st.header("Excel File Interaction")

# File path variables for Excel files
excel_paths = {
    "Set Data": "path_to_set_excel",
    "Move Data": "path_to_move_excel",
    "Use Data": "path_to_use_excel"
}

# Dropdown to select an Excel file
excel_choice = st.selectbox("Select an Excel File", options=list(excel_paths.keys()))

# Reading the selected Excel file
df = pd.read_excel(excel_paths[excel_choice])
program_names = df['Program Name'].unique()
program_line_numbers = df['Program Line Number'].unique()

# Dropdowns for 'Program Name' and 'Program Line Number'
selected_program_name = st.selectbox("Select Program Name", options=program_names)
selected_program_line_number = st.selectbox("Select Program Line Number", options=program_line_numbers)

# Display 'real_code' and 'correspond_code'
real_code = df[df['Program Name'] == selected_program_name]['real_code'].iloc[0]
correspond_code = df[df['Program Line Number'] == selected_program_line_number]['correspond_code'].iloc[0]
st.text_area("Real Code", real_code, height=100)
st.text_area("Correspond Code", correspond_code, height=100)

# Comparison using difflib
if model_output:  # Assuming model_output is available from Part A
    differences = difflib.ndiff(model_output.splitlines(), correspond_code.splitlines())
    st.text_area("Differences", "\n".join(differences), height=100)
