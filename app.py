import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Resource Formatter", layout="centered")
st.title("📊 Convert Resource Table to Long Format + Summary")

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

            st.success("✅ Long format created")
            st.dataframe(df_long)

            # Create pivot-style summary: total mandays per Activity ID and Resource
            summary_df = df_long.groupby([activity_col, "Resource"]).sum().reset_index()

            st.success("📊 Pivot-style summary:")
            st.dataframe(summary_df)

            # Download both sheets as one Excel
            def to_excel(long_df, summary_df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    long_df.to_excel(writer, index=False, sheet_name='Long Format')
                    summary_df.to_excel(writer, index=False, sheet_name='Summary')
                return output.getvalue()

            st.download_button(
                "📥 Download Excel with Both Sheets",
                data=to_excel(df_long, summary_df),
                file_name="resource_mandays_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
