# CampusConnect Study Buddy App

A web application that connects college students with study partners based on shared courses, availability, and study preferences.

## Problem Statement

Students struggle to find compatible study partners in their courses, often studying alone or in mismatched groups. CampusConnect solves this by automatically matching students based on course enrollment, schedule compatibility, and learning preferences.

## Features

### Core MVP Features
- **Google OAuth Authentication** - Secure sign-in with university Google accounts
- **Profile Setup** - Course selection, time availability, and study preferences
- **Smart Matching** - Algorithm matches students based on overlapping courses, schedules, and study styles
- **Dashboard** - View potential study partners and confirmed matches
- **Email Confirmations** - Optional email notifications for confirmed study sessions

### Target Users
- College students seeking study partners
- Students enrolled in challenging courses requiring collaborative study
- Users comfortable with Google-based authentication

## Technical Architecture

### Tech Stack
- **Frontend**: React.js with responsive design
- **Backend**: Node.js/Express or Python/Flask
- **Database**: PostgreSQL or MongoDB
- **Authentication**: Google OAuth 2.0
- **Email Service**: SendGrid or similar
- **Deployment**: Vercel/Netlify (frontend), Heroku/Railway (backend)

### Database Schema

```sql
-- Users table
Users (
  id, email, name, google_id, created_at, updated_at
)

-- Courses table
Courses (
  id, course_code, course_name, university
)

-- User-Course associations
UserCourses (
  user_id, course_id, semester, year
)

-- Availability tracking
Availability (
  user_id, day_of_week, start_time, end_time
)

-- Study preferences
StudyPreferences (
  user_id, group_size, study_style, location_preference, notes
)

-- Study matches
StudyMatches (
  id, user1_id, user2_id, course_id, status, created_at
)
```

## User Flow

1. **Sign-In** - User authenticates via Google OAuth
2. **Profile Setup** - User completes profile with:
   - Course selections (dropdown or manual entry)
   - Weekly availability (time slots per day)
   - Study preferences (group size, quiet vs. discussion, location)
3. **Matching** - Backend algorithm finds compatible study partners
4. **Dashboard** - User views potential matches and confirmed study sessions
5. **Connect** - Users confirm matches and receive email notifications

## Matching Algorithm

The system matches users based on:
- **Course Overlap** - Must share at least one course
- **Time Compatibility** - Overlapping availability windows
- **Study Style** - Compatible preferences (quiet vs. discussion, group size)
- **Priority Score** - Recent activity, course difficulty, match history

## API Integrations

### Required APIs
- **Google OAuth 2.0** - User authentication
- **Google Calendar API** - Optional calendar integration
- **Email Service** - Match notifications (SendGrid/Mailgun)

### Optional APIs
- **University Course Catalog** - Automated course data
- **Campus Map API** - Study location suggestions

## Installation & Setup

### Prerequisites
- Node.js 18+ or Python 3.8+
- PostgreSQL or MongoDB
- Google Cloud Console project with OAuth credentials

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost/campusconnect

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Email Service
SENDGRID_API_KEY=your_sendgrid_key

# App Settings
JWT_SECRET=your_jwt_secret
FRONTEND_URL=http://localhost:3000
```

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/campusconnect
cd campusconnect

# Backend setup
cd backend
npm install
npm run dev

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

## Project Structure

```
campusconnect/
├── backend/
│   ├── routes/
│   │   ├── auth.js
│   │   ├── users.js
│   │   ├── courses.js
│   │   └── matches.js
│   ├── models/
│   ├── middleware/
│   └── server.js
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── utils/
│   └── public/
├── database/
│   └── migrations/
└── README.md
```

## Key Risks & Mitigation

### Technical Risks
- **OAuth Integration Complexity** - Use established libraries (passport.js, react-oauth)
- **Matching Algorithm Performance** - Implement efficient database queries with indexing
- **Email Delivery** - Use reliable service (SendGrid) with fallback options

### User Experience Risks
- **Vague Time Selection** - Provide clear time slot options (hourly blocks)
- **Messy Course Input** - Implement autocomplete and validation
- **Low User Adoption** - Focus on single university for initial launch

## Success Metrics

- **User Registration** - 50+ students sign up during beta
- **Match Success Rate** - 70% of matches result in confirmed study sessions
- **User Retention** - 60% of users return within one week
- **Technical Performance** - <2 second load times, 99% uptime

## Development Timeline (1 Week)

### Days 1-2: Foundation
- Set up project structure
- Implement Google OAuth
- Create basic database schema

### Days 3-4: Core Features
- Build user profile system
- Implement matching algorithm
- Create dashboard UI

### Days 5-6: Integration
- Connect frontend to backend
- Add email notifications
- Testing and bug fixes

### Day 7: Deployment
- Deploy to production
- Final testing
- Documentation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Team: Ohi, Darlene, William
GitHub: @Ohimoiza1205

---

*Built for college students to enhance collaborative learning and academic success.*# CampusConnect
