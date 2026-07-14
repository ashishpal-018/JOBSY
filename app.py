from main import recommend_jobs
import streamlit as st
import pandas as pd

st.title("💼 AI Job Recommender")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf"]
)

if uploaded_file:

    if st.button("Recommend Jobs"):

        with st.spinner("Analyzing Resume..."):

            result = recommend_jobs(uploaded_file)

        st.subheader("Detected Skills")
        st.success(result["skills"])

        jobs_df = pd.DataFrame(result["jobs"])

        st.dataframe(
            jobs_df[
                [
                    "title",
                    "company",
                    "location",
                    "match_score"
                ]
            ],
            use_container_width=True
        )

        for job in result["jobs"]:

            st.markdown(
                f"""
### {job['title']}

🏢 **Company:** {job['company']}

📍 **Location:** {job['location']}

🎯 **Match Score:** {job['match_score']}%

🔗 [Apply Here]({job['url']})
"""
            )