# Russian Learning Center

Russian Learning Center is a modular Django-based adaptive language learning platform designed to help users build and practice personalized Russian vocabulary in a calm, intelligent, and user-focused environment.

Unlike traditional flashcard systems, this project focuses on:
- adaptive review behavior
- intelligent vocabulary prioritization
- personalized learning flow
- meaningful word organization
- maintainable software architecture

The application was originally developed as a Python/Django project for the MIPT Master's program and evolved into a scalable adaptive learning platform.

---

# Live Website

Live deployed version:

```text
https://onurdosi.pythonanywhere.com/
```

---

# Project Philosophy

This project intentionally avoids:
- fake gamification
- meaningless streak systems
- dopamine-driven productivity mechanics
- cluttered dashboards

Instead, the platform focuses on:
- calm educational UX
- adaptive learning behavior
- intelligent review scheduling
- long-term maintainability
- personalized vocabulary learning

The goal is to create a system that behaves more like a personal learning companion than a traditional flashcard application.

---

# Core Features

## User Authentication System

- User registration
- Login/logout system
- User-specific vocabularies
- Secure profile management
- Password change functionality

---

# Vocabulary Management

Users can fully manage their personal vocabulary library.

Features include:
- Add words individually
- Edit existing words
- Delete words with confirmation
- Add personal notes
- Store translations
- Quick Add multiple words simultaneously
- Duplicate detection
- User-specific data isolation

---

# Custom Filter System

Vocabulary can be organized into custom categories.

Features:
- Create custom filters
- Edit filters
- Delete filters
- Delete filters while preserving words
- Delete filters together with all contained words
- Practice words from specific filters
- Practice unfiltered vocabulary
- Automatic empty-filter cleanup

Examples:
- Travel
- Business
- Literature
- Family
- Difficult Words

---

# Quick Add System

The application supports rapid vocabulary importing.

Features:
- Add multiple words at once
- Add multiple translations at once
- Automatic validation
- Matching-count verification
- Optional filter assignment
- Optional automatic filter creation

Example:

Russian words:
```text
привет, вода, дом
```

Translations:
```text
hello, water, house
```

---

# Adaptive Practice System

The project no longer uses simple random practice selection.

Practice Mode now behaves as an adaptive learning system.

The application tracks:
- learning performance
- interaction behavior
- review history
- practice frequency
- mistakes
- memory reinforcement

The system intelligently prioritizes:
- weak vocabulary
- neglected vocabulary
- unseen words
- due-for-review words

while reducing:
- excessive repetition
- frustrating spam loops
- overexposure to recent mistakes

---

# Intelligent Review Scheduling

The project includes a lightweight spaced-review architecture.

Each word stores:
- next review timestamp
- current review interval
- practice history
- mistake history

Correct answers:
- increase review interval
- delay next appearance

Incorrect answers:
- reset interval
- schedule earlier review

This allows the system to gradually simulate:
- memory reinforcement
- adaptive spacing
- personalized review timing

---

# Practice Mode Features

## Multiple Choice Practice

Users can:
- Practice all vocabulary
- Practice selected filters
- Practice only unfiltered words

Features:
- Smart adaptive selection
- Intelligent weighting system
- No repeated words in one session
- Session progress tracking
- Final score display
- Notes/hints support
- Correct/incorrect answer feedback
- Adaptive review scheduling

---

# Learning Analytics System

The application tracks detailed vocabulary learning behavior.

Tracked metrics include:

## Interaction Analytics
- Word detail panel opens
- Practice appearances
- Correct answers
- Incorrect answers

## Learning Timestamps
- Last practiced time
- Last mistake time
- Next scheduled review

## Adaptive Data
- Review intervals
- Practice weighting
- Learning history

---

# Homepage Experience

The homepage was intentionally designed to feel:
- calm
- educational
- meaningful
- personal

Instead of functioning as a productivity dashboard, it provides:
- lightweight learning analytics
- educational atmosphere
- creator message
- quote of the day section
- adaptive learning context

The design intentionally avoids:
- streak systems
- achievement spam
- aggressive gamification
- distracting productivity mechanics

---

# Homepage Analytics Dashboard

The homepage includes lightweight educational analytics.

Features:
- Total word count
- Total filter count
- Percentage of practiced words
- Most mistaken vocabulary
- Most recently mistaken vocabulary
- Most opened vocabulary
- Quote of the Day section
- Creator message section
- Creator contact section
- Clean educational UI

---

# Statistics Reset System

Users can reset learning statistics without deleting vocabulary.

Resettable data:
- Practice counters
- Mistake counters
- Interaction counters
- Timestamps
- Review scheduling data

Preserved data:
- Words
- Filters
- Notes

---

# Multilingual Interface

The application supports:
- English interface
- Russian interface

Features:
- Dynamic language switching
- Session-based language persistence

---

# Adaptive Learning Architecture

The application architecture now supports:
- future spaced repetition systems
- review queues
- adaptive review difficulty
- AI-assisted learning systems
- contextual vocabulary systems
- semantic clustering
- future intelligent scheduling systems

without requiring major rewrites.

---

# Software Architecture

The project was heavily refactored into a modular Django architecture.

The application follows:

```text
thin views
fat services
```

Meaning:
- views handle requests/responses
- services contain reusable business logic

---

# Current Project Structure

```text
RussianLearningCenter/
│
├── config/
│
├── vocab/
│   ├── migrations/
│   ├── services/
│   ├── tests/
│   ├── views/
│   ├── templates/pages/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   ├── constants.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── admin.py
│
├── manage.py
└── README.md
```

---

# Services Layer

Business logic is separated into reusable services.

Current services include:

## language_service.py
- language management
- language helper functions

## filter_service.py
- automatic filter cleanup

## statistics_service.py
- analytics tracking
- statistics reset system

## practice_service.py
- adaptive practice weighting
- review scheduling
- smart word selection
- answer generation
- practice utilities

---

# Views Refactor

The project no longer uses a monolithic `views.py`.

Views are separated into modules:

```text
auth_views.py
dashboard_views.py
word_views.py
filter_views.py
practice_views.py
settings_views.py
analytics_views.py
```

This improves:
- readability
- maintainability
- scalability
- testing

---

# Testing

The project includes modularized tests.

Current test structure:

```text
tests/
├── test_forms.py
├── test_words.py
├── test_filters.py
└── test_practice.py
```

Verified systems:
- authentication
- vocabulary CRUD
- filters
- practice mode
- analytics tracking
- adaptive practice behavior
- review scheduling

---

# Code Quality

## Test Coverage

Current coverage:
```text
75%
```

## Pylint Score

Current pylint score:
```text
9.34 / 10
```

The project emphasizes:
- maintainable code
- modular structure
- scalable architecture
- reusable logic
- professional code organization

---

# Technologies Used

## Backend
- Python
- Django
- SQLite

## Frontend
- HTML
- CSS
- JavaScript

## Architecture
- Service-layer architecture
- Session-based adaptive logic
- Modular Django application structure

---

# Future Development Possibilities

Potential future systems include:
- stronger spaced repetition
- semantic vocabulary clustering
- AI-generated example sentences
- AI-generated contextual exercises
- intelligent review queues
- adaptive difficulty systems
- smarter distractor generation
- advanced memory modeling

---

# Installation Guide

## 1. Clone the repository

```bash
git clone https://github.com/onurdosi/RussianLearningCenter.git
cd RussianLearningCenter
```

---

## 2. Create virtual environment

```bash
python -m venv venv
```

---

## 3. Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 4. Install dependencies

```bash
pip install django
```

Optional development tools:

```bash
pip install coverage pylint pylint-django
```

---

## 5. Run migrations

```bash
python manage.py migrate
```

---

## 6. Start development server

```bash
python manage.py runserver
```

---

## Running Tests

## Run Django tests

```bash
python manage.py test
```

## Run coverage report

```bash
coverage run manage.py test
coverage report
```

## Run pylint

```bash
pylint --load-plugins pylint_django vocab
```

---

# Author

Created by Onur Dosi.

MIPT Master's Program Project.

Dedicated to the creator's sister and girlfriend.

Contact:
```text
onurdosiyev@gmail.com
```