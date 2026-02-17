# Round Robin interactivo - Processing (Python Mode)
# -------------------------------------------------
# Uso:
#  - Haz click en los campos para escribir.
#  - "Agregar proceso" añade el proceso a la lista (no inicia la simulación).
#  - Pon el valor de q (quantum) y presiona "Iniciar" para comenzar.
#  - "Limpiar" borra los procesos (antes de iniciar).
#
# Nota: cada "unidad de tiempo" avanza por defecto cada 450 ms.
# Puedes cambiar speed (time_unit_ms) con los botones + / - en pantalla.

# -----------------------
# Datos / UI / Variables
# -----------------------
process_list = []  # procesos pendientes (antes de iniciar)
next_pid = 1

# Campos de texto (strings)
q_input = "2"
name_input = ""
arrival_input = "0"
burst_input = "5"

active_field = None  # 'q','name','arrival','burst' o None

# UI rectangles (pos, tamaño)
ui = {
    "q_box": (20, 40, 80, 28),
    "name_box": (20, 100, 120, 28),
    "arrival_box": (150, 100, 80, 28),
    "burst_box": (250, 100, 80, 28),
    "add_btn": (350, 100, 120, 28),
    "start_btn": (20, 150, 120, 32),
    "clear_btn": (160, 150, 120, 32),
    "faster_btn": (20, 200, 36, 24),
    "slower_btn": (60, 200, 36, 24),
}

# Simulation runtime state
running = False
quantum = 2
time_unit_ms = 450  # ms per simulation time unit (tick)
last_tick = 0
current_time = 0

# Round Robin structures
ready_queue = []  # queue of indices into running_processes? We'll store dict refs
running_proc = None  # dict of the currently executing process
slice_left = 0

gantt = []  # list of segments: {name, start, dur, color}
scroll_x = 0

# For statistics
finished = []

# -----------------------
# Helper functions
# -----------------------
def make_process(name, arrival, burst):
    global next_pid
    col = color(int(random(80, 240)), int(random(80, 240)), int(random(80, 240)))
    p = {
        "pid": next_pid,
        "name": name if name.strip() != "" else "P{}".format(next_pid),
        "arrival": int(arrival),
        "burst": int(burst),
        "remaining": int(burst),
        "color": col,
        "started": False,
        "finish": None,
        "segments": []  # list of (start, dur) for Gantt
    }
    next_pid += 1
    return p

def reset_simulation():
    global running, ready_queue, running_proc, slice_left, gantt, finished, current_time, last_tick
    running = False
    ready_queue = []
    running_proc = None
    slice_left = 0
    gantt = []
    finished = []
    current_time = 0
    last_tick = millis()

def start_sim():
    global running, quantum, q_input, time_unit_ms, last_tick, current_time, ready_queue
    try:
        q = int(q_input)
        if q <= 0:
            raise ValueError()
        quantum = q
    except:
        print("Quantum invalido. Usar 3.")
        quantum = 3
        q_input = "3"
    # prepare pending processes sorted by arrival
    process_list.sort(key=lambda p: p["arrival"])
    # reset runtime structures
    reset_simulation()
    running = True
    last_tick = millis()
    # ready_queue empty initially; arrivals will be moved when time advances

# -----------------------
# Simulation tick logic
# -----------------------
def tick():
    global current_time, last_tick, running_proc, slice_left, ready_queue, gantt, finished
    # 1) check arrivals at this time
    to_add = [p for p in process_list if p["arrival"] == current_time and p not in ready_queue and (p["finish"] is None and p not in finished)]
    for p in to_add:
        ready_queue.append(p)
    # 2) if no running_proc, pick from queue
    if running_proc is None:
        if len(ready_queue) > 0:
            running_proc = ready_queue.pop(0)
            # start segment in Gantt (start time)
            running_proc["segments"].append({"start": current_time, "dur": 0})
            slice_left = min(quantum, running_proc["remaining"])
            running_proc["started"] = True
    # 3) execute 1 time unit
    if running_proc is not None:
        running_proc["remaining"] -= 1
        slice_left -= 1
        # extend current segment's dur
        running_proc["segments"][-1]["dur"] += 1
        # check completion
        if running_proc["remaining"] <= 0:
            # finished at time current_time+1 (end of this tick)
            running_proc["finish"] = current_time + 1
            finished.append(running_proc)
            # add segment to global Gantt
            gantt.append({"name": running_proc["name"], "start": running_proc["segments"][-1]["start"], "dur": running_proc["segments"][-1]["dur"], "color": running_proc["color"]})
            running_proc = None
            slice_left = 0
        elif slice_left <= 0:
            # time slice expired, preempt and queue end
            # close segment and add to gantt segments list (we'll append full segments)
            gantt.append({"name": running_proc["name"], "start": running_proc["segments"][-1]["start"], "dur": running_proc["segments"][-1]["dur"], "color": running_proc["color"]})
            # enqueue to end (process may arrive again later but already in queue)
            ready_queue.append(running_proc)
            running_proc = None
    # 4) increment time
    current_time += 1

# -----------------------
# Processing lifecycle
# -----------------------
def setup():
    size(1100, 720)
    textFont(createFont("Arial", 12))
    frameRate(60)
    global last_tick
    last_tick = millis()

def draw():
    global last_tick, scroll_x
    background(28)
    draw_ui()
    # run simulation ticks depending on time elapsed
    if running:
        now = millis()
        # may do multiple ticks if lagging behind
        while now - last_tick >= time_unit_ms:
            # if all done, stop
            pending = [p for p in process_list if p not in finished and p["remaining"] > 0]
            any_pending = len(pending) > 0 or (running_proc is not None) or (len(ready_queue) > 0) or any(p["arrival"] >= current_time for p in process_list)
            # If nothing to do and no future arrivals -> stop
            # But we must still consider future arrivals > current_time; let tick run until all finished
            tick()
            last_tick += time_unit_ms
            now = millis()
        draw_simulation()
    else:
        draw_process_list()

def draw_ui():
    # Title and q input
    fill(230)
    textSize(20)
    text("Simulacion Round Robin", 20, 20)
    textSize(12)
    # q box
    x,y,w,h = ui["q_box"]
    fill(200 if active_field == "q" else 245)
    rect(x,y,w,h,4)
    fill(0)
    textAlign(LEFT, CENTER)
    text("q =", x-28, y+14)
    text(q_input, x+6, y+14)
    # fields
    x,y,w,h = ui["name_box"]
    fill(200 if active_field == "name" else 245)
    rect(x,y,w,h,4)
    fill(0)
    textAlign(LEFT, CENTER)
    text("Nombre:", x+6, y+14)
    text(name_input, x+70, y+14)
    x,y,w,h = ui["arrival_box"]
    fill(200 if active_field == "arrival" else 245)
    rect(x,y,w,h,4)
    fill(0)
    text("C:", x+6, y+14)
    text(arrival_input, x+24, y+14)
    x,y,w,h = ui["burst_box"]
    fill(200 if active_field == "burst" else 245)
    rect(x,y,w,h,4)
    fill(0)
    text("t:", x+6, y+14)
    text(burst_input, x+24, y+14)
    # Add button
    x,y,w,h = ui["add_btn"]
    fill(120,180,120)
    rect(x,y,w,h,6)
    fill(0)
    textAlign(CENTER, CENTER)
    text("Agregar proceso", x+w/2, y+h/2)
    # Start / Clear
    x,y,w,h = ui["start_btn"]
    fill(80, 170, 220)
    rect(x,y,w,h,6)
    fill(0)
    text("Iniciar", x+w/2, y+h/2)
    x,y,w,h = ui["clear_btn"]
    fill(220, 90, 90)
    rect(x,y,w,h,6)
    fill(0)
    text("Limpiar", x+w/2, y+h/2)
    # speed buttons
    x,y,w,h = ui["faster_btn"]
    fill(200)
    rect(x,y,w,h,4)
    fill(0)
    text("+", x+w/2, y+h/2)
    x,y,w,h = ui["slower_btn"]
    fill(200)
    rect(x,y,w,h,4)
    fill(0)
    text("-", x+w/2, y+h/2)
    # instructions
    textAlign(LEFT)
    fill(200)
    text("Click en campos para editar. Agrega procesos antes de Iniciar. Scroll Gantt con las flechas", 20, 240)
    text("Velocidad de tick (ms): {}".format(time_unit_ms), 20, 260)

def draw_process_list():
    # show processes pending to start
    fill(240)
    textSize(14)
    text("Lista de procesos (pendientes):", 20, 300)
    y = 330
    textSize(12)
    for p in process_list:
        fill(p["color"])
        rect(20, y-14, 18, 18)
        fill(230)
        textAlign(LEFT, CENTER)
        text("{}  | C={}  | t={}  | rem={}".format(p["name"], p["arrival"], p["burst"], p["remaining"]), 50, y)
        y += 26

def draw_simulation():
    # Top: current time and ready queue / running
    textSize(14)
    fill(230)
    text("Tiempo: {}".format(current_time), 420, 40)
    # Running
    textSize(12)
    fill(200)
    text("CPU:", 420, 70)
    if running_proc is not None:
        fill(running_proc["color"])
        rect(460, 56, 160, 30, 4)
        fill(0)
        text("{}  rem={}  sliceLeft={}".format(running_proc["name"], running_proc["remaining"], slice_left), 540, 71)
    else:
        fill(80)
        rect(460, 56, 160, 30, 4)
        fill(200)
        text("IDLE", 540, 71)
    # Ready queue
    fill(200)
    text("Ready queue (orden):", 420, 110)
    x = 420
    y = 130
    for p in ready_queue:
        fill(p["color"])
        rect(x, y, 60, 30, 4)
        fill(0)
        textAlign(CENTER, CENTER)
        text(p["name"], x+30, y+15)
        x += 70
    # Gantt chart
    draw_gantt(20, 320, width - 60, 160)

    # finished stats
    draw_stats(700, 100)

def draw_gantt(x, y, w, h):
    global scroll_x
    # header
    textSize(13)
    fill(200)
    text("Gantt (segmentos):", x, y-18)
    # timeline scale: 1 unit = 22 px
    unit_w = 22
    pushMatrix()
    translate(x, y)
    noStroke()
    # draw finished segments from gantt list
    for seg in gantt:
        sx = seg["start"] * unit_w + scroll_x
        sw = seg["dur"] * unit_w
        # skip if off-screen
        if sx + sw < 0 or sx > w:
            continue
        fill(seg["color"])
        rect(sx, 0, sw, 30, 4)
        fill(0)
        textAlign(CENTER, CENTER)
        # draw label if wide enough
        if sw >= 28:
            text(seg["name"], sx + sw/2, 15)
    # draw running process current segment (not yet in gantt)
    if running_proc is not None and len(running_proc["segments"])>0:
        seg = running_proc["segments"][-1]
        sx = seg["start"] * unit_w + scroll_x
        sw = seg["dur"] * unit_w
        fill(running_proc["color"])
        rect(sx, 40, sw, 30, 4)
        fill(0)
        if sw >= 28:
            text(running_proc["name"], sx + sw/2, 55)
    # draw time ticks
    stroke(120)
    for t in range(max(0, int((-scroll_x)/unit_w)-1), int((w - scroll_x)/unit_w)+5):
        tx = t * unit_w
        if tx < -unit_w or tx > w + unit_w:
            continue
        line(tx, 90, tx, 95)
        fill(180)
        textAlign(CENTER, TOP)
        text(str(t), tx, 95)
    popMatrix()

def draw_stats(x, y):
    textSize(12)
    fill(200)
    text("Terminados ({}):".format(len(finished)), x, y)
    yy = y + 18
    textAlign(LEFT)
    for p in finished:
        tat = p["finish"] - p["arrival"]
        wt = tat - p["burst"]
        text("{}  C={}  t={}  finish={}  TAT={}  WT={}".format(p["name"], p["arrival"], p["burst"], p["finish"], tat, wt), x, yy)
        yy += 18

# -----------------------
# Input handlers
# -----------------------
def mousePressed():
    global active_field, scroll_x
    mx, my = mouseX, mouseY
    # check q box
    x,y,w,h = ui["q_box"]
    if collide(mx,my,x,y,w,h):
        active_field = "q"
        return
    x,y,w,h = ui["name_box"]
    if collide(mx,my,x,y,w,h):
        active_field = "name"
        return
    x,y,w,h = ui["arrival_box"]
    if collide(mx,my,x,y,w,h):
        active_field = "arrival"
        return
    x,y,w,h = ui["burst_box"]
    if collide(mx,my,x,y,w,h):
        active_field = "burst"
        return
    # Add button
    x,y,w,h = ui["add_btn"]
    if collide(mx,my,x,y,w,h):
        add_process_from_inputs()
        active_field = None
        return
    # Start button
    x,y,w,h = ui["start_btn"]
    if collide(mx,my,x,y,w,h):
        if not running:
            start_sim()
        return
    # Clear button
    x,y,w,h = ui["clear_btn"]
    if collide(mx,my,x,y,w,h):
        if not running:
            clear_processes()
        return
    # speed
    x,y,w,h = ui["faster_btn"]
    if collide(mx,my,x,y,w,h):
        change_speed(-80)
        return
    x,y,w,h = ui["slower_btn"]
    if collide(mx,my,x,y,w,h):
        change_speed(80)
        return
    # click outside -> deactivate field
    active_field = None
    # scroll Gantt by clicking left/right halves of the Gantt area
    # (or use keyboard ← →)
    gx, gy, gw, gh = 20, 320, width-60, 160
    if mx > gx and mx < gx+gw and my > gy and my < gy+gh:
        # if clicked near left half -> scroll left, else right
        if mx < gx + gw/2:
            scroll_x += 200
        else:
            scroll_x -= 200

def keyPressed():
    global active_field, q_input, name_input, arrival_input, burst_input, scroll_x

    # ---- Si estamos escribiendo en un textbox ----
    if active_field is not None:

        # BACKSPACE
        if key == BACKSPACE:
            remove_last_char()
            return

        # ENTER termina edición
        if keyCode == ENTER or keyCode == RETURN:
            active_field = None
            return

        # Solo aceptar caracteres imprimibles
        if key != CODED:
            c = key

            if active_field == "q":
                if c.isdigit():
                    q_input += c

            elif active_field == "name":
                # aceptar letras, números y _
                if c.isalnum() or c == "_":
                    name_input += c

            elif active_field == "arrival":
                if c.isdigit():
                    arrival_input += c

            elif active_field == "burst":
                if c.isdigit():
                    burst_input += c

        return

    # ---- Si NO estamos escribiendo ----
    if key == CODED:
        if keyCode == LEFT:
            scroll_x += 60
        elif keyCode == RIGHT:
            scroll_x -= 60

    # Espacio pausa/reanuda
    if key == ' ':
        toggle_pause()

def append_char_to_field(field, ch):
    global q_input, name_input, arrival_input, burst_input
    if field == "q":
        q_input += ch
    elif field == "name":
        name_input += ch
    elif field == "arrival":
        arrival_input += ch
    elif field == "burst":
        burst_input += ch

def remove_last_char():
    global q_input, name_input, arrival_input, burst_input
    if active_field == "q":
        q_input = q_input[:-1]
    elif active_field == "name":
        name_input = name_input[:-1]
    elif active_field == "arrival":
        arrival_input = arrival_input[:-1]
    elif active_field == "burst":
        burst_input = burst_input[:-1]

# -----------------------
# Utility actions
# -----------------------
def add_process_from_inputs():
    global arrival_input, burst_input, name_input, process_list
    # validate arrival and burst
    try:
        a = int(arrival_input)
        b = int(burst_input)
        if b <= 0:
            raise ValueError()
    except:
        print("Entrada inválida. arrival y burst deben ser enteros (burst>0).")
        return
    p = make_process(name_input, a, b)
    process_list.append(p)
    # reset small fields
    name_input = ""
    arrival_input = "0"
    burst_input = "1"

def clear_processes():
    global process_list, next_pid
    process_list = []
    next_pid = 1

def change_speed(delta):
    global time_unit_ms
    time_unit_ms = max(50, time_unit_ms + delta)

def toggle_pause():
    global running
    running = not running

def collide(mx,my,x,y,w,h):
    return mx >= x and mx <= x+w and my >= y and my <= y+h
