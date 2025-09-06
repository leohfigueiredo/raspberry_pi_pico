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

# LED onboard e Botão (mude o pino se necessário)
led = Pin("LED", Pin.OUT)
button = Pin(0, Pin.IN, Pin.PULL_DOWN) # Botão capacitivo conectado ao GP0

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
        self.write_cmd(0x36)  # MADCTL (Controle de Acesso à Memória)
        self.write_data(bytearray([0xA0]))  # Rotação para paisagem
        self.write_cmd(0x3A)  # COLMOD
        self.write_data(bytearray([0x05]))  # Cor de 16-bit
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

# === FONTE SIMPLES 5x8 (A-Z, espaço) ===
font = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    'A': [0x7C, 0x12, 0x11, 0x12, 0x7C],
    'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
    'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
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
    """Desenha texto em escala usando fill_rect para cada pixel."""
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
        x_start += 5 * scale + scale  # 5 pixels de largura + 1 pixel de espaçamento

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

    # Mensagem inicial centralizada
    display.fill_color(BLACK)
    initial_msg = "PRESSIONE"
    scale = 2
    msg_width = len(initial_msg) * (5 * scale + scale) - scale
    x_start = (display.width - msg_width) // 2
    y_start = (display.height - 8 * scale) // 2
    draw_text_scaled(display, initial_msg, x_start, y_start, scale, WHITE)

    while True:
        try:
            current_button_state = button.value()
            # Verifica se o botão foi tocado (transição de 0 para 1)
            if current_button_state == 1 and last_button_state == 0:
                time.sleep_ms(50) # Debounce (evita múltiplos toques)
                if button.value() == 1: # Confirma o toque
                    led_on = not led_on
                    led.value(led_on)
                    
                    message = "LED ON" if led_on else "LED OFF"
                    bg_color = background_colors[color_index]
                    
                    # Limpa a tela com a nova cor de fundo
                    display.fill_color(bg_color)
                    
                    # Desenha a mensagem, centralizada e estática
                    scale = 3 # Escala ajustada para caber "LED OFF"
                    text_width = len(message) * (5 * scale + scale) - scale
                    x_pos = (display.width - text_width) // 2
                    y_pos = (display.height - 8 * scale) // 2 # 8 é a altura da fonte
                    draw_text_scaled(display, message, x_pos, y_pos, scale, WHITE)
                    
                    color_index = (color_index + 1) % len(background_colors)

            last_button_state = current_button_state
            time.sleep_ms(10) # Pequeno delay para não sobrecarregar a CPU

        except KeyboardInterrupt:
            break

    # Limpa tudo ao sair
    led.off()
    display.fill_color(BLACK)
    print("Finalizado.")