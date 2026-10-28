from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    theme = db.Column(db.String(10), default='dark')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trades = db.relationship('Trade', backref='owner', lazy=True, cascade='all, delete-orphan')
    def set_password(self, value): self.password_hash = generate_password_hash(value)
    def check_password(self, value): return check_password_hash(self.password_hash, value)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    trade_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    symbol = db.Column(db.String(30), nullable=False)
    direction = db.Column(db.String(10), nullable=False, default='Long')
    account = db.Column(db.String(80)); session = db.Column(db.String(40)); setup = db.Column(db.String(80))
    entry = db.Column(db.Float); stop_loss = db.Column(db.Float); take_profit = db.Column(db.Float); position_size = db.Column(db.Float)
    planned_r = db.Column(db.Float); realized_r = db.Column(db.Float); fees = db.Column(db.Float, default=0)
    outcome = db.Column(db.String(20), default='Open'); status = db.Column(db.String(20), default='Open')
    rule_adherence = db.Column(db.Boolean, default=False); emotion = db.Column(db.String(80)); exit_rationale = db.Column(db.Text)
    lessons = db.Column(db.Text); created_at = db.Column(db.DateTime, default=datetime.utcnow)
    screenshots = db.relationship('Screenshot', backref='trade', lazy=True, cascade='all, delete-orphan')
    journal_entries = db.relationship('JournalEntry', backref='trade', lazy=True, cascade='all, delete-orphan')
    analysis = db.relationship('TradeAnalysis', backref='trade', uselist=False, cascade='all, delete-orphan')
    reviews = db.relationship('AIReview', backref='trade', lazy=True, cascade='all, delete-orphan')

class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False); url = db.Column(db.String(500), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False); caption = db.Column(db.String(255)); tags = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'), nullable=False)
    entry_type = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text, nullable=False); emotional_state = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'), unique=True, nullable=False)
    daily_bias = db.Column(db.Text); four_h_poi = db.Column(db.Text); protected_levels = db.Column(db.Text)
    liquidity_objective = db.Column(db.Text); one_h_narrative = db.Column(db.Text); fifteen_m_structure = db.Column(db.Text)
    initial_mitigation = db.Column(db.Boolean, default=False); sweep = db.Column(db.Boolean, default=False); mss = db.Column(db.Boolean, default=False)
    fvg = db.Column(db.Boolean, default=False); retracement = db.Column(db.Boolean, default=False); confirmation_notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'), nullable=False)
    version = db.Column(db.Integer, default=1); model = db.Column(db.String(120), default='rule-based-coach')
    total_score = db.Column(db.Integer, default=0); category_scores = db.Column(db.JSON, default=dict)
    evidence = db.Column(db.JSON, default=list); uncertainties = db.Column(db.JSON, default=list)
    mistakes = db.Column(db.JSON, default=list); lessons = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
