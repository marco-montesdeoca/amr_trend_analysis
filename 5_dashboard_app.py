import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from wordcloud import WordCloud # Import for WordCloud
import matplotlib.pyplot as plt # Import for plotting with matplotlib

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="PubMed Antibiotic Resistance Analysis")

# --- Data Loading (with caching for efficiency) ---
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    # Ensure the date column is of datetime type
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    df['publication_year'] = df['publication_date'].dt.year
    # Remove rows with invalid dates after conversion
    df.dropna(subset=['publication_date', 'publication_year'], inplace=True)
    df['publication_year'] = df['publication_year'].astype(int)
    
    # --- Verification and Adjustment of the 'dominant_topic' column ---
    if 'dominant_topic' not in df.columns:
        st.error("Error: The 'dominant_topic' column was not found in the data. Please ensure '3_nlp_analysis.py' ran successfully and saved this column.")
        st.stop() # Stop the app if the crucial column is missing

    # Adjust the format of the 'dominant_topic' column if necessary.
    # If 'dominant_topic' comes as numbers (0, 1, 2...) and your labels are 'Topic 1', 'Topic 2', etc.:
    if pd.api.types.is_numeric_dtype(df['dominant_topic']):
        df['dominant_topic'] = 'Topic ' + (df['dominant_topic'] + 1).astype(str)
    # If it comes as 'Topic_0', 'Topic_1' and your labels are 'Topic 1', 'Topic 2', etc.:
    elif df['dominant_topic'].astype(str).str.contains(r'Topic_\d+').any():
        df['dominant_topic'] = df['dominant_topic'].astype(str).str.replace('Topic_', 'Topic ')
        # You might need a +1 here if your Topic_0 maps to Topic 1, etc.
        # For example, if Topic_0 -> Topic 1, Topic_1 -> Topic 2:
        # df['dominant_topic'] = 'Topic ' + (df['dominant_topic'].astype(str).str.extract(r'(\d+)').astype(int) + 1).astype(str)
    
    # Ensure the final format is 'Topic X'
    df['dominant_topic'] = df['dominant_topic'].astype(str)

    return df

# --- LDA Topic Definitions (based on the output you provided) ---
# We have provided more descriptive names for each topic.
# Keys must exactly match the values in your 'dominant_topic' column (e.g., 'Topic 1', 'Topic 2').
TOPIC_LABELS = {
    'Topic 1': 'Genomics & Genetics (sequencing, virulence, methicillin resistance)',
    'Topic 2': 'Clinical Infections & Patient Management (hospital, treatment, risk)',
    'Topic 3': 'Microbiota & Phages (intestinal, microbial community, mouse)',
    'Topic 4': 'Antimicrobial Activity & Biofilms (antibacterial, cell, effect, protein)',
    'Topic 5': 'Resistance Genes & Plasmids (colistin, carbapenem, multidrug)',
    'Topic 6': 'Antimicrobial Resistance (AMR) & Public Health (use, review, disease)',
    'Topic 7': 'Antimicrobial Peptides (AMPs) & Vaccines (COVID, insight)',
    'Topic 8': 'Tuberculosis & Drug Resistance (mutation, HIV, mycobacterium)',
    'Topic 9': 'Isolates, Susceptibility & Prevalence (strain, E. coli, sample study)',
    'Topic 10': 'Probiotics & Urinary Tract Infections (UTI, defense, treatment failure)'
}

# --- Load the analyzed data ---
df = load_data('./data/analyzed_antibiotic_resistance_data.csv')

# --- Sidebar for filters ---
st.sidebar.header("Analysis Filters")

# Year Range
min_pub_year = int(df['publication_year'].min())
max_pub_year = int(df['publication_year'].max())

selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=min_pub_year,
    max_value=max_pub_year,
    value=(min_pub_year, max_pub_year)
)

# Keyword filter in title/abstract
keyword_filter = st.sidebar.text_input("Filter by keyword (title/abstract):", "").lower()

# LDA Topic Filter
# Get topic keys and sort them numerically
all_topics_sorted_keys = sorted(TOPIC_LABELS.keys(), key=lambda x: int(x.split(' ')[1]))
selected_topics = st.sidebar.multiselect(
    "Filter by LDA Topic:",
    options=all_topics_sorted_keys,
    format_func=lambda x: f"{x}: {TOPIC_LABELS[x]}", # Display descriptive name
    default=all_topics_sorted_keys # Select all by default
)

st.sidebar.subheader("Identified LDA Topics:")
for topic_key, topic_desc in TOPIC_LABELS.items():
    st.sidebar.write(f"**{topic_key}:** {topic_desc}")


# --- Apply Filters ---
filtered_df = df[
    (df['publication_year'] >= selected_years[0]) & 
    (df['publication_year'] <= selected_years[1])
].copy() # Use .copy() to avoid SettingWithCopyWarning

if keyword_filter:
    filtered_df = filtered_df[
        filtered_df['combined_text'].str.contains(keyword_filter, case=False, na=False)
    ]

if selected_topics:
    # Ensure the 'dominant_topic' column has the expected values
    filtered_df = filtered_df[filtered_df['dominant_topic'].isin(selected_topics)]


# --- Main Dashboard Content ---
st.title("PubMed Antibiotic Resistance Trend Analysis")
st.markdown("Explore scientific publications related to antibiotic resistance across years and topics.")

st.subheader(f"Articles Found: {len(filtered_df)}")

if filtered_df.empty:
    st.warning("No articles found with the selected filters. Try adjusting the filters.")
else:
    # --- Chart 1: Publication Volume by Year and Topic (Stacked Bar) ---
    st.subheader("Publication Volume by Year and Topic")
    
    if 'dominant_topic' in filtered_df.columns:
        yearly_topic_counts = filtered_df.groupby(['publication_year', 'dominant_topic']).size().reset_index(name='count')
        # Add descriptive labels
        yearly_topic_counts['dominant_topic_label'] = yearly_topic_counts['dominant_topic'].map(TOPIC_LABELS).fillna('Unknown') # Handle potential missing labels
        
        # Order topics for legend and stacked bars
        # Ensure consistent order in charts
        yearly_topic_counts['dominant_topic_id'] = yearly_topic_counts['dominant_topic'].apply(lambda x: int(x.split(' ')[1]))
        
        chart_topic_volume = alt.Chart(yearly_topic_counts).mark_bar().encode(
            x=alt.X('publication_year:O', title='Publication Year'),
            y=alt.Y('count:Q', title='Number of Articles'),
            color=alt.Color('dominant_topic_label:N', title='LDA Topic', sort=alt.EncodingSortField(field="dominant_topic_id", op="min", order='ascending')),
            order=alt.Order('dominant_topic_id'), # To ensure bars stack in a consistent order
            tooltip=[
                'publication_year:O', 
                alt.Tooltip('dominant_topic_label:N', title='Topic'), 
                'count:Q', 
                alt.Tooltip('dominant_topic:N', title='Original ID') # Also show original ID
            ]
        ).properties(
            title='Publication Volume by Year and LDA Topic'
        ).interactive()
        st.altair_chart(chart_topic_volume, use_container_width=True)
    else:
        st.warning("The 'dominant_topic' column is not available for topic visualization. Please check '3_nlp_analysis.py'.")
        
        # Fallback to a simple yearly count if 'dominant_topic' is missing for the chart
        yearly_counts = filtered_df['publication_year'].value_counts().reset_index()
        yearly_counts.columns = ['publication_year', 'count']
        yearly_counts = yearly_counts.sort_values('publication_year')

        chart_volume = alt.Chart(yearly_counts).mark_bar().encode(
            x=alt.X('publication_year:O', title='Publication Year'),
            y=alt.Y('count:Q', title='Number of Articles'),
            tooltip=['publication_year', 'count']
        ).properties(
            title='Publication Volume by Year'
        ).interactive()
        st.altair_chart(chart_volume, use_container_width=True)


    # --- Chart 2: Articles by Topic (Top 10) ---
    st.subheader("Distribution of Articles by Topic (Top 10)")
    
    if 'dominant_topic' in filtered_df.columns:
        topic_distribution = filtered_df['dominant_topic'].value_counts().reset_index()
        topic_distribution.columns = ['topic', 'count']
        # Map to descriptive labels for the chart
        topic_distribution['topic_label'] = topic_distribution['topic'].map(TOPIC_LABELS).fillna('Unknown') # Handle potential missing labels
        topic_distribution = topic_distribution.sort_values('count', ascending=False)
        
        chart_topic_dist = alt.Chart(topic_distribution).mark_bar().encode(
            x=alt.X('count:Q', title='Number of Articles'),
            y=alt.Y('topic_label:N', sort='-x', title='LDA Topic'), # Sort by count descending
            tooltip=[
                alt.Tooltip('topic_label:N', title='Topic'), 
                'count:Q', 
                alt.Tooltip('topic:N', title='Original ID')
            ]
        ).properties(
            title='Distribution of Articles by LDA Topic'
        ).interactive()
        st.altair_chart(chart_topic_dist, use_container_width=True)
    else:
        st.warning("The 'dominant_topic' column is not available for topic visualization.")

    # --- NEW CHART: Word Cloud of Filtered Articles ---
    st.subheader("Word Cloud of Filtered Articles")
    
    # Check if 'combined_text' column exists and is not empty
    if 'combined_text' in filtered_df.columns and not filtered_df['combined_text'].empty:
        # Combine all relevant text for the word cloud
        text_for_wordcloud = " ".join(filtered_df['combined_text'].dropna().tolist())
        
        if text_for_wordcloud: # Only generate if there is text
            # Create a WordCloud object
            wordcloud = WordCloud(width=800, height=400, background_color='white', collocations=False).generate(text_for_wordcloud)
            
            # Display the WordCloud using Matplotlib
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off') # Do not show axes
            st.pyplot(fig) # Display the plot in Streamlit
            plt.close(fig) # Close the figure to free memory
        else:
            st.info("No text available to generate a word cloud for the current filters.")
    else:
        st.warning("The 'combined_text' column is not available or is empty. Cannot generate word cloud.")

    # --- Display data in table (optional, for debugging or detailed view) ---
    st.subheader("Article Preview")
    st.dataframe(filtered_df[['publication_year', 'title', 'abstract', 'dominant_topic', 'publication_date', 'authors']].head(100))
