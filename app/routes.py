import csv, io, json
from datetime import datetime, timedelta
from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, send_file, send_from_directory, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from . import db
from .models import Trade, Screenshot, JournalEntry, TradeAnalysis, AIReview
from .services import save_screenshot, coach_review

main = Blueprint('main', __name__)

def owned_trade(trade_id):
    trade = db.session.get(Trade, trade_id)
    if not trade or trade.user_id != current_user.id: abort(404)
    return trade

def ffloat(value):
    try: return float(value) if value not in (None, '') else None
    except ValueError: return None

def trade_from_form(trade=None):
    if trade is None: trade = Trade(user_id=current_user.id)
    trade.symbol=request.form.get('symbol','').strip().upper(); trade.direction=request.form.get('direction','Long')
    trade.account=request.form.get('account','').strip(); trade.session=request.form.get('session','').strip(); trade.setup=request.form.get('setup','').strip()
    date=request.form.get('trade_date','')
    if date:
        try: trade.trade_date=datetime.fromisoformat(date)
        except ValueError: pass
    for field in ('entry','stop_loss','take_profit','position_size','planned_r','realized_r','fees'): setattr(trade, field, ffloat(request.form.get(field)))
    trade.outcome=request.form.get('outcome','Open'); trade.status='Closed' if trade.outcome != 'Open' else 'Open'
    trade.rule_adherence=request.form.get('rule_adherence') == 'on'; trade.emotion=request.form.get('emotion','').strip(); trade.exit_rationale=request.form.get('exit_rationale','').strip(); trade.lessons=request.form.get('lessons','').strip()
    return trade

@main.route('/health')
def health(): return jsonify(status='ok', service='phantomvault-pro')

@main.route('/')
def home(): return redirect(url_for('main.dashboard')) if current_user.is_authenticated else redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    trades=Trade.query.filter_by(user_id=current_user.id).order_by(Trade.trade_date.desc()).all(); resolved=[t for t in trades if t.realized_r is not None]
    wins=[t for t in resolved if t.realized_r>0]; net=sum(t.realized_r or 0 for t in resolved); avg=(net/len(resolved)) if resolved else 0
    return render_template('dashboard.html', trades=trades[:8], total=len(trades), resolved=len(resolved), wins=len(wins), win_rate=(len(wins)/len(resolved)*100 if resolved else 0), net_r=net, avg_r=avg)

@main.route('/trades')
@login_required
def trades():
    q=Trade.query.filter_by(user_id=current_user.id)
    for field in ('symbol','direction','session','setup','outcome'):
        if request.args.get(field): q=q.filter(getattr(Trade,field).ilike(f"%{request.args[field]}%"))
    return render_template('trades.html', trades=q.order_by(Trade.trade_date.desc()).all())

@main.route('/trades/new', methods=['GET','POST'])
@login_required
def new_trade():
    if request.method=='POST':
        trade=trade_from_form();
        if not trade.symbol: flash('Symbol is required.', 'error')
        else: db.session.add(trade); db.session.commit(); flash('Trade workspace created.', 'success'); return redirect(url_for('main.trade_detail', trade_id=trade.id))
    return render_template('trade_form.html', trade=None)

@main.route('/trades/<int:trade_id>', methods=['GET','POST'])
@login_required
def trade_detail(trade_id):
    trade=owned_trade(trade_id)
    if request.method=='POST': trade_from_form(trade); db.session.commit(); flash('Trade updated.', 'success'); return redirect(url_for('main.trade_detail', trade_id=trade.id))
    return render_template('trade_detail.html', trade=trade, latest_review=trade.reviews[-1] if trade.reviews else None)

@main.route('/journal/<int:entry_id>/edit', methods=['POST'])
@login_required
def edit_journal(entry_id):
    entry = JournalEntry.query.filter_by(
        id=entry_id,
        user_id=current_user.id
    ).first_or_404()

    notes = request.form.get('notes', '').strip()

    if not notes:
        flash('Journal notes cannot be empty.', 'error')
    else:
        entry.notes = notes
        entry.entry_type = request.form.get(
            'entry_type', entry.entry_type
        )
        entry.emotional_state = request.form.get(
            'emotional_state', ''
        ).strip()

        db.session.commit()
        flash('Journal entry updated successfully.', 'success')

    return_to = request.form.get('return_to', '')
    if return_to.startswith('/') and not return_to.startswith('//'):
        return redirect(return_to)

    return redirect(url_for(
        'main.trade_detail',
        trade_id=entry.trade_id
    ))

@main.route('/trades/<int:trade_id>/screenshots', methods=['POST'])
@login_required
def upload_screenshot(trade_id):
    trade=owned_trade(trade_id); file=request.files.get('file')
    if not file or not file.filename: flash('Choose an image first.', 'error')
    else:
        try:
            filename,url=save_screenshot(file, current_app.config['UPLOAD_FOLDER']); shot=Screenshot(user_id=current_user.id, trade_id=trade.id, filename=filename, url=url, timeframe=request.form.get('timeframe','5M'), caption=request.form.get('caption','').strip(), tags=request.form.get('tags','').strip()); db.session.add(shot); db.session.commit(); flash('Evidence added.', 'success')
        except Exception as exc: flash(str(exc), 'error')
    return redirect(url_for('main.trade_detail', trade_id=trade.id))

@main.route('/media/<path:filename>')
@login_required
def media(filename):
    shot=Screenshot.query.filter_by(filename=filename, user_id=current_user.id).first_or_404(); return send_from_directory(current_app.config['UPLOAD_FOLDER'], shot.filename)

@main.route('/trades/<int:trade_id>/journal', methods=['POST'])
@login_required
def add_journal(trade_id):
    trade=owned_trade(trade_id); notes=request.form.get('notes','').strip()
    if notes: db.session.add(JournalEntry(user_id=current_user.id, trade_id=trade.id, entry_type=request.form.get('entry_type','post-trade'), notes=notes, emotional_state=request.form.get('emotional_state','').strip())); db.session.commit(); flash('Journal entry saved.', 'success')
    return redirect(url_for('main.trade_detail', trade_id=trade.id))

@main.route('/trades/<int:trade_id>/analysis', methods=['POST'])
@login_required
def save_analysis(trade_id):
    trade=owned_trade(trade_id); a=trade.analysis or TradeAnalysis(trade_id=trade.id)
    for field in ('daily_bias','four_h_poi','protected_levels','liquidity_objective','one_h_narrative','fifteen_m_structure','confirmation_notes'): setattr(a,field,request.form.get(field,'').strip())
    for field in ('initial_mitigation','sweep','mss','fvg','retracement'): setattr(a,field,request.form.get(field)=='on')
    if not trade.analysis: db.session.add(a)
    db.session.commit(); flash('Top-down analysis saved.', 'success'); return redirect(url_for('main.trade_detail', trade_id=trade.id))

@main.route('/trades/<int:trade_id>/coach', methods=['POST'])
@login_required
def run_coach(trade_id):
    trade=owned_trade(trade_id); result=coach_review(trade); version=len(trade.reviews)+1
    review=AIReview(user_id=current_user.id, trade_id=trade.id, version=version, total_score=result['total_score'], category_scores=result['category_scores'], evidence=result['evidence'], uncertainties=result['uncertainties'], mistakes=result['mistakes'], lessons=result['lessons']); db.session.add(review); db.session.commit(); flash('Coach review saved as version %s.' % version, 'success'); return redirect(url_for('main.trade_detail', trade_id=trade.id))

@main.route('/journal')
@login_required
def journal():
    entries=JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.created_at.desc()).all(); return render_template('journal.html', entries=entries)

@main.route('/analytics')
@login_required
def analytics():
    trades=Trade.query.filter_by(user_id=current_user.id).all(); resolved=[t for t in trades if t.realized_r is not None]; wins=[t for t in resolved if t.realized_r>0]; losses=[t for t in resolved if t.realized_r<0]; net=sum(t.realized_r for t in resolved); gross_win=sum(t.realized_r for t in wins); gross_loss=abs(sum(t.realized_r for t in losses));
    running=peak=drawdown=0
    for t in sorted(resolved,key=lambda x:x.trade_date): running += t.realized_r; peak=max(peak,running); drawdown=min(drawdown,running-peak)
    by_setup={}
    for t in resolved: by_setup.setdefault(t.setup or 'Unclassified',[]).append(t.realized_r)
    setup_rows=[{'name':k,'count':len(v),'avg':sum(v)/len(v)} for k,v in by_setup.items()]
    return render_template('analytics.html', resolved=len(resolved), win_rate=(len(wins)/len(resolved)*100 if resolved else 0), avg_r=(net/len(resolved) if resolved else 0), expectancy=(net/len(resolved) if resolved else 0), profit_factor=(gross_win/gross_loss if gross_loss else None), drawdown=drawdown, adherence=(sum(1 for t in resolved if t.rule_adherence)/len(resolved)*100 if resolved else 0), net_r=net, setup_rows=setup_rows)

@main.route('/export.csv')
@login_required
def export_csv():
    output=io.StringIO(); writer=csv.writer(output); writer.writerow(['date','symbol','direction','session','setup','outcome','realized_r','rule_adherence','emotion','lessons'])
    for t in Trade.query.filter_by(user_id=current_user.id).order_by(Trade.trade_date).all(): writer.writerow([t.trade_date.isoformat(),t.symbol,t.direction,t.session,t.setup,t.outcome,t.realized_r,t.rule_adherence,t.emotion,t.lessons])
    mem=io.BytesIO(output.getvalue().encode()); return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='phantomvault-trades.csv')

@main.route('/settings/theme', methods=['POST'])
@login_required
def theme(): current_user.theme=request.form.get('theme','dark'); db.session.commit(); return jsonify(ok=True)
