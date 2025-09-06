from machine import Pin, SPI
import time

# === CONSTANTES E CORES ===
WHITE = bytearray([0xFF, 0xFF])
BLACK = bytearray([0x00, 0x00])
RED   = bytearray([0xF8, 0x00])
GREEN = bytearray([0x07, 0xE0])
BLUE  = bytearray([0x00, 0x1F])
MAGENTA = bytearray([0xF8, 0x1F])

# === CONFIGURAÇÃO DE PINOS (DISPLAY, LED, BOTÃO) ===
# Pinos do Display SPI
spi = SPI(0, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
dc  = Pin(21, Pin.OUT)
cs  = Pin(17, Pin.OUT)
rst = Pin(20, Pin.OUT)
bl  = Pin(22, Pin.OUT)

# LED onboard e Botão (mude o pino do botão se necessário)
led = Pin("LED", Pin.OUT)
button = Pin(15, Pin.IN, Pin.PULL_UP) # Botão conectado entre GP15 e GND

# === CLASSE ST7789 ===
class ST7789:
    def __init__(self, spi, width, height, dc, cs, rst, bl=None):
        self.spi = spi
        self.width = width
        self.height = height
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.bl = bl
        self.init_display()

    def write_cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)

    def reset(self):
        self.rst.value(0)
        time.sleep_ms(100)
        self.rst.value(1)
        time.sleep_ms(100)

    def init_display(self):
        if self.bl:
            self.bl.value(1)
        self.reset()
        self.write_cmd(0x01)  # SWRESET
        time.sleep_ms(150)
        self.write_cmd(0x11)  # SLPOUT
        time.sleep_ms(500)
        self.write_cmd(0x36)  # MADCTL (Memory Data Access Control)
        self.write_data(bytearray([0xA0]))  # Rotação para paisagem (landscape)
        self.write_cmd(0x3A)  # COLMOD
        self.write_data(bytearray([0x05]))  # 16-bit color
        self.write_cmd(0x21)  # INVON
        self.write_cmd(0x29)  # DISPON
        time.sleep_ms(100)

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, x0, 0x00, x1]))
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, y0, 0x00, y1]))
        self.write_cmd(0x2C)

    def fill_color(self, color565):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.dc.value(1)
        self.cs.value(0)
        pixel = bytearray(color565)
        for _ in range(self.width * self.height):
            self.spi.write(pixel)
        self.cs.value(1)

    def fill_rect(self, x, y, w, h, color):
        self.set_window(x, y, x + w - 1, y + h - 1)
        self.dc.value(1)
        self.cs.value(0)
        pixel = bytearray(color)
        for _ in range(w * h):
            self.spi.write(pixel)
        self.cs.value(1)

    def draw_pixel(self, x, y, color):
        self.set_window(x, y, x, y)
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(bytearray(color))
        self.cs.value(1)

# === FONTE 5x8 SIMPLES (A-Z, espaço) ===
font = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    'A': [0x7C, 0x12, 0x11, 0x12, 0x7C],
    'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
    'E': [0x7F, 0x49, 0x49, 0x41, 0x41],
    'F': [0x7F, 0x09, 0x09, 0x01, 0x01],
    'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
    'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
    'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
    'N': [0x7F, 0x04, 0x08, 0x10, 0x7F],
    'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
    'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
    'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
    'S': [0x26, 0x49, 0x49, 0x49, 0x32],
}

def draw_text_scaled(display, text, x_start, y_start, scale, color):
    """Desenha texto com uma escala, usando fill_rect para cada pixel."""
    for char in text:
        data = font.get(char.upper(), font[' '])
        for col_index, bits in enumerate(data):
            for row_index in range(8):
                if bits & (1 << row_index):
                    px = x_start + col_index * scale
                    py = y_start + row_index * scale
                    # Desenha um retângulo para o pixel em escala
                    display.fill_rect(px, py, scale, scale, color)
        # Move para a posição do próximo caractere
        x_start += 5 * scale + scale  # 5 pixels de largura + 1 de espaçamento

def scroll_large_text(display, text, y, scale, text_color, bg_color, delay=30):
    """Faz o texto grande rolar na tela."""
    text_width_pixels = len(text) * (5 * scale + scale)
    # Começa com o texto fora da tela à direita e move para a esquerda
    for offset in range(display.width, -text_width_pixels, -2): # Passo de -2 para acelerar
        display.fill_color(bg_color)  # Limpa a tela com a cor de fundo
        draw_text_scaled(display, text, offset, y, scale, text_color)
        time.sleep_ms(delay)

# === EXECUÇÃO ===
if __name__ == '__main__':
    # Inicializa o display com largura e altura para paisagem
    display = ST7789(spi, 160, 128, dc, cs, rst, bl)

    # Estado inicial
    led_on = False
    led.off()
    last_button_state = button.value()
    
    # Lista de cores de fundo para ciclar
    background_colors = [BLUE, RED, GREEN, MAGENTA]
    color_index = 0

    # Mensagem inicial
    display.fill_color(BLACK)
    draw_text_scaled(display, "PRESSIONE", 25, 50, 2, WHITE)

    while True:
        try:
            current_button_state = button.value()
            # Verifica se o botão foi pressionado (transição de 1 para 0)
            if current_button_state == 0 and last_button_state == 1:
                time.sleep_ms(50) # Debounce (evita múltiplos cliques)
                if button.value() == 0: # Confirma o pressionamento
                    led_on = not led_on
                    led.value(led_on)
                    
                    message = "LED ON" if led_on else "LED OFF"
                    bg_color = background_colors[color_index]
                    
                    scroll_large_text(display, message, 40, 4, WHITE, bg_color)
                    
                    color_index = (color_index + 1) % len(background_colors)

            last_button_state = current_button_state
            time.sleep_ms(10) # Pequeno delay para não sobrecarregar a CPU

        except KeyboardInterrupt:
            break

    # Limpa tudo ao sair
    led.off()
    display.fill_color(BLACK)
    print("Finalizado.")