import streamlit as st
import pandas as pd
from io import BytesIO

# Function to display summary of data types
def summary(df):
    if df is not None:
        dt = pd.DataFrame(df.dtypes).reset_index()
        dt.columns = ['Column', 'Data Type']
        return dt

# Function to convert DataFrame to CSV and provide download link
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to provide a download link for the CSV
def get_download_link(df, filename="updated_data_web_app.csv"):
    csv = convert_df_to_csv(df)
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# Button CSS for uniform styling
st.markdown("""
    <style>
    .stButton > button {
        width: 150px;
        height: 50px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to reset session state
def reset_session_state():
    st.session_state.clear()

# Sidebar for file upload and reset button
st.sidebar.header('📤 Upload your CSV file here')
file = st.sidebar.file_uploader("", type="csv")

st.sidebar.write("> *Click the Reset button to undo all changes*")
if st.sidebar.button('Reset'):
    reset_session_state()

# Check if a new file is uploaded
if file is not None and 'last_uploaded_file' in st.session_state:
    if st.session_state.last_uploaded_file != file:
        reset_session_state()

# Title and upload instructions
st.title("Welcome to Data Cleaning App")
st.write("> *Please use the sidebar on your left to upload files*")

# Main app
if file is None:
    st.warning('Please upload a file.')
else:
    try:
        # Save the file name in session to detect new file uploads
        st.session_state.last_uploaded_file = file

        # Read CSV file
        df = pd.read_csv(file)

        # Initialize session state for modified columns if not already initialized
        if 'modified_columns' not in st.session_state:
            st.session_state.modified_columns = df.columns.tolist()

        st.write('---')
        st.title('File Overview')
        
        col1, col2 = st.columns(2)

        # Data type conversion section
        with col2:
            st.write('## Data Type Conversion')
            change_dtype = st.multiselect("Select columns to change data type", options=df.columns)
            for column in change_dtype:
                current_type = df[column].dtype
                col_type = st.selectbox(f"Select data type for {column} (current: {current_type})", ["Keep current", "numeric", "datetime", "categorical"])
                if col_type == "numeric":
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif col_type == "datetime":
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                elif col_type == "categorical":
                    df[column] = df[column].astype('category')
            st.success('Data type changes applied.')

        # Data overview section
        with col1:
            with st.expander('Data Overview', expanded=True):
                shape = df.shape
                st.write(f'Columns: {shape[1]}')
                st.write(f'Rows: {shape[0]}')
                st.write(summary(df))

        # Column name modifications
        st.write('### *Column Name Changes*')
        with st.expander("Change Column Names", expanded=True):
            before_col = st.session_state.modified_columns
            before_col_df = pd.DataFrame(before_col, columns=['Column Name'])
            st.table(before_col_df)
            
            col3, col4, col5, col6 = st.columns(4)
            if st.button('Capital'):
                st.session_state.modified_columns = [col.title() for col in before_col]
            if st.button('Uppercase'):
                st.session_state.modified_columns = [col.upper() for col in before_col]
            if st.button('Lowercase'):
                st.session_state.modified_columns = [col.lower() for col in before_col]
            if st.button('Spaces ➡ Underscore'):
                st.session_state.modified_columns = [col.replace(" ", "_") for col in before_col]
            df.columns = st.session_state.modified_columns

            st.success("Column name changes applied.")
            st.table(pd.DataFrame(df.columns, columns=['Updated Column Names']))

        # Rename column functionality
        st.write("### *Rename Column Names*")
        column_select = st.selectbox('Select column to rename', options=st.session_state.modified_columns)
        new_column_name = st.text_input('Enter new column name')
        if st.button('Update Column Name'):
            if column_select and new_column_name:
                st.session_state.modified_columns = [new_column_name if col == column_select else col for col in st.session_state.modified_columns]
                df.columns = st.session_state.modified_columns
                st.success("Column name updated.")
                st.table(pd.DataFrame(df.columns, columns=['Updated Column Names']))

        # Duplicate rows handling
        with st.expander("Duplicate Rows", expanded=True):
            duplicate_count = df.duplicated().sum()
            st.write(f"No. of Duplicate rows: {duplicate_count}")
            if st.button('Delete Duplicates'):
                df.drop_duplicates(inplace=True)
                st.success("Duplicates deleted.")

        # Handling missing values
        with st.expander("Missing Values", expanded=True):
            missing_summary = df.isnull().sum()
            st.write("Columns with missing values:")
            st.write(missing_summary[missing_summary > 0])

            # Column-wise and Row-wise deletion
            if st.button('Delete Columns with Missing Values'):
                df.dropna(axis=1, inplace=True)
                st.success("Column-wise deletion successful")
            if st.button('Delete Rows with Missing Values'):
                df.dropna(axis=0, inplace=True)
                st.success("Row-wise deletion successful")

            # Filling missing values options
            fill_columns = st.multiselect('Select columns to fill missing values', options=missing_summary[missing_summary > 0].index)
            for column in fill_columns:
                fill_option = st.selectbox(f'Fill missing values in {column} with:', ["Mean", "Median", "Mode", "Zero", "Forward Fill", "Backward Fill"])
                if fill_option == "Mean":
                    df[column].fillna(df[column].mean(), inplace=True)
                elif fill_option == "Median":
                    df[column].fillna(df[column].median(), inplace=True)
                elif fill_option == "Mode":
                    df[column].fillna(df[column].mode()[0], inplace=True)
                elif fill_option == "Zero":
                    df[column].fillna(0, inplace=True)
                elif fill_option == "Forward Fill":
                    df[column].fillna(method='ffill', inplace=True)
                elif fill_option == "Backward Fill":
                    df[column].fillna(method='bfill', inplace=True)
                st.success(f'Missing values in {column} filled with {fill_option}.')

        # Updated data overview
        st.write("### *Data Overview After Updates*")
        st.table(df.head(8))

        # Provide download link for the updated dataframe
        st.sidebar.write("## 🗂️ Download Updated Data")
        get_download_link(df)

    except Exception as e:
        st.error(f"An error occurred: {e}")
