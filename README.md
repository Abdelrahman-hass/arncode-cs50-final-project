# ARNcode – CS50 Final Project

#### Video Demo: [https://youtu.be/tAm0Aluw5mg?si=-UiBiOX9OVN5Va12](https://youtu.be/tAm0Aluw5mg?si=-UiBiOX9OVN5Va12)

---

### Description

ARNcode is a web-based learning platform built using Flask and SQLite. It allows users to create accounts, log in, and access structured course content. Users can also request admin access to manage courses and lessons.

---

### Features

The app features:

- Signup and login functionality.
- Role-based access: users and admins.
- Users can view available courses and lessons after login.
- Admins can:
  - Add/edit/delete courses.
  - Add/edit/delete lessons.
  - View and manage users.
  - Review admin requests (approve/reject/revoke).

The UI is styled with a dark color palette, designed for clarity and accessibility.

---

### Files Overview

- `app.py` – Main app entry point.  
- `models.py` – SQLAlchemy models for Users, Courses, Lessons, AdminRequests.  
- `auth.py`, `admin_routes.py`, `routes.py` – Flask Blueprints for auth, admin, and general views.  
- `templates/` – All HTML templates (login, signup, dashboard, course views, lesson views, etc).  
- `static/styles.css` – Global CSS styling.  
- `README.md` – This file.  

---

### Design Notes

- Users can request admin access via a dedicated form.  
- Admin approval system includes reasons for rejection and revocation.  
- Admins are limited by role: some are full (head admin), others limited (normal admin).  
- Password reset via email is implemented for user convenience.  

The app took approximately **3 weeks** to complete, including learning, design, coding, and video production.