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





####################################################################################################




import streamlit as st
import pandas as pd
from some_model_library import process_input  # Replace with actual model processing library
from some_similarity_library import calculate_cosine_similarity  # Replace with actual similarity calculation library

# Title of the application
st.title("Model and Excel Data Interaction App")

# Part selection (A or B) with radio buttons
part_selection = st.radio("Choose a part to interact with:", ('A', 'B'))

# Initialize file path variables for models and Excel datasets
model_paths = {"Set": "path_to_set_model", "Move": "path_to_move_model", "Use": "path_to_use_model"}
excel_paths = {"Set": "path_to_set_excel", "Move": "path_to_move_excel", "Use": "path_to_use_excel"}

# Part A: Model Interaction
if part_selection == 'A':
    st.header("Part A: Model Interaction")

    # Dropdown menu for selecting a model
    model_choice = st.selectbox("Choose a Model", options=list(model_paths.keys()))

    # Text input for model processing
    model_input = st.text_area("Enter text for the model:", height=100)

    # Convert and Clear buttons side by side
    col1, col2 = st.columns(2)
    with col1:
        convert_button = st.button("Convert")
    with col2:
        clear_button = st.button("Clear")

    # Convert button functionality
    if convert_button:
        if model_input:
            # Placeholder for actual model processing function
            model_output = process_input(model_input, model_paths[model_choice])
            st.write(model_output)
        else:
            st.warning("Please enter some text to convert.")

    # Clear button functionality
    if clear_button:
        st.experimental_rerun()

# Part B: Excel File Interaction
elif part_selection == 'B':
    st.header("Part B: Excel File Interaction")

    # Dropdown for selecting an Excel file
    excel_choice = st.selectbox("Choose an Excel File", options=list(excel_paths.keys()))

    # Load the selected Excel file
    df = pd.read_excel(excel_paths[excel_choice])

    # Display dropdowns for 'Program Name' and 'Program Line Number' side by side
    col1, col2 = st.columns(2)
    with col1:
        program_name = st.selectbox("Program Name", options=df['Program Name'].unique())
    with col2:
        program_line_number = st.selectbox("Program Line Number", options=df['Program Line Number'].unique())

    # Display 'real_code' and 'correspond_code'
    real_code = df[df['Program Name'] == program_name]['real_code'].iloc[0]
    correspond_code = df[df['Program Line Number'] == program_line_number]['correspond_code'].iloc[0]
    st.text_area("Real Code", real_code, height=100)
    st.text_area("Correspond Code", correspond_code, height=100)

    # Calculate and display cosine similarity
    if 'model_output' in locals():  # Check if model_output exists
        similarity_score = calculate_cosine_similarity(model_output, correspond_code)
        st.text(f"Similarity Score: {similarity_score}")
    else:
        st.warning("Model output not yet generated.")

