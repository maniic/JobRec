# JobRec: Job Recommendation System

## Introduction

In today’s highly saturated job market, students and job seekers often face significant challenges in identifying job postings that align with their skills. With countless listings available across platforms, the process can quickly become overwhelming and inefficient. JobRec simplifies this process by providing an intelligent recommendation system that matches users to relevant job postings based on their skill sets using graph-based matching techniques.

**Our central project goal is:**  
*How can we design an intelligent job recommendation system that efficiently matches users to relevant job postings based on their skills?*

Users can input up to five skills, which are then compared against the skills mentioned in live job listings fetched from the Findwork.dev API. We model the relationship between skills and job postings as a bipartite graph where one set of nodes represents user-input skills and the other represents job postings. An edge is created between a skill and a job if the job’s description contains that skill, and the connection is weighted by the frequency of the skill's occurrence. The resulting match score is then used to rank job recommendations.

## Features

- **Graph-Based Matching:**  
  Constructs a weighted bipartite graph to model the relationship between user skills and job postings. The graph is built by:
  - Mapping up to five skills (converted to lowercase) as vertices.
  - Creating job nodes based on the job's role and company.
  - Connecting skills and jobs via edges weighted by the frequency of each skill’s appearance in the job descriptions.
  - Providing a fallback mechanism by flagging jobs with "[Low Match]" if no skills are detected.

- **Real-Time Job Listings:**  
  Retrieves live job data via the Findwork.dev API, parsing critical fields including:
  - `role`, `company_name`, `location`, `employment_type`, `description`, `text`, `date_posted`, and `url`.

- **Dual Interfaces:**  
  - **Command-Line Interface (CLI):** Run the backend script to test the system via terminal prompts.
  - **Graphical User Interface (GUI):** A Tkinter-based desktop application that offers a responsive, dark-mode interface with input validation, background processing, and detailed, color-coded job recommendations.

## Datasets and API Details

- **Primary Data Source:**  
  The Findwork.dev API ([https://findwork.dev/](https://findwork.dev/)) returns job listings in JSON format. Key data fields extracted include:
  - **Role:** Job title.
  - **Company Name:** Hiring organization.
  - **Location:** Job location.
  - **Employment Type:** e.g., full time, contract, part time.
  - **Job Description:** Combined content from `description` and `text` fields.
  - **Date Posted:** Listing date.
  - **URL:** Direct link to the full job posting.

- **Preprocessing:**  
  The system extracts and normalizes these fields (converting text to lowercase) to facilitate reliable matching against the user’s input skills.

## Computational Overview

The project is divided into two primary modules:

1. **Backend (JobrecBackend.py):**
   - **API Interaction:** Uses the `fetch_jobs` function to send GET requests to the Findwork.dev API.
   - **Graph Construction:** The `build_graph` function creates a weighted bipartite graph connecting skills and job postings.
   - **Recommendation Logic:** The `recommend_jobs` function computes match scores for each job and returns a sorted list of top job recommendations.
   - **Helper Functions:**  
     - `load_api_key`: Loads the API key from a `.env` file.
     - `prompt_skills`: Allows users to input up to five skills in the CLI mode.

2. **Frontend (JobRecFrontend.py):**
   - **Interactive GUI:** Built using Tkinter for a user-friendly experience.
   - **Skill Input and Validation:** Collects user skills through text fields and provides error handling if no skills are entered.
   - **Background Processing:** Utilizes threading to keep the GUI responsive while fetching and processing job data.
   - **Result Display:** Presents job recommendations in a popup window with details such as location, employment type, posting date, and a color-coded match level.
   - **Reset Functionality:** Allows users to clear input fields and perform new searches easily.

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/maniic/JobRec.git
    cd JobRec
    ```

2. **Set Up a Virtual Environment and Install Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **API Key Setup:**
   - Create a file named `.env` in the project root.
   - Add your Findwork.dev API key in the following format:
     ```ini
     FINDWORK_API_KEY=your_api_key_here
     ```
   - Ensure the `.env` file is in the same directory as both `JobrecBackend.py` and `JobRecFrontend.py`.

## Running the Program

### Command-Line Interface (CLI)

Run the backend script to use the CLI version:
```bash
python JobrecBackend.py
Follow the on-screen prompts to enter up to five skills and view your job recommendations along with match scores (High, Medium, or Low).

Graphical User Interface (GUI)
Launch the GUI by running:

bash
Copy
python JobRecFrontend.py

In the GUI:

Enter Skills: Input up to five skills in the designated text fields.

Search for Jobs: Click the "🚀 Find Jobs" button.

View Recommendations: A popup window will display the top five recommended jobs with details such as location, employment type, and posting date.

Reset Search: Use the "🔄 Search Again" button to clear inputs and perform a new search.

Discussion and Future Work
JobRec demonstrates that a simple, skill-based job recommendation system can effectively leverage graph-based matching to provide tailored job opportunities. Key observations include:

Effectiveness of Graph Structures: Using a weighted bipartite graph allows clear quantification of job relevance.

User-Centric Design: Transitioning from a CLI to a fully interactive GUI improves accessibility and usability.

Limitations:

The unstructured nature of the API data can limit match quality.

Vocabulary mismatches (e.g., synonyms) may lead to missed matches.

Future enhancements could include semantic analysis, improved filtering (e.g., by location), and advanced feedback mechanisms.

License
This project is licensed under the MIT License – see the LICENSE file for details.

Acknowledgments
Findwork.dev: For providing the job listings API.

Open-Source Communities: For libraries and resources that enabled rapid development.

References
Findwork.dev. “Findwork API Documentation.” Available at: https://findwork.dev/api/

Python Software Foundation. “Tkinter — Python interface to Tcl/Tk.” Available at: https://docs.python.org/3/library/tkinter.html

NetworkX Developers. “NetworkX: High-productivity software for complex networks.” Available at: https://networkx.org/

Plotly Technologies Inc. “Plotly Python Graphing Library.” Available at: https://plotly.com/python/

Bensaid, S. “python-dotenv: Load environment variables from .env.” GitHub repository. Available at: https://github.com/theskumar/python-dotenv
