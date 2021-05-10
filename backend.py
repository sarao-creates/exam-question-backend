from bottle import Bottle, run, response, request
import json
import db
from mcOption import MCOption
from rubric import Rubric
from setup import Setup
from question import Question

app = Bottle()

MCOption.setupBottleRoutes(app)
Rubric.setupBottleRoutes(app)
Setup.setupBottleRoutes(app)
Question.setupBottleRoutes(app)

# Start the backend
run(app, host='localhost', port=8080, debug=True)
