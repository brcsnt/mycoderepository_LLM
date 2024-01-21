import streamlit as st
import pandas as pd

# Assuming you have a function `convert_code` for the conversion process.
def convert_code(model_choice, x_code):
    # Your LLM conversion logic here
    y_code = "Converted Y code based on the model"
    return y_code

def main():
    st.title("Advanced Code Converter App")

    # Model selection
    model_choice = st.sidebar.selectbox("Choose your model", ["Model 1", "Model 2", "Model 3"])

    # Upload X code as a file or input in text area
    x_code_input_method = st.sidebar.radio("How would you like to input X code?", ("Write Code", "Upload File"))

    x_code = ""
    if x_code_input_method == "Write Code":
        x_code = st.text_area("Enter your X code here:")
    else:
        file = st.file_uploader("Upload your code file", type=["py", "txt"])
        if file is not None:
            x_code = str(file.read(), "utf-8")
    
    # Button to convert code
    if st.button("Convert Code"):
        if x_code:
            try:
                # Call the conversion function
                y_code = convert_code(model_choice, x_code)
                # Display the converted Y code
                st.text_area("Converted Y Code", y_code, height=300)
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
        else:
            st.warning("Please input X code to convert.")

# Run the app
if __name__ == "__main__":
    main()






import streamlit as st
import difflib

# Assuming the convert_code function exists as before
# ...

def highlight_differences(converted_code, true_code):
    """
    Highlights the differences between the converted code and the true code.
    """
    # Create a Differ object
    differ = difflib.Differ()

    # Calculate the differences
    diff = list(differ.compare(converted_code.splitlines(keepends=True),
                               true_code.splitlines(keepends=True)))
    
    # Create a highlighted HTML string
    highlighted_diff = []
    for line in diff:
        if line.startswith('+ '):
            # Lines in true_code but not in converted_code
            highlighted_diff.append(f'<span style="background-color: #90ee90">{line[2:]}</span>')
        elif line.startswith('- '):
            # Lines in converted_code but not in true_code
            highlighted_diff.append(f'<span style="background-color: #ffcccb">{line[2:]}</span>')
        else:
            highlighted_diff.append(line[2:])

    return ''.join(highlighted_diff)

def main():
    st.title("Advanced Code Converter with Comparison")

    # Rest of the app layout as before
    # ...

    # Button to convert code
    if st.button("Convert Code"):
        if x_code:
            try:
                y_code = convert_code(model_choice, x_code)
                st.text_area("Converted Y Code", y_code, height=300)

                # Input for the true code
                true_code = st.text_area("Enter the True Code for comparison", height=300)

                # Compare the converted code with the true code
                if true_code:
                    highlighted_diff = highlight_differences(y_code, true_code)
                    st.markdown(highlighted_diff, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
        else:
            st.warning("Please input X code to convert.")

# Run the app
if __name__ == "__main__":
    main()
