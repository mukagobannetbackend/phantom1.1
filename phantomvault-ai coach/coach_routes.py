
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from . import db
from .models import Trade, AIReview, JournalEntry

coach = Blueprint("coach", __name__, url_prefix="/coach")


@coach.route("/")
@login_required
def home():
    user_id = current_user.id

    # Only read the signed-in user's trades.
    trades = Trade.query.filter_by(user_id=user_id).order_by(
        Trade.trade_date.desc()
    ).all()

    reviews = AIReview.query.filter_by(user_id=user_id).order_by(
        AIReview.created_at.desc()
    ).all()

    journal_count = JournalEntry.query.filter_by(
        user_id=user_id
    ).count()

    # Count recorded outcomes without assuming that missing values are losses.
    wins = sum(1 for trade in trades if (trade.outcome or "").lower() == "win")
    losses = sum(1 for trade in trades if (trade.outcome or "").lower() == "loss")
    open_trades = sum(
        1 for trade in trades
        if (trade.status or trade.outcome or "").lower() == "open"
    )

    reviewed_trade_ids = {review.trade_id for review in reviews}

    # Collect recurring lessons from saved AI reviews.
    lesson_counts = {}
    mistake_counts = {}

    for review in reviews:
        for lesson in (review.lessons or []):
            if isinstance(lesson, str) and lesson.strip():
                lesson_counts[lesson.strip()] = (
                    lesson_counts.get(lesson.strip(), 0) + 1
                )

        for mistake in (review.mistakes or []):
            if isinstance(mistake, str) and mistake.strip():
                mistake_counts[mistake.strip()] = (
                    mistake_counts.get(mistake.strip(), 0) + 1
                )

    recurring_lessons = sorted(
        lesson_counts.items(), key=lambda item: item[1], reverse=True
    )[:5]

    recurring_mistakes = sorted(
        mistake_counts.items(), key=lambda item: item[1], reverse=True
    )[:5]

    # A history summary, not a claim that the AI has trained itself.
    return render_template(
        "coach_home.html",
        trades=trades,
        reviews=reviews,
        trade_count=len(trades),
        review_count=len(reviews),
        reviewed_trade_count=len(reviewed_trade_ids),
        journal_count=journal_count,
        wins=wins,
        losses=losses,
        open_trades=open_trades,
        recurring_lessons=recurring_lessons,
        recurring_mistakes=recurring_mistakes,
    )
