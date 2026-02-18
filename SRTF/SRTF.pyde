# ==============================
# SRTF Interactive Simulator
# Processing - Python Mode
# ==============================

processes = []
ready_queue = []
current = None
time_tick = 0
running = False
finished = False

time_unit_ms = 450
last_step = 0

active_field = None
input_name = ""
input_arrival = ""
input_burst = ""

# ------------------------------
# Setup
# ------------------------------
def setup():
    size(1000, 600)
    textSize(16)

# ------------------------------
# Draw Loop
# ------------------------------
def draw():
    global last_step, time_tick, running, finished
    
    background(30)
    
    drawUI()
    drawProcesses()
    
    if running and not finished:
        if millis() - last_step > time_unit_ms:
            simulate_step()
            last_step = millis()

# ------------------------------
# Simulation Step (SRTF)
# ------------------------------
def simulate_step():
    global time_tick, current, finished
    
    # Add arriving processes
    for p in processes:
        if p["arrival"] == time_tick:
            ready_queue.append(p)
    
    # Remove finished processes
    ready_queue[:] = [p for p in ready_queue if p["remaining"] > 0]
    
    # Stop if no processes left
    if all(p["remaining"] <= 0 for p in processes):
        finished = True
        running = False
        return
    
    # Choose shortest remaining
    if ready_queue:
        current = min(ready_queue, key=lambda x: x["remaining"])
        current["remaining"] -= 1
    
    time_tick += 1

# ------------------------------
# Draw UI
# ------------------------------
def drawUI():
    fill(255)
    text("SRTF - Short Remaining Time First", 30, 30)
    text("Tiempo actual: " + str(time_tick), 30, 60)
    text("Velocidad: " + str(time_unit_ms) + " ms", 30, 90)
    
    # Input fields
    drawField(30, 130, 120, 30, input_name, "Nombre", "name")
    drawField(170, 130, 120, 30, input_arrival, "Llegada", "arrival")
    drawField(310, 130, 120, 30, input_burst, "Ráfaga", "burst")
    
    # Buttons
    drawButton(450,130,160,30,"Agregar proceso")
    drawButton(630,130,120,30,"Limpiar")
    drawButton(770,130,120,30,"Iniciar")
    drawButton(910,130,80,30,"Parar")
    
    drawButton(200,80,40,30,"+")
    drawButton(250,80,40,30,"-")

# ------------------------------
# Draw Process List
# ------------------------------
def drawProcesses():
    y = 200
    for p in processes:
        fill(70,120,200)
        rect(30, y, p["remaining"]*25, 30)
        fill(255)
        text(p["name"] + 
             " (L:" + str(p["arrival"]) +
             ", R:" + str(p["remaining"]) + ")", 40, y+20)
        y += 50

# ------------------------------
# Input Field
# ------------------------------
def drawField(x,y,w,h,value,label,field_id):
    global active_field
    stroke(255)
    if active_field == field_id:
        fill(60)
    else:
        fill(45)
    rect(x,y,w,h)
    fill(255)
    text(value, x+5, y+20)
    text(label, x, y-5)

# ------------------------------
# Button
# ------------------------------
def drawButton(x,y,w,h,label):
    fill(100)
    rect(x,y,w,h)
    fill(255)
    text(label, x+10, y+20)

# ------------------------------
# Mouse Click
# ------------------------------
def mousePressed():
    global active_field, running, processes, time_tick, finished, time_unit_ms
    
    # Fields
    if inside(30,130,120,30): active_field="name"
    elif inside(170,130,120,30): active_field="arrival"
    elif inside(310,130,120,30): active_field="burst"
    else: active_field=None
    
    # Buttons
    if inside(450,130,160,30):
        add_process()
    elif inside(630,130,120,30):
        if not running:
            processes[:] = []
            time_tick = 0
            finished = False
    elif inside(770,130,120,30):
        running = True
        finished = False
    elif inside(910,130,80,30):
        running = False
    elif inside(200,80,40,30):
        time_unit_ms = max(50, time_unit_ms - 50)
    elif inside(250,80,40,30):
        time_unit_ms += 50

# ------------------------------
# Add Process
# ------------------------------
def add_process():
    global input_name, input_arrival, input_burst
    if input_name and input_arrival.isdigit() and input_burst.isdigit():
        processes.append({
            "name": input_name,
            "arrival": int(input_arrival),
            "burst": int(input_burst),
            "remaining": int(input_burst)
        })
        input_name=""
        input_arrival=""
        input_burst=""

# ------------------------------
# Keyboard Input
# ------------------------------
def keyPressed():
    global input_name, input_arrival, input_burst
    
    if active_field == "name":
        if key == BACKSPACE:
            input_name = input_name[:-1]
        else:
            input_name += key
            
    elif active_field == "arrival":
        if key == BACKSPACE:
            input_arrival = input_arrival[:-1]
        elif key.isdigit():
            input_arrival += key
            
    elif active_field == "burst":
        if key == BACKSPACE:
            input_burst = input_burst[:-1]
        elif key.isdigit():
            input_burst += key

# ------------------------------
# Helper
# ------------------------------
def inside(x,y,w,h):
    return mouseX>x and mouseX<x+w and mouseY>y and mouseY<y+h
