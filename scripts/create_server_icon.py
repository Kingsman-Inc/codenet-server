#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de ícone profissional para CodeNet Server Monitor
Cria ícone com tema de servidor/rede em múltiplas resoluções
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_server_monitor_icon():
    """Cria ícone profissional para Server Monitor"""
    try:
        # Tamanhos padrão para ICO
        sizes = [16, 24, 32, 48, 64, 96, 128, 256]
        images = []
        
        for size in sizes:
            # Criar imagem com fundo transparente
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Cores do tema Server Monitor
            bg_color = (10, 15, 28, 255)      # Azul escuro profundo
            accent_color = (0, 212, 255, 255)  # Azul ciano vibrante
            success_color = (0, 255, 136, 255) # Verde de sucesso
            panel_color = (26, 35, 50, 255)    # Azul-cinza
            
            # Desenhar fundo circular com gradiente
            margin = max(1, size // 16)
            circle_size = size - (margin * 2)
            
            # Fundo principal (círculo)
            draw.ellipse(
                [margin, margin, margin + circle_size, margin + circle_size],
                fill=bg_color,
                outline=accent_color,
                width=max(1, size // 32)
            )
            
            # Desenhar elementos do servidor baseado no tamanho
            if size >= 32:
                # Servidor principal (retângulo central)
                server_width = size // 3
                server_height = size // 2
                server_x = (size - server_width) // 2
                server_y = (size - server_height) // 2
                
                # Corpo do servidor
                draw.rectangle(
                    [server_x, server_y, server_x + server_width, server_y + server_height],
                    fill=panel_color,
                    outline=accent_color,
                    width=max(1, size // 64)
                )
                
                # LEDs de status (pequenos círculos)
                led_size = max(2, size // 32)
                led_spacing = led_size + 2
                
                # LED verde (online)
                led_x = server_x + led_spacing
                led_y = server_y + led_spacing
                draw.ellipse(
                    [led_x, led_y, led_x + led_size, led_y + led_size],
                    fill=success_color
                )
                
                # LED azul (conectado)
                led_x += led_spacing
                draw.ellipse(
                    [led_x, led_y, led_x + led_size, led_y + led_size],
                    fill=accent_color
                )
                
                if size >= 48:
                    # Linhas de dados (representando atividade)
                    line_y = server_y + server_height // 2
                    line_width = max(1, size // 64)
                    
                    for i in range(3):
                        y_pos = line_y + (i * (led_size + 1))
                        if y_pos < server_y + server_height - led_size:
                            draw.rectangle(
                                [server_x + led_spacing, y_pos, 
                                 server_x + server_width - led_spacing, y_pos + line_width],
                                fill=accent_color
                            )
                
                if size >= 64:
                    # Antena/sinal (linhas radiantes)
                    center_x = size // 2
                    antenna_y = server_y - (size // 8)
                    
                    # Linhas de sinal
                    for i in range(3):
                        radius = (i + 1) * (size // 16)
                        arc_width = max(1, size // 64)
                        
                        # Arco superior (sinal)
                        draw.arc(
                            [center_x - radius, antenna_y - radius,
                             center_x + radius, antenna_y + radius],
                            start=220, end=320,
                            fill=success_color,
                            width=arc_width
                        )
            
            elif size >= 16:
                # Versão simplificada para tamanhos pequenos
                # Servidor como retângulo simples
                rect_size = size // 2
                rect_x = (size - rect_size) // 2
                rect_y = (size - rect_size) // 2
                
                draw.rectangle(
                    [rect_x, rect_y, rect_x + rect_size, rect_y + rect_size],
                    fill=panel_color,
                    outline=accent_color,
                    width=1
                )
                
                # LED central
                led_size = max(2, size // 8)
                led_x = (size - led_size) // 2
                led_y = (size - led_size) // 2
                
                draw.ellipse(
                    [led_x, led_y, led_x + led_size, led_y + led_size],
                    fill=success_color
                )
            
            images.append(img)
        
        # Salvar como ICO
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "server_monitor.ico")
        
        # Converter para ICO
        images[0].save(
            icon_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        
        print(f"✅ Ícone Server Monitor criado: {icon_path}")
        
        # Também criar versão PNG para preview
        png_path = os.path.join(current_dir, "server_monitor_preview.png")
        images[-1].save(png_path, format='PNG')
        print(f"📸 Preview PNG salvo: {png_path}")
        
        return icon_path
        
    except Exception as e:
        print(f"❌ Erro ao criar ícone Server Monitor: {e}")
        return None

def create_alternative_server_icon():
    """Cria ícone alternativo com design mais moderno"""
    try:
        sizes = [16, 24, 32, 48, 64, 96, 128, 256]
        images = []
        
        for size in sizes:
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Cores modernas
            primary_color = (0, 212, 255, 255)    # Azul ciano
            secondary_color = (10, 15, 28, 255)   # Azul escuro
            accent_color = (0, 255, 136, 255)     # Verde
            
            # Fundo hexagonal moderno
            margin = max(2, size // 12)
            hex_size = size - (margin * 2)
            center = size // 2
            
            # Calcular pontos do hexágono
            import math
            hex_points = []
            for i in range(6):
                angle = i * math.pi / 3
                x = center + (hex_size // 2) * math.cos(angle)
                y = center + (hex_size // 2) * math.sin(angle)
                hex_points.extend([x, y])
            
            # Desenhar hexágono
            if size >= 24:
                draw.polygon(hex_points, fill=secondary_color, outline=primary_color, width=max(1, size // 32))
            else:
                # Círculo para tamanhos pequenos
                draw.ellipse([margin, margin, size-margin, size-margin], 
                           fill=secondary_color, outline=primary_color, width=1)
            
            # Ícone de rede/servidor no centro
            if size >= 32:
                # Grade de conexão (3x3)
                dot_size = max(2, size // 16)
                spacing = size // 6
                start_x = center - spacing
                start_y = center - spacing
                
                # Desenhar pontos de conexão
                for row in range(3):
                    for col in range(3):
                        x = start_x + (col * spacing)
                        y = start_y + (row * spacing)
                        
                        # Ponto central maior e diferente
                        if row == 1 and col == 1:
                            draw.ellipse([x-dot_size, y-dot_size, x+dot_size, y+dot_size], 
                                       fill=accent_color)
                        else:
                            draw.ellipse([x-dot_size//2, y-dot_size//2, x+dot_size//2, y+dot_size//2], 
                                       fill=primary_color)
                
                # Linhas de conexão
                line_width = max(1, size // 64)
                # Horizontais
                for row in range(3):
                    y = start_y + (row * spacing)
                    draw.rectangle([start_x-dot_size//2, y-line_width//2, 
                                  start_x + 2*spacing+dot_size//2, y+line_width//2], 
                                 fill=primary_color)
                
                # Verticais
                for col in range(3):
                    x = start_x + (col * spacing)
                    draw.rectangle([x-line_width//2, start_y-dot_size//2, 
                                  x+line_width//2, start_y + 2*spacing+dot_size//2], 
                                 fill=primary_color)
            
            elif size >= 16:
                # Versão simplificada - apenas pontos principais
                dot_size = max(1, size // 8)
                
                # Centro
                draw.ellipse([center-dot_size, center-dot_size, center+dot_size, center+dot_size], 
                           fill=accent_color)
                
                # 4 pontos cardeais
                offset = size // 4
                for dx, dy in [(0, -offset), (offset, 0), (0, offset), (-offset, 0)]:
                    x, y = center + dx, center + dy
                    draw.ellipse([x-dot_size//2, y-dot_size//2, x+dot_size//2, y+dot_size//2], 
                               fill=primary_color)
            
            images.append(img)
        
        # Salvar ícone alternativo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "CodeNet_server.ico")
        
        images[0].save(
            icon_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        
        print(f"✅ Ícone alternativo Server criado: {icon_path}")
        return icon_path
        
    except Exception as e:
        print(f"❌ Erro ao criar ícone alternativo: {e}")
        return None

if __name__ == "__main__":
    print("🎨 Gerando ícones para CodeNet Server Monitor...")
    
    # Criar ícone principal
    main_icon = create_server_monitor_icon()
    
    # Criar ícone alternativo
    alt_icon = create_alternative_server_icon()
    
    print("\n🎉 Ícones gerados com sucesso!")
    print(f"📁 Localização: {os.path.dirname(os.path.abspath(__file__))}")
    print("💡 Use 'server_monitor.ico' como ícone principal")
    print("💡 Use 'CodeNet_server.ico' como alternativa")
