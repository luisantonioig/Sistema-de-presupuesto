from flask import Flask, flash, render_template, request, redirect, send_from_directory,url_for
from flask_redis import Redis
import redis
import os

app = Flask(__name__)
r = Redis(app)
app.secret_key = 'secreto'

@app.route('/',methods=['POST','GET'])
def index():
  flash('Bienvenido al "Sistema de presupuesto"')
  nombre = 'sin nombre'
  if request.method == 'POST':
    print request.form['nombre']
    nombre= request.form['nombre']
  return render_template('index.html',  nombre=nombre)

@app.route('/index')
def iicio():
  flash('Este es un mensaje flash jaja')
  return redirect(url_for('index'))

@app.route('/reporte')
def hello_world():
  datos = []
  categorias = r.lrange('categoria',0,-1)
  a_gastar = r.lrange('a_gastar',0,-1)
  gastado = r.lrange('gastado',0,-1)
  index = 0
  dat = []
  for categoria in categorias:
    gasto_categoria = r.lrange('gastos:%s'%categoria,0 , -1)
    gast= sum([int(i) for i in gasto_categoria])
    dat.append(categorias[index])
    valor=int(gastado[index])*100/int(a_gastar[index])
    dat.append(a_gastar[index])
    dat.append(gast)
    promedio=int(gast)*100/int(a_gastar[index])
    dat.append(str(promedio)+'%')
    datos.append(dat)
    dat = []
    index= index+1
  return render_template('reporte.html', datos=datos, usuario = 'Esto es el usuario')

@app.route('/presupuesto')
def presupuesto():
  categorias =r.lrange('categoria',0,-1)
  presupuestos = r.lrange('presupuestos',0,-1)
  index =0
  datos= []
  for presupuesto in presupuestos:
    dat=[]
    dat.append(categorias[index])
    dat.append(presupuestos[index])
    datos.append(dat)
    index=index+1
  return render_template('presupuestos.html', presupuestos=presupuestos,datos=datos,usuario='Antonio :D')

@app.route('/presupuestar',methods=['POST','GET'])
def presupuestar():
  if request.method == 'POST':
    categorias = r.lrange('categoria',0,-1)
    index = 0
    print categorias
    for categoria in categorias:
      if categoria == request.form['categorias']:
        if int(r.get('dinero_para_presupuestar'))-int(request.form['dinero']) < 0:
          flash('No puedes presupuestar %s'%request.form['dinero'])
        else:
          presupuesto = int(r.lindex('presupuestos',index))+int(request.form['dinero'])
          r.lset('presupuestos',index,presupuesto)
          r.set('dinero_para_presupuestar',int(r.get('dinero_para_presupuestar'))-int(request.form['dinero']))
          flash('Dinero presupuestado')
      index= index+1
  dinero_para_presupuestar = r.get('dinero_para_presupuestar')
  categorias =r.lrange('categoria',0,-1)
  presupuestos = r.lrange('presupuestos',0,-1)
  index =0
  datos= []
  for presupuesto in presupuestos:
    dat=[]
    dat.append(categorias[index])
    dat.append(presupuestos[index])
    datos.append(dat)
    index=index+1
  return render_template('presupuestar.html', presupuestos=presupuestos, datos=datos, usuario ='Antonio',categorias=categorias,dinero_para_presupuestar=dinero_para_presupuestar)


@app.route('/gastos/<numero>',methods=['POST','GET'])
def gastos(numero):
  mensaje = None
  if request.method== 'POST':
    gasto = -1
    try:
      gasto= int(request.form['gasto'])
      mensaje = 'Gastaste {0} en {1}'.format(str(gasto),request.form['categorias'])
      r.lpush('gastos:%s'%request.form['categorias'],gasto)
      import time
      print time.strftime("%d/%m/%y")
      r.lpush('fechas_gastos',time.strftime("%d/%m/%y"))
      index = 0
      categorias = r.lrange('categorias',0,-1)
      for categoria in categorias:
        if categoria == request.form['categorias']:
          r.lset('presupuestos',index,r.lindex('presupuestos')-gasto)
        index=index+1
      return redirect(url_for('gastos',numero=3))
    except ValueError:
      mensaje = 'No puedes gastar %s' %request.form['gasto']
  fechas = r.lrange('fechas_gastos',0,-1)
  categorias = r.lrange('categoria',0,-1)
  gastos1 = []
  cat = []
  datos = []
  index = 0
  for categoria in categorias:
    gastos = r.lrange('gastos:%s'%categoria,0,-1)
    for gasto in gastos:
      dato=[]
      dato.append(gasto)
      dato.append(categoria)
      dato.append(fechas[index])
      index = index + 1
      datos.append(dato)
      gastos1.append(gasto)
      cat.append(categoria)
  gastos = r.lrange('gastos',0 , -1)
  categorias = r.lrange('categoria',0,-1)
  return render_template('gastos.html', gastos=gastos1,categoria= cat,datos=datos,categorias=categorias,mensaje=None)

@app.route('/gastar', methods=['POST','GET'])
def gastar():
  mensaje = None
  if request.method== 'POST':
    gasto = -1
    try:
      gasto= int(request.form['gasto'])
      mensaje = 'Gastaste {0} en {1}'.format(str(gasto),request.form['categorias'])
      import time
      index = 0
      categorias = r.lrange('categoria',0,-1)
      for categoria in categorias:
        if categoria == request.form['categorias']:
          print r.lindex('presupuestos',index)
          print gasto
          if int(r.lindex('presupuestos',index))-gasto < 0 or gasto <= 0:
            flash('No puedes gastar %s'%gasto)
          else:
            r.lset('presupuestos',index,int(r.lindex('presupuestos',index))-gasto)
            r.lpush('fechas_gastos',time.strftime("%d/%m/%y"))
            r.lpush('gastos:%s'%request.form['categorias'],gasto)
            flash('gastaste %s'%gasto)
        index=index+1
      flash("gastaste :D")
      return redirect(url_for('gastos',numero=3))
    except ValueError:
      flash('No puedes gastar %s' %request.form['gasto'])
      return redirect(url_for('gastos',numero=3))
  categorias = r.lrange('categoria',0,-1)
  return render_template('gastar.html',categorias=categorias, mensaje = mensaje)

@app.route('/nueva_categoria',methods=['POST','GET'])
def nueva_categoria():
  if request.method == 'POST':
    print request.form['nombre']
    print request.form['presupuesto']
    print request.form['temporizar']
    print request.form['a_gastar']
    print request.form['de']
    print request.form['a']
    print request.form['repetir']
    if request.form['temporizar'] == 'on':
      print 'categoria temporizada'
    else:
      print 'categoria no temporizada'
    if request.form['nombre'] in r.lrange('categoria', 0,-1):
      flash('Ya existe esa categoria')
    else:
      r.lpush('categoria', request.form['nombre'])
      print request.form['presupuesto']
      r.lpush('presupuestos', request.form['presupuesto'])
      print 'Ya se guardo :D'
      r.lpush('a_gastar', request.form['a_gastar'])
      r.lpush('gastado',0)
      r.lpush('de',request.form['de'])
      r.lpush('a', request.form['a'])
      r.lpush('repetir', request.form['repetir'])
      flash('Guardado')
  return render_template('nueva_categoria.html')

@app.route('/categoria')
def categoria():
  return render_template('categoria.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0')
