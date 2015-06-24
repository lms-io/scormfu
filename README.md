Organization
Course
Registration
User

Users can
1) CRUD courses
2) CRUD users 
3) CRUD registrations

api/<org>/course/<id>
api/<org>/user/<id>
api/<org>/registration/<id>

4) Assign registrations to courses
api/<org>/assign/<id>/<course>/<registration>
api/<org>/unassign/<id>/<course>/<registration>

5) View responses by registration
api/<org>/registration/<registration>/extract

6) View responses by course
api/<org>/course/<id>/<course>/extract

Registrations can
1) Track answers to a course 
api/<org>/track/<registration>/<course>

2) View their own responses 
api/<org>/registration/<registration>/<course>/extract

3) View their courses
api/<org>/course/<registration>/list

