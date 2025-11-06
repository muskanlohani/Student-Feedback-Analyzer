# 📚 Student Feedback Analyzer

A **beginner-friendly Python project** that collects, stores, and analyzes student feedback using:

-   🗄️ **MySQL** – for database storage
-   🌐 **Streamlit** – for interactive UI
-   🤖 **Google Gemini AI** – for sentiment analysis & automated summaries
-   🎨 **WordCloud + Charts** – for data visualization

---

## 🚀 Features

-   ✅ **Feedback Submission** – Students can enter name, subject, rating, and comments.
-   ✅ **Database Integration** – Feedback stored securely in a MySQL database.
-   ✅ **Dashboard**:

    -   View all feedback in tabular format.
    -   See **average rating per subject** in bar charts.
    -   **Subject-wise Analysis** with:

        -   Word Cloud of comments
        -   AI-powered Sentiment Analysis (Positive/Negative/Neutral)
        -   AI-generated Summary of all feedback

---

## 🏗️ Project Architecture

```text
+----------------+       +------------------+       +-------------------+
|  Streamlit UI  | <-->  |  MySQL Database  | <-->  |   Data Storage    |
+----------------+       +------------------+       +-------------------+
        |
        v
+----------------+       +---------------------------+
|  WordCloud &   |       |   Google Gemini AI API    |
|  Charts        | <-->  | (Sentiment + Summarizer)  |
+----------------+       +---------------------------+
```

---

## ⚙️ Tech Stack

-   **Language**: Python
-   **Framework**: Streamlit
-   **Database**: MySQL
-   **Visualization**: Matplotlib, WordCloud
-   **AI**: Google Gemini (via Google AI Studio API)

---

## 📂 Project Structure

```
student-feedback-analyzer/
│
├── app.py               # Main Streamlit app
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API key, DB creds)
└── README.md            # Project documentation
```

---

## 📦 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/arunishrajput/student-feedback-analyzer.git
cd student-feedback-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt** should include:

```txt
streamlit
mysql-connector-python
pandas
matplotlib
wordcloud
python-dotenv
google-genai
```

### 3. Setup MySQL Database

```sql
CREATE DATABASE feedback_db;
USE feedback_db;

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100),
    subject VARCHAR(100),
    rating INT,
    comments TEXT,
    date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```ini
# Google Gemini API Key
GEMINI_API_KEY=your_google_ai_studio_api_key_here

# MySQL Config
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=feedback_db
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## 🎮 Usage Flow

1. **Submit Feedback**

    - Enter Name, Subject, Rating, Comments
    - Data saved to MySQL

2. **Dashboard**

    - View all raw feedback in a table
    - See average ratings (per subject)
    - Choose a subject → WordCloud + Sentiment + AI Summary

---

## 📊 Example Output

-   **Word Cloud**

-   **Average Ratings**

```text
Physics        4.2
Chemistry      3.8
Mathematics    4.5
```

-   **Sentiment Counts (Chemistry)**

```json
{
    "Positive": 12,
    "Negative": 3,
    "Neutral": 5
}
```

-   **AI Summary Example**

> “Most students appreciated the clarity of explanations.
> A few suggested more real-world examples.
> Overall feedback is positive with some scope for improvement.”

---

## 💡 Future Improvements

-   🔐 Add login system (students/teachers)
-   📤 Export reports (PDF/Excel)
-   📈 Compare subject feedback across semesters
-   🎤 Voice-based feedback submission

---

## 🎤 Demo Script (for presentation)

See 👉 [Demo Script Guide](./Demo.md) _(extra file for classroom presentation)_

---

## 👨‍💻 Author

-   **Arunish** (CSE Student, 1st Year)
