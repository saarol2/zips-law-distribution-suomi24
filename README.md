# Zipf's Law Distribution and Suomi24 Corpus Analysis

# Authors

Oliver Saari - oliver.saari@student.oulu.fi

Janne Tuikka - janne.tuikka@student.oulu.fi


This project investigates various facets of Zipf's law and empirically tests it on the Finnish Suomi24 corpus. The analysis focuses on hate speech detection, sentiment evolution, and linguistic patterns in Finnish online discussions from 2001-2017. Tasks 1 & 2 are implemented in parse_suomi24.py, and the analysis tasks (3-10) are located in the suomi24_analysis.ipynb file.

## Project Overview

This comprehensive analysis examines the Suomi24 corpus to understand:
- Temporal evolution of hate speech vs. friendly speech
- Vocabulary growth patterns following Heap's law
- Sentiment analysis using Finnish lexicons
- Word frequency distributions and their visualization

## Dataset

The project uses **The Suomi24 Corpus 2001-2017, VRT version 1.1** (71GB) containing Finnish online forum discussions. The data is available through:
- [META-SHARE repository](http://urn.fi/urn:nbn:fi:lb-2020021802)

## Project Structure

```
├── suomi24_analysis.ipynb     # Main analysis notebook
├── docker-compose.yml         # PostgreSQL database setup
├── dockerfile                 # Docker configuration
├── app/
│   ├── main.py               # Data processing scripts
│   ├── parse_suomi24.py      # Corpus parsing utilities
│   └── requirements.txt      # Python dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Docker and Docker Compose
- Minimum 70GB free disk space

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/saarol2/zips-law-distribution-suomi24.git
cd zips-law-distribution-suomi24
```

### 2. Install Python Dependencies
```bash
pip install -r app/requirements.txt
```

### 3. Environment Variables
Include these environment variables in your `.env` file:

POSTGRES_USER=postgres  
POSTGRES_PASSWORD=secret  
POSTGRES_DB=suomi24  
POSTGRES_PORT=5432  
ZIP_LOCATION=/absolute/or/relative/path/to/suomi24.zip  

> Replace `ZIP_LOCATION` with the correct path to your downloaded Suomi24 ZIP file.

### 4. Set up Database
```bash
# Start PostgreSQL with Docker
docker-compose up -d

# Import data (after downloading Suomi24 corpus). The dataset is massive, so this may take hours.
python app/main.py
```

## Usage

### Running the Analysis

1. **Data Import**: First, parse and import the Suomi24 corpus into PostgreSQL.
2. **Execute Notebook**: Run `suomi24_analysis.ipynb` in Jupyter/VS Code
3. **View Results**: The notebook generates all visualizations and statistical analyses

## Technical Implementation

### Libraries Used
- **Data Processing**: pandas, numpy
- **Database**: SQLAlchemy, PostgreSQL, psycopg2
- **NLP**: NLTK (Finnish stopwords)
- **Visualization**: matplotlib, seaborn, wordcloud
- **Statistics**: scikit-learn (linear regression, R-squared)