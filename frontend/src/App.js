import React, { useState } from 'react';
import { User, Calendar, Users, BookOpen, Clock, Mail, Star, MapPin } from 'lucide-react';

const CampusConnect = () => {
  const [currentPage, setCurrentPage] = useState('login');
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState({
    courses: [],
    availability: {},
    studyStyle: '',
    groupSize: '',
    location: ''
  });

  // Mock data
  const mockCourses = [
    'CS 101 - Intro to Computer Science',
    'MATH 205 - Calculus II',
    'PHYS 150 - Physics I',
    'CHEM 120 - General Chemistry',
    'ENG 102 - English Composition',
    'HIST 201 - World History',
    'PSYC 101 - Introduction to Psychology',
    'ECON 101 - Microeconomics'
  ];

  const mockMatches = [
    {
      id: 1,
      name: 'Sarah Chen',
      courses: ['CS 101', 'MATH 205'],
      availability: 'Mon 2-4pm, Wed 10-12pm',
      studyStyle: 'Discussion-based',
      compatibility: 95
    },
    {
      id: 2,
      name: 'Marcus Johnson',
      courses: ['PHYS 150', 'MATH 205'],
      availability: 'Tue 1-3pm, Thu 3-5pm',
      studyStyle: 'Quiet study',
      compatibility: 88
    },
    {
      id: 3,
      name: 'Emma Rodriguez',
      courses: ['CS 101', 'PHYS 150'],
      availability: 'Mon 10-12pm, Fri 2-4pm',
      studyStyle: 'Small group',
      compatibility: 92
    }
  ];

  const handleGoogleLogin = () => {
    // Mock Google OAuth
    setUser({
      name: 'Alex Student',
      email: 'alex.student@university.edu',
      avatar: '/api/placeholder/40/40'
    });
    setCurrentPage('profile-setup');
  };

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    setCurrentPage('dashboard');
  };

  const handleCourseToggle = (course) => {
    setProfile(prev => ({
      ...prev,
      courses: prev.courses.includes(course)
        ? prev.courses.filter(c => c !== course)
        : [...prev.courses, course]
    }));
  };

  const handleAvailabilityChange = (day, time) => {
    setProfile(prev => ({
      ...prev,
      availability: {
        ...prev.availability,
        [day]: prev.availability[day]?.includes(time)
          ? prev.availability[day].filter(t => t !== time)
          : [...(prev.availability[day] || []), time]
      }
    }));
  };

  // Login Page
  const LoginPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <Users className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">CampusConnect</h1>
          <p className="text-gray-600">Find your perfect study partner</p>
        </div>
        
        <button
          onClick={handleGoogleLogin}
          className="w-full bg-white border-2 border-gray-200 rounded-lg py-3 px-4 flex items-center justify-center gap-3 hover:bg-gray-50 transition-colors duration-200"
        >
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">G</span>
          </div>
          <span className="text-gray-700 font-medium">Continue with Google</span>
        </button>
        
        <p className="text-xs text-gray-500 text-center mt-4">
          Use your university Google account to sign in
        </p>
      </div>
    </div>
  );

  // Profile Setup Page
  const ProfileSetupPage = () => (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Set Up Your Profile</h2>
          
          <form onSubmit={handleProfileSubmit} div className="space-y-6">
            {/* Course Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select Your Courses
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {mockCourses.map(course => (
                  <button
                    key={course}
                    type="button"
                    onClick={() => handleCourseToggle(course)}
                    className={`text-left p-3 rounded-lg border-2 transition-colors duration-200 ${
                      profile.courses.includes(course)
                        ? 'bg-blue-50 border-blue-200 text-blue-800'
                        : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <BookOpen className="w-4 h-4 inline mr-2" />
                    {course}
                  </button>
                ))}
              </div>
            </div>

            {/* Availability */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                When are you available to study?
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(day => (
                  <div key={day} className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-700 mb-2">{day}</h4>
                    <div className="space-y-2">
                      {['9-11am', '11-1pm', '1-3pm', '3-5pm', '5-7pm'].map(time => (
                        <button
                          key={time}
                          type="button"
                          onClick={() => handleAvailabilityChange(day, time)}
                          className={`w-full text-left p-2 rounded text-sm transition-colors duration-200 ${
                            profile.availability[day]?.includes(time)
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                        >
                          <Clock className="w-3 h-3 inline mr-1" />
                          {time}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Study Preferences */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Study Style
                </label>
                <select
                  value={profile.studyStyle}
                  onChange={(e) => setProfile(prev => ({ ...prev, studyStyle: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select style...</option>
                  <option value="quiet">Quiet study</option>
                  <option value="discussion">Discussion-based</option>
                  <option value="mixed">Mixed approach</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Group Size
                </label>
                <select
                  value={profile.groupSize}
                  onChange={(e) => setProfile(prev => ({ ...prev, groupSize: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select size...</option>
                  <option value="1-on-1">1-on-1</option>
                  <option value="small">Small group (2-3)</option>
                  <option value="large">Large group (4+)</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={profile.courses.length === 0}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
            >
              Find Study Partners
            </button>
          </form>
        </div>
      </div>
    </div>
  );

  // Dashboard Page
  const DashboardPage = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 rounded-full w-10 h-10 flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <h1 className="text-xl font-bold text-gray-800">CampusConnect</h1>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-600">Welcome, {user?.name}</span>
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Your Courses</p>
                <p className="text-2xl font-bold text-gray-800">{profile.courses.length}</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Potential Matches</p>
                <p className="text-2xl font-bold text-gray-800">{mockMatches.length}</p>
              </div>
              <Users className="w-8 h-8 text-green-500" />
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Study Sessions</p>
                <p className="text-2xl font-bold text-gray-800">0</p>
              </div>
              <Calendar className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>

        {/* Matches */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-6 border-b">
            <h2 className="text-xl font-bold text-gray-800">Your Study Matches</h2>
            <p className="text-gray-600">Students who share your courses and availability</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {mockMatches.map(match => (
                <div key={match.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors duration-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">{match.name.charAt(0)}</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-800">{match.name}</h3>
                        <p className="text-sm text-gray-600">
                          Shared courses: {match.courses.join(', ')}
                        </p>
                        <p className="text-xs text-gray-500">
                          Available: {match.availability}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 mb-2">
                        <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        <span className="text-sm font-medium text-gray-700">
                          {match.compatibility}% match
                        </span>
                      </div>
                      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors duration-200">
                        <Mail className="w-4 h-4 inline mr-1" />
                        Connect
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render current page
  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'login':
        return <LoginPage />;
      case 'profile-setup':
        return <ProfileSetupPage />;
      case 'dashboard':
        return <DashboardPage />;
      default:
        return <LoginPage />;
    }
  };

  return renderCurrentPage();
};

export default CampusConnect;
