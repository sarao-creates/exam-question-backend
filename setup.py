import db
import json
from bottle import response, request

class Setup:

    def __init__(self, id, setup_text):
        '''Constructor'''
        self.id = id
        self.setup_text = setup_text

    def update(self):
        '''Writes back instance values into database'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Setup SET setup_text = ? WHERE id = ?",
                               (self.setup_text, self.id))
            conn.commit()
        
    def updateFromJSON(self, setup_data):
        '''Unpack JSON representation to update instance variables and then
           calls update to write back into database'''
        
        self.setup_text = setup_data['setup_text']
        self.update()

    def delete(self):
        '''Deletes instance from database, any object representations of the
           instance are now invalid and shouldn't be used including this one'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Setup WHERE id = ?", (self.id, ))

    
    def jsonable(self):
        '''Returns a dict appropriate for creating JSON representation
           of the instance'''
        
        return {'id': self.id, 'setup_text': self.setup_text}

    @staticmethod
    def createFromJSON(setup_data):
        '''Creates new instance object using dict created from JSON representation
           using create'''
        
        setup_text = setup_data['setup_text']

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Setup (setup_text) VALUES (?)",
                               (setup_text,))
            conn.commit()
        return Setup.find(cursor.lastrowid)

    @staticmethod
    def find(id):
        '''If row with specified id exists, creates and returns corresponding ORM
           instance. Otherwise Exception raised.'''
        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Setup WHERE id = ?", (id,))
            row = cursor.fetchone()

        if row is None:
            raise Exception(f'No such Setup with id: {id}')
        else:
            return Setup(row['id'], row['setup_text'])

    @staticmethod
    def getAllIDs():        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Setup")
            all_ids = [row['id'] for row in cursor]
        return all_ids
        
    @staticmethod
    def setupBottleRoutes(app):
        @app.get('/setup')
        def getSetupIndex():
            setup_index = Setup.getAllIDs()
            response.content_type = 'application/json'
            return json.dumps(setup_index)
            
        @app.get('/setup/<id>')
        def getSetup(id):
            try:
                setup = Setup.find(id)
            except Exception:
                response.status = 404
                return f"Setup {id} not found"
            return setup.jsonable()
        
        @app.post('/setup')
        def postSetup():
            setup = Setup.createFromJSON(request.json)
            return setup.jsonable()

        @app.put('/setup/<id>')
        def updateSetup(id):
            '''Implements instance updating'''
    
            try:
                setup = Setup.find(id)
            except Exception:
                response.status = 404
                return f"Setup {id} to update not found"

            setup.updateFromJSON(request.json)
            return setup.jsonable()

        @app.delete('/setup/<id>')
        def deleteSetup(id):
            '''Implements instance deletion'''
    
            try:
                setup = Setup.find(id)
            except Exception:
                response.status = 404
                return f"Setup {id} to delete does not exist"

            setup.delete()
    
            response.content_type = 'application/json'
            return json.dumps(True)

