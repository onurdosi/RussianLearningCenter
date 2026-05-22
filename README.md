# RussianLearningCenter

RussianLearningCenter is a Django web application designed to help users learn and practice Russian vocabulary in a simple and interactive way.

---

## Project Goal

The goal of this project is to create a personal vocabulary learning tool where users can:

- Store Russian words with translations
- Organize vocabulary using custom filters
- Add personal notes for context
- Practice vocabulary using a quiz system
- Practice specific groups of words
- Track basic learning progress

This project was also developed as part of a final assessment, focusing on both functionality and code quality.

---

## Features

### Vocabulary Management
- Add new words with translation, filter, and notes
- Edit existing words
- Delete words with confirmation
- Quick Add multiple words at once
- Duplicate detection
- Optional filters for every word

### Custom Filters
- Users can create custom vocabulary filters
- Words can belong to a filter or remain unfiltered
- Practice specific filters
- Delete filters without deleting words
- Empty filters are automatically removed

### Search & Filtering
- Search by Russian word or translation
- Filter words using custom filters
- View words with no filter
- Combined search + filtering system

### Practice Mode
- Multiple-choice quiz system
- Practice all words
- Practice words from a selected filter
- Practice unfiltered words
- No repeated words in one session
- Session-based progress tracking
- Final score display
- Optional hints from notes
- Visual feedback for correct and incorrect answers

### Statistics
- Total words count
- Total filters count
- Unfiltered words count
- Largest filter displayed on homepage

### User Features
- User authentication system
- User-specific vocabularies
- Profile/settings page
- Password changing
- English/Russian language switching

---

## Technologies Used

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/onurdosi/RussianLearningCenter.git
cd RussianLearningCenter
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install django
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

### 7. Open the website

Open your browser and go to:

```text
http://127.0.0.1:8000/
```

---

## Project Structure

```text
RussianLearningCenter/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── vocab/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── ...
│
├── db.sqlite3
├── manage.py
└── README.md
```

---

## Future Improvements

Possible future improvements include:

- Spaced repetition system
- Audio pronunciation support
- Word tagging system
- Import/export vocabulary
- Mobile-responsive improvements
- Better statistics and analytics
- Flashcard mode
- Dark mode
- AI-generated example sentences

---

## Author

Created by Onur Dosi.