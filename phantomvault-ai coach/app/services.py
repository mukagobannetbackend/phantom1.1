import os, uuid
from pathlib import Path
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','webp','gif'}

def save_screenshot(file, upload_folder):
    ext = (file.filename.rsplit('.',1)[-1].lower() if '.' in file.filename else '')
    if ext not in ALLOWED_EXTENSIONS: raise ValueError('Only PNG, JPG, WEBP, and GIF images are supported.')
    safe = f'{uuid.uuid4().hex}_{secure_filename(file.filename)}'
    cloudinary_url = os.getenv('CLOUDINARY_URL')
    if cloudinary_url:
        import cloudinary, cloudinary.uploader
        cloudinary.config(cloudinary_url=cloudinary_url)
        result = cloudinary.uploader.upload(file, folder='phantomvault/trades')
        return safe, result['secure_url']
    Path(upload_folder).mkdir(parents=True, exist_ok=True); file.save(Path(upload_folder) / safe)
    return safe, f'/media/{safe}'

def coach_review(trade):
    analysis = trade.analysis
    checks = {'Premarket / HTF alignment': 20, 'POI & liquidity': 20, 'Entry execution': 25, 'Risk management': 15, 'Exit & review': 10, 'Journal & rules': 10}
    scores = {k: 0 for k in checks}; evidence=[]; uncertainties=[]; mistakes=[]; lessons=[]
    if analysis and analysis.daily_bias: scores['Premarket / HTF alignment']=15; evidence.append('Daily bias was recorded.')
    else: uncertainties.append('Daily bias or higher-timeframe alignment is not recorded.')
    if analysis and analysis.four_h_poi: scores['POI & liquidity']=12; evidence.append('A 4H point of interest is visible in the record.')
    else: uncertainties.append('POI evidence is missing or unverifiable.')
    if analysis and (analysis.mss or analysis.sweep or analysis.fvg): scores['Entry execution']=18; evidence.append('At least one execution confirmation is recorded.')
    else: mistakes.append('No execution confirmation is recorded; entry quality is uncertain.')
    if trade.entry and trade.stop_loss and trade.take_profit: scores['Risk management']=12; evidence.append('Entry, stop, and target are present.')
    else: uncertainties.append('Risk fields are incomplete.')
    if trade.exit_rationale or trade.lessons: scores['Exit & review']=8; evidence.append('Post-trade reflection is present.')
    else: lessons.append('Add an exit-versus-plan note after every closed trade.')
    if trade.rule_adherence: scores['Journal & rules']=10; evidence.append('Trade is marked as rule-adherent.')
    else: lessons.append('Use the checklist to mark which rules were actually followed.')
    if trade.outcome == 'Loss' and trade.rule_adherence: lessons.append('A loss can still be a quality process outcome; separate variance from execution.')
    elif trade.outcome == 'Win' and not trade.rule_adherence: lessons.append('A win without rule adherence may be positive variance, not a repeatable edge.')
    return {'total_score': sum(scores.values()), 'category_scores': scores, 'evidence': evidence, 'uncertainties': uncertainties, 'mistakes': mistakes, 'lessons': lessons}
