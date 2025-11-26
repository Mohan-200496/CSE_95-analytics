# Contributing to CSE_95 Analytics

Thank you for your interest in contributing to the Punjab Rozgar Analytics Portal! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs
- Provide detailed information about the issue
- Include steps to reproduce the problem
- Specify your environment (OS, browser, Python version)

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Provide use cases and examples
- Consider the impact on existing functionality

### Submitting Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Update documentation
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git
- Code editor (VS Code recommended)

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/CSE_95-analytics.git
cd CSE_95-analytics

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend/api
npm install  # if package.json exists

# Run development servers
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Frontend API
node server.js
```

## 📋 Code Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Use async/await for database operations
- Example:
```python
async def get_user_by_id(user_id: str, session: AsyncSession) -> Optional[User]:
    """
    Retrieve a user by their ID.
    
    Args:
        user_id: The unique user identifier
        session: Database session
        
    Returns:
        User object if found, None otherwise
    """
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()
```

### JavaScript (Frontend)
- Use ES6+ features (const/let, arrow functions, async/await)
- Follow camelCase naming convention
- Add JSDoc comments for functions
- Use meaningful variable names
- Example:
```javascript
/**
 * Tracks user interaction events
 * @param {string} eventName - Name of the event
 * @param {Object} properties - Event properties
 * @returns {Promise<void>}
 */
async trackEvent(eventName, properties = {}) {
    const eventData = {
        event_name: eventName,
        timestamp: new Date().toISOString(),
        properties
    };
    
    await this.sendEvent(eventData);
}
```

### Database
- Use descriptive table and column names
- Add proper indexes for query performance
- Use foreign key constraints where appropriate
- Document model relationships

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests
```bash
# Add tests for JavaScript functions
# Use Jest or similar testing framework
```

### Manual Testing
- Test all user flows (registration, login, job search, application)
- Verify mobile responsiveness
- Check analytics tracking functionality
- Test error handling and edge cases

## 📝 Documentation

### Code Documentation
- Add docstrings to all Python functions
- Include JSDoc comments for JavaScript functions
- Update README.md for new features
- Update API documentation for new endpoints

### Commit Messages
Follow conventional commit format:
```
type(scope): description

Examples:
feat(auth): add password reset functionality
fix(jobs): resolve search filter bug
docs(readme): update installation instructions
style(frontend): improve mobile navigation
test(backend): add user registration tests
```

## 🎯 Project Areas

### High Priority Areas
- **Authentication & Security**: Improve JWT handling, add OAuth
- **Analytics Engine**: Enhance real-time processing
- **Mobile Experience**: Optimize for mobile devices
- **Performance**: Database query optimization
- **Testing**: Increase test coverage

### Specialized Areas
- **Government Integration**: PGRKAM portal connectivity
- **Machine Learning**: Job recommendation algorithms
- **Data Visualization**: Advanced Chart.js implementations
- **DevOps**: CI/CD pipeline improvements

## 🔍 Review Process

### Pull Request Review
- Code functionality and correctness
- Performance impact assessment
- Security considerations
- Documentation completeness
- Test coverage
- Code style compliance

### Review Timeline
- Initial response: Within 2-3 days
- Full review: Within 1 week
- Feedback incorporation: Ongoing discussion

## 🏷️ Labels and Workflow

### Issue Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `priority: high` - High priority issue
- `priority: low` - Low priority issue

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🌟 Recognition

### Contributors
- All contributors will be recognized in the project
- Significant contributions may be highlighted in releases
- Consider writing blog posts about major features

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional communication

## 📞 Getting Help

### Communication Channels
- GitHub Issues for bug reports and feature requests
- GitHub Discussions for questions and ideas
- Code review comments for specific feedback

### Mentorship
- New contributors are welcome to ask questions
- Core maintainers available for guidance
- Pair programming sessions for complex features

## 📚 Resources

### Learning Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Modern JavaScript Guide](https://javascript.info/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

### Project-Specific Resources
- API Documentation: `http://localhost:8000/docs`
- Database Schema: `backend/app/models/`
- Frontend Components: `frontend/pages/`
- Analytics Engine: `backend/app/analytics/`

Thank you for contributing to CSE_95 Analytics! 🚀