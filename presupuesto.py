from flask import Flask, render_template, request, redirect, send_from_directory,url_for
from flask_redis import Redis
import redis
import os

app = Flask(__name__)
r = Redis(app)

@app.route('/',methods=['POST','GET'])
def index():
  nombre = 'sin nombre'
  if request.method == 'POST':
    print request.form['nombre']
    nombre= request.form['nombre']
  return render_template('index.html',  nombre=nombre)

@app.route('/reporte')
def hello_world():
  datos = []
  categorias = r.lrange('categoria',0,-1)
  a_gastar = r.lrange('a_gastar',0,-1)
  gastado = r.lrange('gastado',0,-1)
  tipos = r.lrange('tipos',0,-1)
  fechas = r.lrange('fechas',0,-1)
  index = 0
  dat = []
  for categoria in categorias:
    dat.append(categorias[index])
    valor=int(gastado[index])*100/int(a_gastar[index])
    dat.append(a_gastar[index])
    dat.append(gastado[index])
    promedio=int(gastado[index])*100/int(a_gastar[index])
    dat.append(str(promedio)+'%')
    dat.append(tipos[index])
    dat.append(fechas[index])
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
      print str(index)
      if categoria == request.form['categorias']:
        r.lset('presupuestos',index,int(r.lindex('presupuestos',index))+int(request.form['dinero']))
      index= index+1
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
  return render_template('presupuestar.html', presupuestos=presupuestos, datos=datos, usuario ='Antonio',categorias=categorias)


@app.route('/gastos/<numero>',methods=['POST','GET'])
def gastos(numero):
  mensaje = None
  if request.method== 'POST':
    gasto = -1
    try:
      gasto= int(request.form['gasto'])
      mensaje = 'Gastaste {0} en {1}'.format(str(gasto),request.form['categorias'])
      r.lpush('gastos:%s'%request.form['categorias'],gasto)
      print 'se guardo correctamente'
      return redirect(url_for('gastos',numero=3))
    except ValueError:
      mensaje = 'No puedes gastar %s' %request.form['gasto']
  categorias = r.lrange('categoria',0,-1)
  gastos1 = []
  cat = []
  datos = []
  for categoria in categorias:
    gastos = r.lrange('gastos:%s'%categoria,0,-1)
    for gasto in gastos:
      dato=[]
      dato.append(gasto)
      dato.append(categoria)
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
      print 'paso el gasto =  sabe que'
      mensaje = 'Gastaste {0} en {1}'.format(str(gasto),request.form['categorias'])
      r.lpush('gastos:%s'%request.form['categorias'],gasto)
      print 'se guardo correctamente'
      return redirect(url_for('gastos',numero=3))
    except ValueError:
      mensaje = 'No puedes gastar %s' %request.form['gasto']
  categorias = r.lrange('categoria',0,-1)
  return render_template('gastar.html',categorias=categorias, mensaje = mensaje)

@app.route('/nueva_categoria',methods=['POST','GET'])
def nueva_categoria():
  if request.method == 'POST':
    print request.form['nombre']
    print request.form['fecha']
    print request.form['tipo']
    print request.form['a_pagar']
  return render_template('nueva_categoria.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0')

