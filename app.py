import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Resource Formatter", layout="centered")
st.title("📊 Convert Resource Table to Long Format")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("File uploaded. Preview:")
    st.dataframe(df.head())

    # Let user pick Activity ID column
    activity_col = st.selectbox("Select the Activity ID column", df.columns)

    # Ensure multiselect default is in options
    if activity_col:
        all_other_cols = [col for col in df.columns if col != activity_col]
        default_non_resource = [activity_col] if activity_col in all_other_cols else []
        non_resource_cols = st.multiselect(
            "Exclude non-resource columns",
            options=all_other_cols,
            default=default_non_resource
        )

        if st.button("Convert to Long Format"):
            resource_cols = [col for col in df.columns if col not in non_resource_cols]

            df_long = df.melt(
                id_vars=[activity_col],
                value_vars=resource_cols,
                var_name="Resource",
                value_name="Mandays"
            )

            # Filter non-zero / non-null
            df_long = df_long[df_long["Mandays"].notna() & (df_long["Mandays"] != 0)]

            st.success("Conversion complete. Preview:")
            st.dataframe(df_long)

            # Download
            def to_excel(bytes_df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    bytes_df.to_excel(writer, index=False, sheet_name='Resource Mandays')
                return output.getvalue()

            st.download_button(
                "📥 Download Excel",
                data=to_excel(df_long),
                file_name="resource_mandays_long_format.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
