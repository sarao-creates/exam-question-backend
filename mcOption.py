import db
import json
from bottle import response, request

class MCOption:

    def __init__(self, id, is_true, option_text, qid):
        '''Constructor'''
        self.id = id
        self.is_true = is_true
        self.option_text = option_text
        self.qid = qid

    def update(self):
        '''Writes back instance values into database'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE MCOption SET is_true = ?, option_text = ?, qid = ? WHERE id = ?",
                               (1 if self.is_true else 0, self.option_text, self.qid, self.id))
            conn.commit()
        
    def updateFromJSON(self, mc_data):
        '''Unpack JSON representation to update instance variables and then
           calls update to write back into database'''
        
        self.is_true = mc_data['is_true']
        self.option_text = mc_data['option_text']
        self.qid = mc_data['qid']
        self.update()

    def delete(self):
        '''Deletes instance from database, any object representations of the
           instance are now invalid and shouldn't be used including this one'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM MCOption WHERE id = ?", (self.id, ))

    
    def jsonable(self):
        '''Returns a dict appropriate for creating JSON representation
           of the instance'''
        
        return {'id': self.id, 'is_true': self.is_true, 'option_text': self.option_text, 'qid': self.qid}

    @staticmethod
    def createFromJSON(mc_data):
        '''Creates new instance object using dict created from JSON representation
           using create'''
        
        # Unpack the instance data from JSON
        # Should validate information here and throw exception
        # if something is not right.
        is_true = mc_data['is_true']
        option_text = mc_data['option_text']
        qid = mc_data['qid']

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO MCOption (is_true, option_text, qid) VALUES (?, ?, ?)",
                               (1 if is_true else 0, option_text, qid))
            conn.commit()
        return MCOption.find(cursor.lastrowid)

    @staticmethod
    def find(id):
        '''If row with specified id exists, creates and returns corresponding ORM
           instance. Otherwise Exception raised.'''
        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM MCOption WHERE id = ?", (id,))
            row = cursor.fetchone()

        if row is None:
            raise Exception(f'No such MCOption with id: {id}')
        else:
            return MCOption(row['id'], bool(row['is_true']), row['option_text'], row['qid'])

    @staticmethod
    def getAllIDs():        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM MCOption")
            all_ids = [row['id'] for row in cursor]
        return all_ids
        
    @staticmethod
    def setupBottleRoutes(app):
        @app.get('/mc_option')
        def getMCOptionIndex():
            mc_option_index = MCOption.getAllIDs()
            response.content_type = 'application/json'
            return json.dumps(mc_option_index)
            
        @app.get('/mc_option/<id>')
        def getMCOption(id):
            try:
                mc_option = MCOption.find(id)
            except Exception:
                response.status = 404
                return f"Multiple choice option {id} not found"
            return mc_option.jsonable()
        
        @app.post('/mc_option')
        def postMCOption():

            mc_option = MCOption.createFromJSON(request.json)
            return mc_option.jsonable()

        @app.put('/mc_option/<id>')
        def updateMCOption(id):
            '''Implements instance updating'''
    
            try:
                mc_option = MCOption.find(id)
            except Exception:
                response.status = 404
                return f"Multiple choice option {id} to update not found"

            mc_option.updateFromJSON(request.json)
            return mc_option.jsonable()

        @app.delete('/mc_option/<id>')
        def deleteMCOption(id):
            '''Implements instance deletion'''
    
            try:
                mc_option = MCOption.find(id)
            except Exception:
                response.status = 404
                return f"Multiple choice option {id} to delete does not exist"

            mc_option.delete()
    
            response.content_type = 'application/json'
            return json.dumps(True)

