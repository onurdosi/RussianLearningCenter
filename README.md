# RussianLearningCenter

RussianLearningCenter is a Django web application designed to help users learn and practice Russian vocabulary in a simple and interactive way.

---

## Project Goal

The goal of this project is to create a personal vocabulary learning tool where users can:

- Store Russian words with translations
- Organize words by difficulty
- Add personal notes for context
- Practice vocabulary using a quiz system
- Track basic learning progress

This project was also developed as part of a final assessment, focusing on both functionality and code quality.

---

## Features

### Vocabulary Management
- Add new words with translation, difficulty, and notes
- Edit existing words
- Delete words with confirmation
- Quick Add multiple words at once (with duplicate detection)

### Search & Filtering
- Search by Russian word or translation
- Filter by difficulty (easy, medium, hard)
- Combined search + filtering

### Practice Mode
- Multiple-choice quiz system
- No repeated words in one session
- Session-based progress tracking
- Final score display
- Optional hints from notes
- Visual feedback (correct = green, wrong = red)

### Statistics
- Total words count
- Words grouped by difficulty
- Displayed on homepage with a clean UI

---

## Technologies Used

- Python
- Django
- SQLite
- HTML
- CSS

---

## How to Run the Project

1. Clone the repository:

```bash
git clone https://github.com/onurdosi/RussianLearningCenter.git
cd RussianLearningCenter