import os
import datetime
from sqlalchemy import desc
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
    complete = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False)
    sub_tasks = db.relationship("SubTask", backref="task", lazy=True)


class SubTask(db.Model):
    __tablename__ = "SubTasks"
    id = db.Column(db.Integer, primary_key=True)
    complete = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('Tasks.id'), nullable=False)
    sub_sub_tasks = db.relationship("SubSubTask", backref="subtask", lazy=True)


class SubSubTask(db.Model):
    __tablename__ = "SubSubTasks"
    id = db.Column(db.Integer, primary_key=True)
    complete = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False)
    subtask_id = db.Column(db.Integer, db.ForeignKey(
        'SubTasks.id'), nullable=False)


db.create_all()


@app.route('/')
def home():
    tasks_due = Task.query.order_by(Task.due_date).limit(5).all()
    tasks_priority = Task.query.order_by(Task.priority).limit(5).all()
    tasks_recent = Task.query.order_by(desc(Task.id)).limit(5).all()
    tasks_recent_completed = Task.query.filter_by(
        complete=True).limit(5).all()
    return render_template('index.html',
                           tasks_due=tasks_due,
                           tasks_priority=tasks_priority,
                           tasks_recent=tasks_recent,
                           tasks_recent_completed=tasks_recent_completed,
                           )


@app.route('/all_tasks')
def all_tasks():
    all_tasks = Task.query.order_by(desc(Task.id)).all()
    return render_template('all_tasks.html',
                           tasks=all_tasks
                           )


@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        due_date = request.form['due_date'].replace("-", "")
        due_date = datetime.datetime.strptime(
            due_date, '%Y%m%d')

        new_task = Task(
            name=request.form['name'],
            description=request.form['description'],
            priority=request.form['priority'],
            due_date=due_date,
            complete=False,
            notes=request.form['notes'],
        )

        db.session.add(new_task)
        db.session.commit()
        task = Task.query.filter_by(
            name=request.form['name']).order_by(desc(Task.id)).first()

        return redirect(url_for('task_view', task_id=task.id))

    return render_template('create_task.html')


@app.route('/create_subtask/<int:task_id>', methods=['GET', 'POST'])
def create_subtask(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':
        due_date = request.form['due_date'].replace("-", "")
        due_date = datetime.datetime.strptime(
            due_date, '%Y%m%d')
        new_task = SubTask(
            name=request.form['name'],
            description=request.form['description'],
            priority=request.form['priority'],
            due_date=due_date,
            complete=False,
            task_id=task_id,
            notes=request.form['notes'],
        )

        db.session.add(new_task)
        db.session.commit()
        subtask = SubTask.query.filter_by(
            name=request.form['name']).order_by(desc(SubTask.id)).first()
        return redirect(url_for('subtask_view', subtask_id=subtask.id))

    return render_template('create_subtask.html', task=task)


@app.route('/create_subsubtask/<int:subtask_id>', methods=['GET', 'POST'])
def create_subsubtask(subtask_id):
    subtask = SubTask.query.get(subtask_id)
    if request.method == 'POST':
        due_date = request.form['due_date'].replace("-", "")
        due_date = datetime.datetime.strptime(
            due_date, '%Y%m%d')

        new_task = SubSubTask(
            name=request.form['name'],
            description=request.form['description'],
            priority=request.form['priority'],
            due_date=due_date,
            complete=False,
            subtask_id=subtask_id,
            notes=request.form['notes'],
        )

        db.session.add(new_task)
        db.session.commit()
        subsubtask = SubSubTask.query.filter_by(
            name=request.form['name']).order_by(desc(SubSubTask.id)).first()
        return redirect(url_for('subsubtask_view', subsubtask_id=subsubtask.id))

    return render_template('create_subsubtask.html', subtask=subtask)


@app.route('/task_view/<int:task_id>', methods=['GET', 'POST'])
def task_view(task_id):
    task = Task.query.get(task_id)
    if request.method == "POST":
        task.complete = request.form['complete']
        db.session.commit()
        return redirect(url_for('notes', task_id=task.id))
    subtasks = SubTask.query.filter_by(
        task_id=task_id).order_by(SubTask.priority).all()
    total_tasks = len(subtasks)
    completed_tasks = 0
    for subtask in subtasks:
        if subtask.complete:
            completed_tasks += 1

    return render_template('task_view.html', completed_tasks=completed_tasks, total_tasks=total_tasks, task=task, subtasks=subtasks)


@app.route('/subtask_view/<int:subtask_id>')
def subtask_view(subtask_id):
    subtask = SubTask.query.get(subtask_id)
    subsubtasks = SubSubTask.query.filter_by(
        subtask_id=subtask_id).order_by(SubSubTask.priority).all()
    total_tasks = len(subsubtasks)
    completed_tasks = 0
    for subsubtask in subsubtasks:
        if subsubtask.complete:
            completed_tasks += 1
    return render_template('subtask_view.html', subtask=subtask, subsubtasks=subsubtasks, total_tasks=total_tasks, completed_tasks=completed_tasks)


@app.route('/subsubtask_view/<int:subsubtask_id>')
def subsubtask_view(subsubtask_id):
    subsubtask = SubSubTask.query.get(subsubtask_id)
    return render_template('subsubtask_view.html', subsubtask=subsubtask)


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':
        due_date = request.form['due_date'].replace("-", "")
        due_date = datetime.datetime.strptime(
            due_date, '%Y%m%d')

        task.name = request.form['name']
        task.description = request.form['description']
        task.priority = request.form['priority']
        task.due_date = due_date
        task.notes = request.form['notes']

        db.session.commit()

        return redirect(url_for('task_view', task_id=task.id))

    return render_template('create_task.html', edit=True, task=task)


@app.route('/edit_subtask/<int:subtask_id>', methods=['GET', 'POST'])
def edit_subtask(subtask_id):
    subtask = SubTask.query.get(subtask_id)
    if request.method == 'POST':
        due_date = request.form['due_date'].replace("-", "")
        due_date = datetime.datetime.strptime(
            due_date, '%Y%m%d')

        subtask.name = request.form['name']
        subtask.description = request.form['description']
        subtask.priority = request.form['priority']
        subtask.due_date = due_date
        subtask.notes = request.form['notes']

        db.session.commit()

        return redirect(url_for('subtask_view', subtask_id=subtask.id))

    return render_template('create_subtask.html', edit=True, subtask=subtask)


@app.route('/edit_subsubtask/<int:subsubtask_id>', methods=['GET', 'POST'])
def edit_subsubtask(subsubtask_id):
    subsubtask = SubSubTask.query.get(subsubtask_id)
    if request.method == 'POST':
        due_date = request.form['due_date'].replace("-", "")
        due_date = datetime.datetime.strptime(
            due_date, '%Y%m%d')

        subsubtask.name = request.form['name']
        subsubtask.description = request.form['description']
        subsubtask.priority = request.form['priority']
        subsubtask.due_date = due_date
        subsubtask.notes = request.form['notes']

        db.session.commit()

        return redirect(url_for('subsubtask_view', subsubtask_id=subsubtask.id))

    return render_template('create_subsubtask.html', edit=True, subsubtask=subsubtask)


@app.route('/task_delete/<int:task_id>')
def task_delete(task_id):
    db.session.delete(Task.query.get(task_id))
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/subtask_delete/<int:subtask_id>')
def subtask_delete(subtask_id):
    db.session.delete(SubTask.query.get(subtask_id))
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/subsub_delete/<int:subsubtask_id>')
def subsubtask_delete(subsubtask_id):
    db.session.delete(SubSubTask.query.get(subsubtask_id))
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/task_complete/<int:task_id>')
def task_complete(task_id):
    task = Task.query.get(task_id)
    if task.complete == False:
        task.complete = True
        db.session.commit()
        return redirect(url_for('task_view', task_id=task_id))
    if task.complete == True:
        task.complete = False
        db.session.commit()
        return redirect(url_for('task_view', task_id=task_id))


@app.route('/subtask_complete/<int:subtask_id>')
def subtask_complete(subtask_id):
    task = SubTask.query.get(subtask_id)
    if task.complete == False:
        task.complete = True
        db.session.commit()
        return redirect(url_for('subtask_view', subtask_id=subtask_id))
    if task.complete == True:
        task.complete = False
        db.session.commit()
        return redirect(url_for('subtask_view', subtask_id=subtask_id))


@app.route('/subsubtask_complete/<int:subsubtask_id>')
def subsubtask_complete(subsubtask_id):
    task = SubSubTask.query.get(subsubtask_id)
    if task.complete == False:
        task.complete = True
        db.session.commit()
        return redirect(url_for('subsubtask_view', subsubtask_id=subsubtask_id))
    if task.complete == True:
        task.complete = False
        db.session.commit()
        return redirect(url_for('subsubtask_view', subsubtask_id=subsubtask_id))


if __name__ == "__main__":
    app.run(debug=True)
