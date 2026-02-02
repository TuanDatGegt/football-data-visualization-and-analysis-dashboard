# Football Data Visualization & xG Analysis Dashboard

## Overview
This project focuses on building a **data-driven decision support system** for football analytics, with an emphasis on **data processing, system design, model deployment, and analytical visualization**.  
The system transforms raw soccer event data into structured datasets, applies machine learning models to estimate Expected Goals (xG), and delivers insights through an interactive dashboard.

The implementation prioritizes **data quality, scalability, and interpretability**, making it suitable for analytical and digital transformation use cases.

---

## Chapter 3 – Data Processing & Exploratory Data Analysis

### Data Source
- Soccer event data provided by **Wyscout** (via Kaggle)
- Spatio-temporal events including passes, shots, duels, and ball movements
- Each event contains time, team, player, and spatial coordinates (x, y)

### Data Architecture & Storage
- Designed a **relational database schema** using **SQL Server**
- Normalized event data into structured tables (events, players, teams, tags)
- Implemented secure and reusable database connections via **SQLAlchemy**
- Centralized SQL queries to ensure data consistency and integrity

### Data Extraction & Transformation
- Built SQL queries to aggregate and enrich raw event data
- Cleaned invalid or missing spatial coordinates
- Transformed coordinate systems into standardized pitch dimensions
- Engineered spatio-temporal features (distance to goal, shot angle, context tags)

### Exploratory Data Analysis (EDA)
- Analyzed distributions of shot locations, shot types, and match contexts
- Identified tactical patterns affecting goal-scoring probability
- Quantified the impact of different situations (open play, set pieces, corners)
- Generated analytical visualizations to validate feature relevance and data quality

### Outcome
- Delivered **clean, analysis-ready datasets**
- Ensured data reliability for downstream modeling and dashboard visualization
- Established a reusable data pipeline for future extensions

---

## Chapter 4 – Model Deployment & Dashboard Development

### Expected Goals (xG) Modeling
- Framed xG as a **binary classification problem**
- Implemented and compared three models:
  - Logistic Regression (baseline, high interpretability)
  - Random Forest (primary predictive model)
  - Support Vector Machine (edge-case analysis)
- Evaluated models using Log-Loss and AUC-ROC
- Selected models based on the trade-off between accuracy and explainability

### Dashboard System
- Developed an **interactive analytical dashboard** using Python Dash
- Integrated model outputs with match-level and event-level statistics
- Enabled user interactions:
  - Match and team filtering
  - Shot map visualization
  - xG comparison and tactical insights
- Combined statistical views with **pseudo video tracking** reconstructed from event data

### System Role
- Acts as a **Decision Support System (DSS)** for tactical and performance analysis
- Bridges raw data, machine learning models, and business-oriented insights

---

## Chapter 5 – Conclusions & Future Development

### Key Contributions
- Built a complete **data pipeline from raw events to decision-ready insights**
- Demonstrated how structured data and analytics can support tactical evaluation
- Provided a scalable foundation for football data analysis systems

### Limitations
- Event data lacks off-ball player movement
- Video tracking is reconstructed and approximate
- Model performance depends on data coverage and labeling quality

### Future Enhancements
- Integrate real video-based tracking data
- Develop an end-to-end pipeline from video to analytics
- Expand dashboard features to player-level and team-level analysis
- Optimize data storage using columnar formats (e.g., Apache Parquet)

---

## Tech Stack
- **Data Processing:** Python, Pandas, NumPy
- **Database:** SQL Server, SQLAlchemy
- **Machine Learning:** Scikit-learn
- **Visualization:** Dash, Matplotlib, Plotly
- **Version Control:** Git

---

## Repository Structure

