# PubMed Antibiotic Resistance Trend Analysis Dashboard

Available at: https://amrtrendanalysis-zoajgryzuojpr3f9atwicc.streamlit.app/

## Project Overview

This project presents an interactive web dashboard developed with Streamlit, designed to analyze and visualize trends in scientific publications related to **Antibiotic Resistance (AR)** sourced from PubMed. Leveraging **Natural Language Processing (NLP)** and **Topic Modeling (LDA)**, this tool provides key insights into research evolution, prevalent themes, and emerging areas within the field of antibiotic resistance.

This dashboard demonstrates my ability to:
* **Acquire and process real-world, unstructured data.**
* **Apply advanced NLP techniques** (including text cleaning, tokenization, and Latent Dirichlet Allocation for topic modeling).
* **Extract meaningful insights** from large text datasets.
* **Develop interactive data visualizations** for clear communication of complex findings.
* **Build deployable data applications.**

## Key Features

* **Interactive Filtering:** Filter publications by publication year range and keywords within titles/abstracts.
* **Dynamic LDA Topic Analysis:** Explore the dominant research themes automatically identified from the text data. Each topic is accompanied by a descriptive label derived from its most prominent keywords.
* **Temporal Trend Visualization:** Observe the evolution of publication volume over time, broken down by identified LDA topics, showcasing shifts in research focus.
* **Topic Distribution Overview:** Understand the overall prevalence of each research topic within the filtered dataset.
* **Word Cloud Generation:** Visualize the most frequent keywords for the currently filtered articles, offering a quick grasp of key terminology.

## Technologies Used

* **Python:** Core programming language.
* **Pandas:** Data manipulation and analysis.
* **Streamlit:** For building the interactive web dashboard.
* **Altair:** Declarative statistical visualizations.
* **NLTK / SpaCy (Implicit via NLP Pipeline):** Text preprocessing (tokenization, stopwords, lemmatization).
* **Gensim (Implicit via NLP Pipeline):** Implementation of Latent Dirichlet Allocation (LDA) for topic modeling.
* **WordCloud:** Generating visual word clouds.
* **Matplotlib:** For displaying Word Clouds.
