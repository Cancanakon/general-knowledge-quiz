from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Gizli bir anahtar belirleyin
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yarisma.db'

db = SQLAlchemy(app)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, default=0)
    answered_question_count = db.Column(db.Integer, default=0)
    # Katılımcı ile sorular arasında ilişki
    answered_questions = db.relationship('Question', secondary='participant_answers')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

class ParticipantAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answered_correctly = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        participant = Participant(first_name=first_name, last_name=last_name, phone_number=phone_number)
        db.session.add(participant)
        db.session.commit()
        return redirect(url_for('game', participant_id=participant.id, question_id=1))
@app.route('/game/<int:participant_id>/<int:question_id>')
def game(participant_id, question_id):
    participant = Participant.query.get(participant_id)
    if not participant:
        flash('Katılımcı bulunamadı!', 'error')
        return redirect(url_for('index'))

    all_questions = Question.query.all()
    random.shuffle(all_questions)

    questions = all_questions[:10]

    answered_question_count = participant.answered_question_count
    next_question_number = answered_question_count + 1

    if answered_question_count >= 10 or next_question_number > 10:
        return redirect(url_for('leaderboard'))

    current_question = questions[answered_question_count]

    return render_template('game.html', participant=participant, current_question=current_question, remaining_questions=len(questions))

@app.route('/check_answer/<int:participant_id>/<int:question_id>', methods=['POST'])
def check_answer(participant_id, question_id):
    participant = Participant.query.get(participant_id)
    if not participant:
        flash('Katılımcı bulunamadı!', 'error')
        return redirect(url_for('index'))

    question = Question.query.get(question_id)
    if not question:
        flash('Soru bulunamadı!', 'error')
        return redirect(url_for('game', participant_id=participant_id, question_id=1))

    selected_answer = request.form['answer']
    answered_correctly = selected_answer == question.correct_answer

    answered_question = ParticipantAnswers(participant_id=participant_id, question_id=question_id, answered_correctly=answered_correctly)
    db.session.add(answered_question)
    db.session.commit()

    if answered_correctly:
        participant.points += 10

    # Her yanıt sonrasında toplam yanıtlama sayısını artır
    participant.answered_question_count += 1
    db.session.commit()

    if participant.answered_question_count >= 10:
        return redirect(url_for('leaderboard'))
    else:
        next_question_number = participant.answered_question_count + 1
        return redirect(url_for('game', participant_id=participant_id, question_id=next_question_number))

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        question_text = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        correct_answer = request.form['correct_answer']

        new_question = Question(question=question_text, option_a=option_a, option_b=option_b, option_c=option_c, correct_answer=correct_answer)
        db.session.add(new_question)
        db.session.commit()
        flash('Soru başarıyla eklendi!', 'success')

    return render_template('add_question.html')

@app.route('/leaderboard')
def leaderboard():
    participants = Participant.query.order_by(Participant.points.desc()).all()
    return render_template('leaderboard.html', participants=participants)

media_dizini = os.path.join(os.path.dirname(__file__), 'media')

# Bu URL ile medya dosyalarını sunacak bir route tanımlayın
@app.route('/medya/<dosya_ad>')
def medya(dosya_ad):
    return send_from_directory(media_dizini, dosya_ad)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    #
    #app.run(debug=True) #localde paylaşımsız server için!!!
    app.run('192.168.186.243',5000)