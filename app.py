from flask import Flask,render_template,Response, request,send_file
import cv2
import os,sys
from threading import Thread

app=Flask(__name__)

global camera,switch,rec_frame,fourcc,out,now,cap
cap = 0
now = 1
rec_frame = 0
switch = 1
camera=cv2.VideoCapture(0)


try:
    os.mkdir('./shots')
except OSError as error:
    pass

def rec(out):
    global rec_frame,camera
    while rec_frame:

        ret, frame = camera.read()
        if ret==True:
            frame = cv2.flip(frame,1)
            # write the flipped frame
            out.write(frame)
            

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

def capture(p):
    global camera
    ret, frame = camera.read()
    if ret:
        cv2.imwrite(p,frame)
    


def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            
            frame = cv2.flip(frame,1)
            frame=buffer.tobytes()
            
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    global cap,rec_frame,now
    return render_template('index.html',rec = rec_frame,cap = cap,now = now)

@app.route('/downloadImg')
def downloadImg():
    global cap
    cap_path = './shots/capture_{}.jpg'.format(str(cap))
    return send_file(cap_path, as_attachment=True)

@app.route('/downloadrec')
def downloadrec():
    global now
    rec_path = './capture/output_{}.avi'.format(str(now))
    return send_file(rec_path, as_attachment=True)
    


@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods = ['POST','GET'])
def tasks():
    global switch,camera,rec_frame,out,now,cap
    if request.method == 'POST':
        if request.form.get('on/off'):
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif request.form.get('rec'):
            
            rec_frame = not rec_frame
            if rec_frame:
                 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('./capture/output_{}.avi'.format(str(now)),fourcc, 20.0, (640,480))
                thread = Thread(target = rec, args=[out,])
                thread.start()
            elif rec_frame == False:
                now+=1
                out.release()

        elif request.form.get('capture'):
           
            cap += 1
            p = "./shots/capture_{}.jpg".format(cap)
            capture(p)



    elif request.method == 'GET':
        return render_template('index.html',rec = rec_frame, cap = cap,now = now)
    
    return render_template('index.html',rec = rec_frame, cap = cap,now = now)

if __name__=="__main__":
    app.run(debug=True)
