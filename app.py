from flask import Flask, session, request, render_template, redirect, make_response, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "my_secret_key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

#save the key names for responses and survey so the names are constant
RESPONSES_KEY = 'responses'
SURVEY_KEY = 'survey_type'

@app.route('/')
def select_survey():
    ''' Display a form for the user to select a survey type. '''
    return render_template('choose_survey.html', surveys=surveys)

@app.route('/', methods=['POST'])
def start_survey():
    ''' Get the survey selection and display the survey instructions to the user. '''

    #get the survey selection
    selection = request.form['survey_name']

    #get the survey object so we can pass to the start page
    survey = surveys[selection]

    #save the survey type to the current session, also overrides any past selection
    session[SURVEY_KEY] = selection

    return render_template('start.html', survey=survey)

@app.route('/start_survey', methods=['POST'])
def save_session():
    ''' Clear past responses data from the session before beginning this new survey. '''

    #set sessions to an empty list
    session[RESPONSES_KEY] = []

    return redirect('/questions/1')


@app.route('/questions/<int:num>')
def display_question(num):
    '''Get survey question number and display question and choices to user. '''

    #get the current responses
    responses = session.get(RESPONSES_KEY)

    survey = get_current_survey()

    if (num - 1 == len(responses)):
        #the current page num matches the number of responses we have!
        #get the question data and show the question to the user
        question = survey.questions[num - 1]
        return render_template('question.html', question_num=num, question=question)
    elif (len(responses) == len(survey.questions)):
        #all questions are answered
        return redirect('/thanks')
    else:
        #they are trying to cheat!
        flash('Stop trying to change the survey question order!', 'error')
        return redirect(f'/questions/{len(responses) + 1}')

@app.route('/answer', methods=['POST'])
def save_answer():
    '''Get survey responses for the user and save the response to responses[].
    Handle responses from the form if there is more than one response to parse
    and save the responses to the response list in memory.
    If the survey has more questions, show the next question, otherwise
    thank the user for taking the survey. '''

    #get answer and reason (if reason doesn't exist save an empty string)
    answer = request.form['answer']
    reason = request.form.get('reason', '')

    #point responses to the session response list to access it and add this response to the list
    responses = session[RESPONSES_KEY]
    responses.append({'answer': answer, 'reason': reason})
    #rebind session
    session[RESPONSES_KEY] = responses

    survey = get_current_survey()

    if (len(responses) == len(survey.questions)):
        #the survey is complete
        return redirect('/thanks')
    else:
        #there are more questions to go - show the next question to the user
        return redirect(f'/questions/{len(responses) + 1}')

@app.route('/thanks')
def say_thanks():
    '''Thank user for completing the survey.'''

    #get end of survey data
    survey = get_current_survey()
    responses = session[RESPONSES_KEY]
    survey_length = len(survey.questions)

    return render_template('thanks.html', survey=survey, responses=responses, len=survey_length)

def get_current_survey():
    ''' Gets the survey type from the current session, then gets survey object
    from surveys and returns it. '''
    #get the current survey selection and survey object for that type
    survey_type = session.get(SURVEY_KEY)
    survey = surveys[survey_type]

    return survey