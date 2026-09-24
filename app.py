from flask import Flask,render_template,request,redirect,url_for,flash,send_from_directory,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user
from werkzeug.security import generate_password_hash,check_password_hash
from pathlib import Path
import os,uuid
BASE=Path(__file__).resolve().parent
# A Vercel usa um filesystem somente-leitura. Apenas /tmp pode receber arquivos
# durante a execução da função. Para testes, banco e uploads ficam em /tmp.
IS_VERCEL=bool(os.getenv('VERCEL'))
RUNTIME_BASE=Path('/tmp/site-uniao') if IS_VERCEL else BASE
INSTANCE_DIR=RUNTIME_BASE/'instance'
UPLOAD_DIR=(RUNTIME_BASE/'uploads') if IS_VERCEL else (BASE/'static/uploads')
INSTANCE_DIR.mkdir(parents=True,exist_ok=True)
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)

app=Flask(__name__,instance_relative_config=True)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY','troque-esta-chave-de-producao'),
    SQLALCHEMY_DATABASE_URI='sqlite:///'+str(INSTANCE_DIR/'site.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=str(UPLOAD_DIR),
    MAX_CONTENT_LENGTH=50*1024*1024
)
db=SQLAlchemy(app);login=LoginManager(app);login.login_view='admin_login'
class Admin(UserMixin,db.Model):
 id=db.Column(db.Integer,primary_key=True);name=db.Column(db.String(120),nullable=False);email=db.Column(db.String(180),unique=True,nullable=False);password_hash=db.Column(db.String(255),nullable=False)
 def set_password(self,p):self.password_hash=generate_password_hash(p)
 def check_password(self,p):return check_password_hash(self.password_hash,p)
class SiteSettings(db.Model):
 id=db.Column(db.Integer,primary_key=True);company_name=db.Column(db.String(180),default='União');story=db.Column(db.Text,default='');showroom_phone=db.Column(db.String(80),default='');showroom_whatsapp=db.Column(db.String(80),default='');address=db.Column(db.String(255),default='');logo=db.Column(db.String(255),default='');hero_media=db.Column(db.String(255),default='');current_photo=db.Column(db.String(255),default='');old_photo=db.Column(db.String(255),default='');fleet_media=db.Column(db.String(255),default='')
class Region(db.Model):
 id=db.Column(db.Integer,primary_key=True);name=db.Column(db.String(80),unique=True,nullable=False);state=db.Column(db.String(2),nullable=False)
class Seller(db.Model):
 id=db.Column(db.Integer,primary_key=True);name=db.Column(db.String(120),nullable=False);phone=db.Column(db.String(40),nullable=False);role=db.Column(db.String(80),default='Vendedor');region_id=db.Column(db.Integer,db.ForeignKey('region.id'));state=db.Column(db.String(2),default='');city=db.Column(db.String(100),default='');lat=db.Column(db.Float,default=-7.23056);lng=db.Column(db.Float,default=-35.88111);active=db.Column(db.Boolean,default=True);region=db.relationship('Region',backref='sellers')
class Download(db.Model):
 id=db.Column(db.Integer,primary_key=True);title=db.Column(db.String(180),nullable=False);filename=db.Column(db.String(255),nullable=False);kind=db.Column(db.String(50),default='Arquivo');active=db.Column(db.Boolean,default=True)
@login.user_loader
def load_user(uid):return db.session.get(Admin,int(uid))
ALLOWED={'pdf','png','jpg','jpeg','webp','svg','mp4','webm'}
def save_upload(f):
 if not f or not f.filename:return None
 ext=f.filename.rsplit('.',1)[-1].lower()
 if ext not in ALLOWED:return None
 name=f'{uuid.uuid4().hex}.{ext}';f.save(Path(app.config['UPLOAD_FOLDER'])/name);return name
def seed():
 db.create_all()
 if not Admin.query.first():a=Admin(name='Administrador',email='admin@uniao.local');a.set_password('admin123');db.session.add(a)
 if not Region.query.first():
  for n,s in [('Paraíba','PB'),('Rio Grande do Norte','RN'),('Pernambuco','PE'),('Ceará','CE')]:db.session.add(Region(name=n,state=s))
 if not SiteSettings.query.first():db.session.add(SiteSettings(company_name='União'))
 db.session.commit()
with app.app_context():seed()
@app.get('/')
def home():
    sellers=Seller.query.filter_by(active=True).all()
    seller_data=[{'id':x.id,'name':x.name,'phone':x.phone,'role':x.role,'state':x.state,'city':x.city,'lat':x.lat,'lng':x.lng} for x in sellers]
    return render_template('site.html',settings=SiteSettings.query.first(),sellers=sellers,seller_data=seller_data,downloads=Download.query.filter_by(active=True).all(),regions=Region.query.all())

@app.get('/health')
def health():
    return {'status':'ok'}
@app.get('/download/<path:name>')
def download(name):return send_from_directory(app.config['UPLOAD_FOLDER'],name,as_attachment=True)
@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
 if request.method=='POST':
  a=Admin.query.filter_by(email=request.form['email'].strip().lower()).first()
  if a and a.check_password(request.form['password']):login_user(a);return redirect(url_for('dashboard'))
  flash('E-mail ou senha inválidos.','error')
 return render_template('login.html')
@app.get('/admin/logout')
@login_required
def admin_logout():logout_user();return redirect(url_for('admin_login'))
@app.get('/admin')
@login_required
def dashboard():return render_template('admin/dashboard.html',settings=SiteSettings.query.first(),sellers=Seller.query.all(),regions=Region.query.all(),downloads=Download.query.all())
@app.post('/admin/settings')
@login_required
def settings():
 s=SiteSettings.query.first()
 for k in ['company_name','story','showroom_phone','showroom_whatsapp','address']:setattr(s,k,request.form.get(k,''))
 for field in ['logo','hero_media','current_photo','old_photo','fleet_media']:
  f=save_upload(request.files.get(field))
  if f:setattr(s,field,f)
 db.session.commit();flash('Informações atualizadas.','ok');return redirect(url_for('dashboard'))
@app.post('/admin/sellers/save')
@login_required
def seller_save():
 sid=request.form.get('id');x=db.session.get(Seller,int(sid)) if sid else Seller();x.name=request.form['name'];x.phone=request.form['phone'];x.role=request.form.get('role','Vendedor');x.state=request.form.get('state','');x.city=request.form.get('city','');x.lat=float(request.form.get('lat') or 0);x.lng=float(request.form.get('lng') or 0);x.region_id=int(request.form['region_id']) if request.form.get('region_id') else None;x.active=True;db.session.add(x);db.session.commit();return redirect(url_for('dashboard'))
@app.post('/admin/sellers/delete/<int:id>')
@login_required
def seller_delete(id):db.session.delete(db.session.get(Seller,id));db.session.commit();return redirect(url_for('dashboard'))
@app.post('/admin/regions/save')
@login_required
def region_save():db.session.add(Region(name=request.form['name'],state=request.form['state'].upper()));db.session.commit();return redirect(url_for('dashboard'))
@app.post('/admin/regions/delete/<int:id>')
@login_required
def region_delete(id):db.session.delete(db.session.get(Region,id));db.session.commit();return redirect(url_for('dashboard'))
@app.post('/admin/downloads/save')
@login_required
def download_save():
 f=request.files.get('file');saved=save_upload(f)
 if saved:db.session.add(Download(title=request.form['title'],filename=saved,kind=request.form.get('kind','Arquivo')));db.session.commit()
 return redirect(url_for('dashboard'))
@app.post('/admin/downloads/delete/<int:id>')
@login_required
def download_delete(id):db.session.delete(db.session.get(Download,id));db.session.commit();return redirect(url_for('dashboard'))
@app.get('/api/sellers')
def api_sellers():return jsonify([{'id':x.id,'name':x.name,'phone':x.phone,'role':x.role,'state':x.state,'city':x.city,'lat':x.lat,'lng':x.lng} for x in Seller.query.filter_by(active=True)])
if __name__=='__main__':
    port=int(os.getenv('PORT','5000'))
    app.run(host='0.0.0.0',port=port,debug=False)
