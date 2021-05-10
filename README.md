# exam-question-backend
Complete backend RESTful interface for a web application allowing an admin to develop exam questions (multiple choice, short answer, and SQL questions). Created with Python Bottle and tested with Postman. **Project made for COMP 521: Databases class taught by Professor Ketan-Mayer Patel.**

## Design
Questions
* Three types of questions: multiple choice, short answer, or SQL
* Have an integer id as primary key
* 'type' is 'mc', 'sa' or 'sql'
* Questions have question text.
* Questions are attributed with a point value greater than or equal to 0

Setup
* A setup is a some text that helps 'setup' the question. Multiple choice and short answer questions may or may not be associated with a setup but a SQL question is always associated with a setup.
* If associated with a setup, a question is associated with only one setup. But many questions can share the same setup.

Multiple Choice Questions
* Have 0 or more multiple choice options
* Each option has an integer id as a primary key
* Each option is associated as true or false, indicating the answer to the question.
* Each multiple choice option is associated with option text, the answer choice itself.

Short Answer Questions
* Associated with a model answer and a rubric
* Rubrics have an integer id, explanation text, and a point value.

SQL Questions
* Must have a setup
* Has a model answer

## ER Diagram for Backend
![image](https://user-images.githubusercontent.com/54407806/117677409-68f6d500-b17c-11eb-8a02-ee11cb71f803.png)

## Routes
### GET /question: returns an indexx of questions as a JSON object with the following structure:
```
{
  "mc": [<question digest>, <question digest>, ...],
  "sa": [<question digest>, <question digest>, ...],
  "sql": [<question digets>, <question digest>, ...]
}
```

### GET /question/[qid]: Returns a JSON object with one of the following structures depending on the type of the question.
For multiple choice questions:
```
{
  "id": <qid>,
  "type": "mc",
  "question_text": <question text>,
  "points": <point value>,
  "setup": null or <setup id>,
  "true_options": [<mc option>, <mc option>, ...],
  "false_options": [<mc option>, <mc option>, ...]
}
```
For SQL questions:
```
{
  "id": <qid>,
  "type": "sql",
  "question_text": <question text>,
  "points": <point value>,
  "setup": <setup id>,
  "answer": <model answer text>
}
```
For short answer questions:
```
{
  "id": <qid>,
  "type": "sa",
  "question_text": <question text>,
  "points": <point value>,
  "setup": <setup id> | null,
  "answer": <model answer text>,
  "rubrics": [<rubric>, <rubric>, <rubric>, ...]
}
```
  
### POST /question: Creates a new question using the JSON data provided in the request body. Data should be in the following form:
```
{
  "type": "mc" | "sql" | "sa",
  "question_text": <question text>,
  "points": <point value>,
  "setup": <setup id> | null,
  "answer": <answer text>
}
```
The following is validated and generates a 400 BAD Request:
* If the question is sql, then 'setup' is not allowed to be null
* If the question type is multiple choice, 'answer' does not need to be present and is ignored if present
* Question text can not be blank or nothing but white space
* Answer text (if present and needed) cannot be blank or nothing but white space
* Points must be greater than 0

### PUT /question/[qid]: Updates an existing question with id [qid]
Same JSON object as POST operation:
```
{
  "type": "mc" | "sql" | "sa",
  "question_text": <question text>,
  "points": <point value>,
  "setup": <setup id> | null,
  "answer": <answer text>
}
```
The question type is not allowed to change and must match the current type of the question. If the update attempts to change the question type, a 400 Bad Request response should be generated. Otherwise, the same validation as for creating a new question instance should be applied.

### DELETE /question/[qid]: Deletes the question with id <qid>.
If a multiple choice question, all associated answer options (both true and false) should be deleted.
If a short answer question, all associated rubrics should be deleted. 
Any model answer associated with the question (i.e., for short answer and sql questions) should be deleted.

If there is no question with id <qid>, a 404 Not Found response should be generated.

The response should be the JSON encoding of boolean true.
