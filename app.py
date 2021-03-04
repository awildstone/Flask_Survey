from flask import Flask, request, render_template, redirect, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from surveys import *

app = Flask(__name__)
app.config['SECRET_KEY'] = "my_secret_key"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# hold responses from our survey
responses = []
# hold the survey type and questions length selected by the user
survey_selection = {}

@app.route('/')
def select_survey():
    return render_template('choose_survey.html')

# @app.route('/')
@app.route('/home', methods=['POST'])
def survey_home():
    '''Get survey type and display survey instructions to user.'''
    selection = request.form['survey']
    survey_obj = surveys.get(f'{selection}')

    #save the survey selection
    survey_selection['type'] = survey_obj
    survey_selection['name'] = selection
    survey_selection['num_questions'] = len(survey_obj.questions)
    
    survey_title = survey_obj.title
    survey_instructions = survey_obj.instructions
    return render_template('home.html', title=survey_title, instructions=survey_instructions)

@app.route('/questions/<int:num>')
def display_question(num):
    '''Get survey questions and display question and choices to user. '''
    if (num - 1 == len(responses)):
        # get the survey type
        survey_obj = survey_selection.get('type')
        title = survey_obj.title
        # get question data
        question_obj = survey_obj.questions[num - 1]
        question = question_obj.question
        choices = question_obj.choices
        allow_text = question_obj.allow_text
        return render_template('question.html', title=title, question_num=num, question=question, choices=choices, allow_text=allow_text)
    elif (len(responses) == survey_selection.get('num_questions')):
        return redirect('/thanks')
    else:
        flash('Stop trying to change the survey question order!', 'error')
        return redirect(f'/questions/{len(responses) + 1}')

@app.route('/answer', methods=['POST'])
def save_answer():
    '''Get survey responses for the user and save the response to responses[].
    If the survey has more questions, show the next question, otherwise
    thank the user for taking the survey. '''
    if (len(request.form) == 2):
        answer = request.form['answer']
        reason = request.form['reason']
        responses.append({'answer': answer, 'reason': reason})
    else:
        answer = request.form['answer']
        responses.append(answer)

    if (len(responses) == survey_selection.get('num_questions')):
        return redirect('/thanks')
    else: 
        return redirect(f'/questions/{len(responses) + 1}')

@app.route('/thanks')
def say_thanks():
    '''Thank user for completing the survey.'''

    survey_obj = survey_selection.get('type')
    questions = survey_obj.questions
    q_res = responses
    length = survey_selection.get('num_questions')

    return render_template('thanks.html', questions=questions, responses=q_res, length=length)