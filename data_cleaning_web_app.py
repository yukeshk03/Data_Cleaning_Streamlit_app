import streamlit as st
import pandas as pd
from io import BytesIO

def summary(df):
    if df is not None:
        dt = pd.DataFrame(df.dtypes).reset_index()
        dt.columns = ['Columns List', 'Data types']
        return dt

# Function to convert DataFrame to CSV and provide download link
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to get the CSV download link
def get_download_link(df, filename="updated_data_web_app.csv"):
    csv = convert_df_to_csv(df)
    st.sidebar.download_button(
        label="📥 Download ",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# Button CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 150px; 
        height: 50px; 
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Reset session state function
def reset_session_state():
    st.session_state.clear()  # Clear all session state

st.sidebar.header('📤Upload your CSV file here')
file = st.sidebar.file_uploader("", type="csv")

# Reset Button
st.sidebar.write("> *Click the Reset button to undo all changes*")
if st.sidebar.button('Reset'):
    reset_session_state()

# Check if new file is uploaded and reset session state if needed
if file is not None and 'last_uploaded_file' in st.session_state:
    if st.session_state.last_uploaded_file != file:
        reset_session_state()

st.title("Welcome to Data Cleaning App")
st.write("> *Please Use the sidebar on your left side for uploading files*")
if file is None:
    st.warning('Please upload a file.')
else:
    try:
        # Save the file name in session to detect new file uploads
        st.session_state.last_uploaded_file = file

        # Load the data into session state if not already done
        if 'df' not in st.session_state:
            st.session_state.df = pd.read_csv(file)

        # Assign session state DataFrame to a variable for easy reference
        df = st.session_state.df

        # Initialize session state for modified columns if not already initialized
        if 'modified_columns' not in st.session_state:
            st.session_state.modified_columns = df.columns.tolist()

        st.write('---')
        st.title('File Overview')
        col1, col2 = st.columns(2)

        with col2:
            # Data type conversion
            with st.container():
                st.write('## Data type Conversion')
                change_dtype = st.multiselect("Select columns to Change Data type", options=df.columns)
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
                st.success('Changes reflect on Data Overview')
                st.session_state.df = df  # Save updated DataFrame to session state

        with col1:
            with st.expander('Data Overview', expanded=True):
                shape = df.shape
                st.write(f'Columns = {shape[1]}')
                st.write(f'Rows = {shape[0]}')
                st.write(summary(df))

        st.write("***")
        st.write('### *Column Name Changes*')
        with st.expander("",expanded=True):
            before_col = st.session_state.modified_columns
            before_col_df = pd.DataFrame(before_col, columns=['Column Name'])
            st.table(before_col_df)
            st.write("***")
            st.markdown("> *Buttons will strip the additional Spaces.And perform respective functions.Space -Replace will replace everything with underscore*")
            # Buttons for modifying column names
            col3, col4, col5, col6 = st.columns(4)
            with col3:
                if st.button('Capital'):
                    after_col = [col.strip().title() for col in before_col]
                    st.session_state.modified_columns = after_col
                    st.success('Updated column names to Capital Case')
            with col4:
                if st.button('Uppercase'):
                    after_col = [col.strip().upper() for col in before_col]
                    st.session_state.modified_columns = after_col
                    st.success('Updated column names to Upper Case')
            with col5:
                if st.button('Lowercase'):
                    after_col = [col.strip().lower() for col in before_col]
                    st.session_state.modified_columns = after_col
                    st.success('Updated column names to Lower Case')
            with col6:
                if st.button('Spaces ➡ Underscore'):
                    after_col = [col.replace(" ", "_") for col in before_col]
                    st.session_state.modified_columns = after_col
                    st.success('Updated column names: Spaces replaced with underscores')

            # Update column names in df
            df.columns = st.session_state.modified_columns
            st.session_state.df = df

            update_column_name = pd.DataFrame(df.columns, columns=['Updated Column Names'])
            st.success("Updated Column Names")
            st.table(update_column_name)

        # Duplicate rows
        with st.expander("", expanded=True):
            st.write("### *Duplicate Rows*")
            st.write('***')
            duplicate = df.duplicated().sum()
            st.write(f"No. of Duplicate rows: {duplicate}")
            if st.button('Delete Duplicate'):
                if duplicate:
                    df.drop_duplicates(inplace=True)
                    st.session_state.df = df
                st.success('Successfully Deleted Duplicates')
            after_duplicate = df.duplicated().sum()
            st.write(f"Current Duplicate rows: {after_duplicate}")

        # Missing Values
        with st.expander("", expanded=True):
            st.write('### *Missing Values*')
            st.write('***')
            col7, col8 = st.columns(2)
            with col7:
                missing = df.isnull().sum().reset_index()
                missing.columns = ['Columns', 'Missing Values']
                st.write("### Before Deletion")
                st.write(missing)

            with col8:
                if st.button('Column-wise'):
                    df.dropna(axis=1, inplace=True)
                    st.session_state.df = df
                    st.success('Column-wise Deletion successful')
                if st.button('Row-wise'):
                    df.dropna(axis=0, inplace=True)
                    st.session_state.df = df
                    st.success('Row-wise Deletion successful')

            after_missing = df.isnull().sum().reset_index()
            after_missing.columns = ['Columns', 'Missing Values']
            st.write('### After Deletion')
            st.write(after_missing)

        # Filling Missing Values
        with st.expander('', expanded=True):
            st.write('### *Filling Missing Values*')
            st.write('***')

            missing = df.isnull().sum()
            missing = missing[missing > 0]
            st.write("### Columns with missing values:")
            st.write(missing)

            fill_selected_values = st.multiselect('Select columns to fill missing values', options=missing.index.tolist())
            for column in fill_selected_values:
                col_type = df[column].dtype
                col9, col10, col11 = st.columns(3)

                with col9:
                    if st.button(f'Zero fill {column}'):
                        if pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].fillna(0)
                            st.session_state.df = df
                            st.success(f'Filled missing values in {column} with zero')

                with col10:
                    if st.button(f'Median fill {column}'):
                        if pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].fillna(df[column].median())
                            st.session_state.df = df
                            st.success(f'Filled missing values in {column} with Median')

                with col11:
                    if st.button(f'Mean fill {column}'):
                        if pd.api.types.is_numeric_dtype(df[column]):
                            df[column] = df[column].fillna(df[column].mean())
                            st.session_state.df = df
                            st.success(f'Filled missing values in {column} with Mean')

                with col9:
                    if st.button(f'Mode fill {column}'):
                        df[column] = df[column].fillna(df[column].mode()[0])
                        st.session_state.df = df
                        st.success(f'Filled missing values in {column} with Mode')

                with col10:
                    if st.button(f'Forward fill {column}'):
                        df[column] = df[column].fillna(method='ffill')
                        st.session_state.df = df
                        st.success(f'Filled missing values in {column} with Forward fill')

                with col11:
                    if st.button(f'Backward fill {column}'):
                        df[column] = df[column].fillna(method='bfill')
                        st.session_state.df = df
                        st.success(f'Filled missing values in {column} with Backward fill')

            after_fill = df.isnull().sum()
            st.write("### *Current Missing Values:*")
            st.write(after_fill)

        # Download the updated DataFrame as a CSV
        get_download_link(df)

    except Exception as e:
        st.error(f"An error occurred: {e}")
