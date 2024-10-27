import streamlit as st
import pandas as pd
from io import BytesIO

# Function to convert DataFrame to CSV and provide download link
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to get the CSV download link
def get_download_link(df, filename="updated_data_web_app.csv"):
    csv = convert_df_to_csv(df)
    st.sidebar.download_button(
        label="📥 Download",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# Reset session state function
def reset_session_state():
    st.session_state.clear()  # Clear all session state

# Sidebar file uploader
st.sidebar.header('📤Upload your CSV file here')
file = st.sidebar.file_uploader("", type="csv")

# Reset Button
st.sidebar.write("> *Click the Reset button to undo all changes*")
if st.sidebar.button('Reset'):
    reset_session_state()

# Check if a new file is uploaded and reset session state if needed
if file is not None and 'last_uploaded_file' in st.session_state:
    if st.session_state.last_uploaded_file != file:
        reset_session_state()

st.title("Welcome to Data Cleaning App")
st.write("> *Use the sidebar on your left to upload files*")

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

        with col2:
            # Data type conversion
            st.write('## Data type Conversion')
            change_dtype = st.multiselect("Select columns to change data type", options=df.columns)
            for column in change_dtype:
                current_type = df[column].dtype
                col_type = st.selectbox(f"Select data type for {column} (current: {current_type})", 
                                        ["Keep current", "numeric", "datetime", "categorical"])
                if col_type == "numeric" and current_type != 'numeric':
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif col_type == "datetime" and current_type != 'datetime64[ns]':
                    df[column] = pd.to_datetime(df[column], format="%d-%m-%Y", errors='coerce')
                elif col_type == "categorical" and current_type != 'category':
                    df[column] = df[column].astype('category')
            st.success('Data type changes reflected in Data Overview')

        with col1:
            st.expander('Data Overview', expanded=True).write(f"Columns = {df.shape[1]}, Rows = {df.shape[0]}")

        st.write("***")
        st.write('### *Column Name Changes*')
        with st.expander("", expanded=True):
            st.table(pd.DataFrame(st.session_state.modified_columns, columns=['Column Name']))

            # Modify column names
            if st.button('Uppercase'):
                st.session_state.modified_columns = [col.strip().upper() for col in st.session_state.modified_columns]
            if st.button('Lowercase'):
                st.session_state.modified_columns = [col.strip().lower() for col in st.session_state.modified_columns]
            if st.button('Spaces ➡ Underscore'):
                st.session_state.modified_columns = [col.replace(" ", "_") for col in st.session_state.modified_columns]

        df.columns = st.session_state.modified_columns

        # Handle Duplicate Rows
        st.expander("Duplicate Rows", expanded=True).write(f"Duplicate rows: {df.duplicated().sum()}")
        if st.button('Delete Duplicates'):
            df.drop_duplicates(inplace=True)
            st.success("Duplicates removed")

        # Missing Values Handling
        st.expander('Missing Values', expanded=True).write(df.isnull().sum().reset_index())

        # Filling Missing Values with Immediate Updates
        missing = df.isnull().sum()[df.isnull().sum() > 0]
        st.write("### Columns with missing values")
        st.write(missing)

        fill_selected_values = st.multiselect('Select columns to fill missing values', options=missing.index.tolist())
        if fill_selected_values:
            for column in fill_selected_values:
                col_type = df[column].dtype

                if st.button(f'Zero fill {column}'):
                    df[column].fillna(0, inplace=True)
                    st.success(f"Filled {column} with zeros")

                if pd.api.types.is_numeric_dtype(df[column]):
                    if st.button(f'Median fill {column}'):
                        df[column].fillna(df[column].median(), inplace=True)
                        st.success(f"Filled {column} with median value")

                    if st.button(f'Mean fill {column}'):
                        df[column].fillna(df[column].mean(), inplace=True)
                        st.success(f"Filled {column} with mean value")

                if st.button(f'Mode fill {column}'):
                    df[column].fillna(df[column].mode()[0], inplace=True)
                    st.success(f"Filled {column} with mode")

                if st.button(f'Forward fill {column}'):
                    df[column].fillna(method='ffill', inplace=True)
                    st.success(f"Forward filled {column}")

                if st.button(f'Backward fill {column}'):
                    df[column].fillna(method='bfill', inplace=True)
                    st.success(f"Backward filled {column}")

        st.write("### Data Overview After Update")
        st.write(df.head(8))

        # Provide download link for the updated dataframe
        st.sidebar.write("## 🗂️Download updated data")
        get_download_link(df)

    except Exception as e:
        st.error(f"An error occurred: {e}")
