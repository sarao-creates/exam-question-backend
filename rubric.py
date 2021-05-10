import db
import json
from bottle import response, request

class Rubric:

    def __init__(self, id, rubric_text, points, qid):
        '''Constructor'''
        self.id = id
        self.rubric_text = rubric_text
        self.points = points
        self.qid = qid

    def update(self):
        '''Writes back instance values into database'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Rubric SET rubric_text = ?, points = ?, qid = ? WHERE id = ?",
                               (self.rubric_text, self.points, self.qid, self.id))
            conn.commit()
        
    def updateFromJSON(self, rubric_data):
        '''Unpack JSON representation to update instance variables and then
           calls update to write back into database'''
        
        self.rubric_text = rubric_data['rubric_text']
        self.points = rubric_data['points']
        self.qid = rubric_data['qid']
        self.update()

    def delete(self):
        '''Deletes instance from database, any object representations of the
           instance are now invalid and shouldn't be used including this one'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Rubric WHERE id = ?", (self.id, ))

    
    def jsonable(self):
        '''Returns a dict appropriate for creating JSON representation
           of the instance'''
        
        return {'id': self.id, 'rubric_text': self.rubric_text, 'points': self.points, 'qid': self.qid}

    @staticmethod
    def createFromJSON(rubric_data):
        '''Creates new instance object using dict created from JSON representation
           using create'''
        
        # Unpack the instance data from JSON
        # Should validate information here and throw exception
        # if something is not right.
        rubric_text = rubric_data['rubric_text']
        points = rubric_data['points']
        qid = rubric_data['qid']

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Rubric (rubric_text, points, qid) VALUES (?, ?, ?)",
                               (rubric_text, points, qid))
            conn.commit()
        return Rubric.find(cursor.lastrowid)

    @staticmethod
    def find(id):
        '''If row with specified id exists, creates and returns corresponding ORM
           instance. Otherwise Exception raised.'''
        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Rubric WHERE id = ?", (id,))
            row = cursor.fetchone()

        if row is None:
            raise Exception(f'No such Rubric with id: {id}')
        else:
            return Rubric(row['id'], row['rubric_text'], row['points'], row['qid'])

    @staticmethod
    def getAllIDs():        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Rubric")
            all_ids = [row['id'] for row in cursor]
        return all_ids
        
    @staticmethod
    def setupBottleRoutes(app):
        @app.get('/rubric')
        def getRubricIndex():
            rubric_index = Rubric.getAllIDs()
            response.content_type = 'application/json'
            return json.dumps(rubric_index)
            
        @app.get('/rubric/<id>')
        def getRubric(id):
            try:
                rubric = Rubric.find(id)
            except Exception:
                response.status = 404
                return f"Rubric {id} not found"
            return rubric.jsonable()
        
        @app.post('/rubric')
        def postRubric():
            rubric = Rubric.createFromJSON(request.json)
            return rubric.jsonable()

        @app.put('/rubric/<id>')
        def updateRubric(id):
            '''Implements instance updating'''
    
            try:
                rubric = Rubric.find(id)
            except Exception:
                response.status = 404
                return f"Rubric {id} to update not found"

            rubric.updateFromJSON(request.json)
            return rubric.jsonable()

        @app.delete('/rubric/<id>')
        def deleteRubric(id):
            '''Implements instance deletion'''
    
            try:
                rubric = Rubric.find(id)
            except Exception:
                response.status = 404
                return f"Rubric {id} to delete does not exist"

            rubric.delete()
    
            response.content_type = 'application/json'
            return json.dumps(True)

