import db
import json
from bottle import response, request
from mcOption import MCOption
from rubric import Rubric

class Question:

    def __init__(self, id, q_type, question_text, points, setup, answer):
        '''Constructor'''
        self.id = id
        self.type = q_type
        self.question_text = question_text
        self.points = points
        self.setup = setup
        self.answer = answer

    def update(self):
        '''Writes back instance values into database'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Question SET question_text = ?, points = ?, setup = ?, answer = ? WHERE id = ?",
                (self.question_text, self.points, self.setup, self.answer, self.id))
            conn.commit()
    
    def updateFromJSON(self, question_data):
        '''Unpack JSON representation to update instance variables and then
           calls update to write back into database'''

        if (question_data['type'] != self.type):
            raise Exception(f'Type cannot be changed.')

        self.question_text = question_data['question_text']
        self.points = question_data['points']
        self.setup = question_data['setup']
        self.answer = question_data['answer']
        self.update()
    
    def delete(self):
        '''Deletes instance from database, any object representations of the
           instance are now invalid and shouldn't be used including this one'''

        if (self.type == 'mc'):
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Question WHERE id =?", (self.id, ))
                cursor.execute("DELETE FROM MCOption WHERE qid =?", (self.id,))
        
        if (self.type == 'sa'):
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Question WHERE id =?", (self.id, ))
                cursor.execute("DELETE FROM Rubric WHERE qid =?", (self.id,))
        if (self.type == 'sql'):
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Question WHERE id =?", (self.id, ))
    
    def jsonable(self):
        '''Returns a dict appropriate for creating JSON representation
           of the instance'''

        
        
        if (self.type == 'sql'):
            return {'id': self.id, 'type': "sql", 'question_text': self.question_text, 'points': self.points, 'setup': self.setup, 'answer': self.answer}
        
        if (self.type == 'mc'):
            true_options = []
            false_options = []
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM MCOption WHERE qid = ? AND is_true = ?", (self.id, 1))
                for row in cursor:
                    true_options.append(MCOption(row['id'], bool(row['is_true']), row['option_text'], row['qid']).jsonable()) 
            
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM MCOption WHERE qid = ? AND is_true = ?", (self.id, 0))
                for row in cursor:
                    false_options.append(MCOption(row['id'], bool(row['is_true']), row['option_text'], row['qid']).jsonable())
            
            return {'id': self.id, 'type': "mc", 'question_text': self.question_text, 'points': self.points, 'setup': self.setup, 'true_options': true_options , 'false_options': false_options} 

        if (self.type == 'sa'):
            rubrics = []
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Rubric WHERE qid = ?", (self.id, ))
                for row in cursor:
                    rubrics.append(Rubric(row['id'], row['rubric_text'], row['points'], row['qid']).jsonable())
            
            return {'id': self.id, 'type': "sa", 'question_text': self.question_text, 'points': self.points, 'setup': self.setup, 'answer': self.answer, 'rubrics': rubrics}

    

    @staticmethod
    def createFromJSON(question_data):
        '''Creates new instance object using dict created from JSON representation
           using create'''
        
        # Unpack the instance data from JSON
        # Should validate information here and throw exception
        # if something is not right.
        q_type = question_data['type']
        question_text = question_data['question_text']
        points = question_data['points']
        setup = question_data['setup']


        if (q_type == 'mc'):
            answer = 'filler'
        else:
            answer = question_data['answer']
        
        if (q_type != 'sql' and q_type != 'sa' and q_type != 'mc'):
            raise Exception(f'Question type must be sql, sa, or mc.')

        if (q_type == 'sql' and setup == None):
            raise Exception(f'Setup is required for SQL questions')

        if (question_text == '' or question_text.isspace()):
            raise Exception(f'Blank or white space entries are not allowed.')
        if (points <= 0):
            raise Exception(f'Point value must be greater than 0.')

        if (q_type == 'sql' or q_type == 'sa'):
            if (answer == '' or answer.isspace()):
                raise Exception(f'Answer must be filled in for this question.')

        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Question (type, question_text, points, setup, answer) VALUES (?, ?, ?, ?, ?)",
                    (q_type, question_text, points, setup, answer))
            conn.commit()
        return Question.find(cursor.lastrowid)
        
    @staticmethod
    def find(id):
        '''If row with specified id exists, creates and returns corresponding ORM
           instance. Otherwise Exception raised.'''
        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question WHERE id = ?", (id,))
            row = cursor.fetchone()
        
        if row is None:
            raise Exception(f'No such Question with id: {id}')
        else:
            return Question(row['id'], row['type'], row['question_text'], row['points'], row['setup'], row['answer'])
    
    @staticmethod
    def getAllIDs():
        mc_digest = []
        sa_digest = []
        sql_digest = []
        temp = {}
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, SUBSTRING(question_text, 1, 40) as blurb FROM Question WHERE type='mc'")
            for row in cursor:
                temp = {'id': row['id'], 'question_start': row['blurb']}
                mc_digest.append(temp)
                
            cursor.execute("SELECT id, SUBSTRING(question_text, 1, 40) as blurb FROM Question WHERE type='sa'")
            for row in cursor:
                temp = {'id': row['id'], 'question_start': row['blurb']}
                sa_digest.append(temp)
                
            cursor.execute("SELECT id, SUBSTRING(question_text, 1, 40) as blurb FROM Question WHERE type='sql'")
            for row in cursor:
                temp = {'id': row['id'], 'question_start': row['blurb']}
                sql_digest.append(temp)
        
        return mc_digest, sa_digest, sql_digest
                

    @staticmethod
    def setupBottleRoutes(app):
        @app.get('/question')
        def getQuestionIndex():
            mc_digest, sa_digest, sql_digest = Question.getAllIDs()
            response.content_type = 'application/json'
            return {"mc": mc_digest, "sa": sa_digest, "sql": sql_digest}
            # return json.dumps(question_index)
        
        @app.get('/question/<qid>')
        def getQuestion(qid):
            try:
                question = Question.find(qid)
            except Exception:
                response.status = 404
                return f"Question {qid} not found"
            return question.jsonable()
        
        @app.post('/question')
        def postQuestion():
            try:
                question = Question.createFromJSON(request.json)
            except Exception as err:
                response.status = 400
                return err.args
            return question.jsonable()
        
        @app.put('/question/<id>')
        def updateQuestion(id):
            '''Implements instance updating'''
            try:
                question = Question.find(id)
            except Exception:
                response.status = 404
                return f"Question {id} to update not found"
            
            try:
                question.updateFromJSON(request.json)
            except Exception as err:
                response.status = 400
                return err.args
            return question.jsonable()

        @app.delete('/question/<id>')
        def deleteQuestion(id):
            '''Implements instance deletion'''
            try: 
                question = Question.find(id)
            except Exception:
                response.status = 404
                return f"Question {id} to delete does not exist"

            
            question.delete()
            
            response.content_type = 'application/json'
            return json.dumps(True)
