# Simulación simple de una Cola FIFO en Processing (Python Mode)

queue = []
counter = 1  # Para numerar los elementos

def setup():
    size(900, 300)
    textAlign(CENTER, CENTER)
    textSize(16)

def draw():
    background(30)
    
    draw_title()
    draw_queue()
    draw_instructions()

def draw_title():
    fill(255)
    textSize(20)
    text("Simulacion Cola FIFO", width/2, 30)

def draw_queue():
    global queue
    
    start_x = 100
    y = height / 2
    
    for i in range(len(queue)):
        x = start_x + i * 90
        
        # Dibujar rectángulo
        fill(70, 130, 180)
        rect(x, y - 30, 80, 60)
        
        # Dibujar texto
        fill(255)
        text(str(queue[i]), x + 40, y)

    # Indicadores
    if len(queue) > 0:
        fill(0, 255, 0)
        text("FRONT", start_x + 40, y - 50)
        
        fill(255, 0, 0)
        text("REAR", start_x + (len(queue)-1)*90 + 40, y + 50)

def draw_instructions():
    fill(200)
    textSize(14)
    text("Presiona 'A' para agregar | 'R' para remover | 'C' para limpiar", width/2, height - 30)

def keyPressed():
    global counter
    
    if key == 'a' or key == 'A':
        enqueue()
    elif key == 'r' or key == 'R':
        dequeue()
    elif key == 'c' or key == 'C':
        clear_queue()

def enqueue():
    global queue, counter
    queue.append("E" + str(counter))
    counter += 1

def dequeue():
    global queue
    if len(queue) > 0:
        queue.pop(0)

def clear_queue():
    global queue
    queue = []
