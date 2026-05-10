from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'


# ─── Models ───────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    role       = db.Column(db.String(20),  default='member')   # 'admin' or 'member'
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    tasks      = db.relationship('Task', backref='assignee', lazy=True,
                                 foreign_keys='Task.assigned_to')

    @property
    def is_admin(self):
        return self.role == 'admin'


class Task(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,        default='')
    status      = db.Column(db.String(20),  default='pending')   # pending / in_progress / completed
    priority    = db.Column(db.String(20),  default='medium')    # low / medium / high
    due_date    = db.Column(db.Date,        nullable=True)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    created_by  = db.Column(db.Integer,     db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer,     db.ForeignKey('user.id'), nullable=True)
    creator     = db.relationship('User',   foreign_keys=[created_by], backref='created_tasks')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role     = request.form.get('role', 'member')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('signup.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
    else:
        tasks = Task.query.filter_by(assigned_to=current_user.id)\
                          .order_by(Task.created_at.desc()).all()

    total     = len(tasks)
    completed = sum(1 for t in tasks if t.status == 'completed')
    pending   = sum(1 for t in tasks if t.status == 'pending')
    in_prog   = sum(1 for t in tasks if t.status == 'in_progress')

    recent = tasks[:5]
    return render_template('dashboard.html',
                           tasks=tasks, recent=recent,
                           total=total, completed=completed,
                           pending=pending, in_progress=in_prog)


@app.route('/tasks')
@login_required
def tasks():
    status_filter   = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')

    if current_user.is_admin:
        query = Task.query
    else:
        query = Task.query.filter_by(assigned_to=current_user.id)

    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)

    all_tasks = query.order_by(Task.created_at.desc()).all()
    members   = User.query.all() if current_user.is_admin else []
    return render_template('tasks.html', tasks=all_tasks,
                           members=members,
                           status_filter=status_filter,
                           priority_filter=priority_filter)


@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if not current_user.is_admin:
        flash('Only admins can create tasks.', 'danger')
        return redirect(url_for('tasks'))

    members = User.query.all()

    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority    = request.form.get('priority', 'medium')
        assigned_to = request.form.get('assigned_to', type=int)
        due_date_str = request.form.get('due_date', '')

        if not title:
            flash('Task title is required.', 'danger')
            return render_template('create_task.html', members=members)

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        task = Task(
            title=title,
            description=description,
            priority=priority,
            assigned_to=assigned_to,
            due_date=due_date,
            created_by=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks'))

    return render_template('create_task.html', members=members)


@app.route('/tasks/<int:task_id>')
@login_required
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    if not current_user.is_admin and task.assigned_to != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tasks'))
    return render_template('task_detail.html', task=task)


@app.route('/tasks/<int:task_id>/update_status', methods=['POST'])
@login_required
def update_status(task_id):
    task = Task.query.get_or_404(task_id)
    if not current_user.is_admin and task.assigned_to != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tasks'))

    new_status = request.form.get('status')
    if new_status in ('pending', 'in_progress', 'completed'):
        task.status = new_status
        db.session.commit()
        flash('Task status updated!', 'success')

    return redirect(url_for('task_detail', task_id=task_id))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    if not current_user.is_admin:
        flash('Only admins can delete tasks.', 'danger')
        return redirect(url_for('tasks'))

    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'success')
    return redirect(url_for('tasks'))


@app.route('/members')
@login_required
def members():
    if not current_user.is_admin:
        flash('Admin access only.', 'danger')
        return redirect(url_for('dashboard'))
    all_members = User.query.order_by(User.created_at.desc()).all()
    return render_template('members.html', members=all_members)


# ─── Init ─────────────────────────────────────────────────────────────────────

def create_tables():
    db.create_all()
    # seed an admin account if none exists
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin',
            email='admin@taskmanager.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('✅  Default admin created — email: admin@taskmanager.com  password: admin123')


with app.app_context():
    create_tables()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
