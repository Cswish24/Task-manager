import os
from django.shortcuts import render

from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = "somewords"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///task_management.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = "Tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    sub_tasks = db.relationship("SubTask", backref="task", lazy=True)


class SubTask(db.Model):
    __tablename__ = "SubTasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('Tasks.id'), nullable=False)
    sub_sub_tasks = db.relationship("SubSubTask", backref="subtask", lazy=True)


class SubSubTask(db.Model):
    __tablename__ = "SubSubTasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    subtask_id = db.Column(db.Integer, db.ForeignKey(
        'SubTasks.id'), nullable=False)


db.create_all()


@app.route('/')
def home():
    tasks = Task.query.all()
    print(tasks)
    return render_template('index.html', tasks=tasks)


@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':

        new_task = Task(
            name=request.form['name'],
            description=request.form['description'],
            priority=request.form['priority'],
        )

        db.session.add(new_task)
        db.session.commit()
        task = Task.query.filter_by(name=request.form['name']).first()

        return redirect(url_for('create_subtask', task_id=task.id))

    return render_template('create_task.html')


@app.route('/create_subtask/<int:task_id>', methods=['GET', 'POST'])
def create_subtask(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':

        new_task = SubTask(
            name=request.form['name'],
            description=request.form['description'],
            priority=request.form['priority'],
            task_id=task_id,
        )
        print(request.form['name'])

        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    print('jank')
    return render_template('create_subtask.html', task=task)


@app.route('/task_view/<int:task_id>', methods=['GET', 'POST'])
def task_view(task_id):
    print(task_id)
    task = Task.query.get(task_id)
    subtasks = SubTask.query.filter_by(task_id=task_id).all()
    return render_template('task_view.html', task=task, subtasks=subtasks)


@app.route('/subtask_view/<int:subtask_id>', methods=['GET', 'POST'])
def subtask_view(subtask_id):
    subtask = SubTask.query.get(subtask_id)
    subsubtasks = SubSubTask.query.filter_by(subtask_id=subtask_id).all()
    return render_template('subtask_view.html', subtask=subtask, subsubtasks=subsubtasks)


if __name__ == "__main__":
    app.run(debug=True)
