import streamlit as st
import pandas as pd
from io import BytesIO

def summary(x):
if x is not None:
dt = pd.DataFrame(x.dtypes).reset_index()
dt.columns = ['Columns List', 'Data types']
return dt

# Function to convert DataFrame to CSV and provide download link

def convert_df_to_csv(df):
return df.to_csv(index=False).encode('utf-8')

# Function to get the CSV download link

def get_download_link(df, filename="updated_data_web_app.csv"):

```
csv = convert_df_to_csv(df)
st.sidebar.download_button(
    label="📥 Download ",
    data=csv,
    file_name=filename,
    mime='text/csv'
)

```

#Button CSS
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

```
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
            st.success('Changes reflects on Data Overview')

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
        if st.button:
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
                    # Replace spaces with underscores in column names
                    after_col = [col.replace(" ", "_") for col in before_col]
                    st.session_state.modified_columns = after_col
                    st.success('Updated column names: Spaces replaced with underscores')

    # Change column name
        st.write("")
        st.write("***")
        st.write("### *Rename Column Names* ")
        st.write('***')
        columns_names = st.session_state.modified_columns
        column_select = st.selectbox('Enter column name', options=columns_names)
        new_column_name = st.text_input('Enter New column name,')
        if st.button('Update'):
            if column_select and new_column_name:
                st.session_state.modified_columns = [
                    new_column_name if col == column_select else col
                    for col in st.session_state.modified_columns
                ]
        df.columns = st.session_state.modified_columns
        update_column_name=pd.DataFrame(df.columns,columns=['Updated Column Names'])
        st.success("Updated Column Names")
        st.table(update_column_name)
    # Duplicated rows
    with st.expander("",expanded=True):
        st.write("### *Duplicate Rows*")
        st.write('***')
        duplicate = df.duplicated().sum()
        st.write(f"No. of Duplicate rows: {duplicate}")
        if st.button('Delete Duplicate'):
            if duplicate:
                df.drop_duplicates(inplace=True)
            st.success('Successfully Deleted Duplicates')
        after_duplicate = df.duplicated().sum()
        st.write(f"Current Duplicate rows: {after_duplicate}")

    # Missing Values
    with st.expander("",expanded=True):
        st.write('### *Missing Values*')
        st.write('***')
        col7, col8 = st.columns(2)
        with col7:
            missing = df.isnull().sum().reset_index()
            missing.columns=['Columns','Missing Values']
            st.write("### Before Deletion")
            st.write(missing)

        with col8:
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            if st.button('Column-wise'):
                df.dropna(axis=1, inplace=True)
                st.success('Column-wise Deletion successful')
            if st.button('Row-wise'):
                df.dropna(axis=0, inplace=True)
                st.success('Row-wise Deletion successful')

        after_missing = df.isnull().sum().reset_index()
        after_missing.columns = ['Columns', 'Missing Values']
        st.write('### After Deletion')
        st.write(after_missing)

        # Filling Missing Values
        with st.expander('', expanded=True):
        st.write('### *Filling Missing Values*')
        st.write('***')
        
        # Display columns with missing values
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        st.write("### Columns with missing values:")
        st.write(missing)
        
        # Select columns to fill missing values
        fill_selected_values = st.multiselect('Select columns to fill missing values', options=missing.index.tolist())
        
        # Create fill method options
        fill_methods = ["Zero", "Median", "Mean", "Mode", "Forward fill", "Backward fill"]
        
        for column in fill_selected_values:
            col_type = df[column].dtype
        
            # Dropdown for fill method
            fill_method = st.selectbox(f'Select fill method for {column}', fill_methods, key=f"fill_{column}")
        
            # Apply the selected fill method
            if fill_method == "Zero":
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(0)
                    st.success(f'Filled missing values in {column} with zero')
                else:
                    st.warning(f'Cannot apply zero fill to {column} (Data type: {col_type})')
        
            elif fill_method == "Median":
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].median())
                    st.success(f'Filled missing values in {column} with Median')
                else:
                    st.warning(f'Cannot apply median fill to {column} (Data type: {col_type})')
        
            elif fill_method == "Mean":
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(df[column].mean())
                    st.success(f'Filled missing values in {column} with Mean')
                else:
                    st.warning(f'Cannot apply mean fill to {column} (Data type: {col_type})')
        
            elif fill_method == "Mode":
                df[column] = df[column].fillna(df[column].mode()[0])
                st.success(f'Filled missing values in {column} with Mode')
        
            elif fill_method == "Forward fill":
                df[column] = df[column].fillna(method='ffill')
                st.success(f'Filled missing values in {column} with Forward fill')
        
            elif fill_method == "Backward fill":
                df[column] = df[column].fillna(method='bfill')
                st.success(f'Filled missing values in {column} with Backward fill')
        
        # Show remaining missing values after filling
        after_fill = df.isnull().sum()
        st.write('')
        st.write("### *Current Missing Values:*")
        st.write('')
        st.write(after_fill)


    st.write(" ")
    st.write('### *Data Overview After Update*')
    st.write('***')
    st.table(df.head(8))

    # Provide download link for the updated dataframe
    st.sidebar.write("## 🗂️Download updated data ")
    get_download_link(df)

except Exception as e:
    st.error(f"An error occurred: {e}")

```
