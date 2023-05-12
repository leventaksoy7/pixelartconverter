from flask import Flask, render_template, request
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'image' in request.files:
        resim = request.files['image']
        cevrilecek_resim = Image.open(resim)

        print("resim")
        print(resim)

        output_size = int(request.form['output_size'])
        width, height = cevrilecek_resim.size

        palet_boyutu = int(request.form['palet'])

        # Seçilen boyutun katı olup olmadığını kontrol etme
        if width % output_size != 0 or height % output_size != 0:

            # Çerçeve boyutunu hesaplama
            new_width = (width // output_size + 1) * output_size
            new_height = (height // output_size + 1) * output_size

            # Büyük kenarı bulma
            max_dim = max(new_width, new_height)
            
            # Çerçeve için gerekli olan mesafe
            padding_x = (max_dim - width) // 2
            padding_y = (max_dim - height) // 2

            # Yeni bir resim oluşturma ve beyaz çerçeve ekleme
            yeni_resim = Image.new('RGB', (max_dim, max_dim), 'white')
            yeni_resim.paste(cevrilecek_resim, (padding_x, padding_y))

            cevrilecek_resim = yeni_resim

        # Seçilen boyuta göre bölge sayısını hesaplama
        region_count_x = max_dim // output_size
        region_count_y = max_dim // output_size

        # Ortalama renklerin tutulacağı liste
        colors_r = []
        colors_g = []
        colors_b = []

        #------------------------------------------------------------------------------------------
        # Pixel art dönüşümü işlemi - 1
        for y in range(output_size):
            for x in range(output_size):
                # Bölgedeki piksellerin ortalama rengini - l
                r_total, g_total, b_total = 0, 0, 0
                pixel_count = 0

                for j in range(y * region_count_y, (y + 1) * region_count_y):
                    for i in range(x * region_count_x, (x + 1) * region_count_x):
                        if i < max_dim and j < max_dim:
                            r, g, b = cevrilecek_resim.getpixel((i, j))
                            r_total += r
                            g_total += g
                            b_total += b
                            pixel_count += 1

                # Bölgenin ortalama rengini hesapla
                if pixel_count > 0:
                    r_avg = r_total // pixel_count
                    g_avg = g_total // pixel_count
                    b_avg = b_total // pixel_count

                    colors_r.append(r_avg)
                    colors_g.append(g_avg)
                    colors_b.append(b_avg)

                    # Bölgeyi ortalama renge boyama
                    for j in range(y * region_count_y, (y + 1) * region_count_y):
                        for i in range(x * region_count_x, (x + 1) * region_count_x):
                            if i < max_dim and j < max_dim:
                                cevrilecek_resim.putpixel((i, j), (r_avg, g_avg, b_avg))
        #------------------------------------------------------------------------------------------

        colors_r.sort()
        colors_g.sort()
        colors_b.sort()

        # colors_r, colors_g, colors_b listelerindeki eleman sayısını palet_boyutu kadar indirgeme
        if len(colors_r) > palet_boyutu:
            step = len(colors_r) // palet_boyutu
            colors_r = [sum(colors_r[i:i+step]) // step for i in range(0, len(colors_r), step)]
            colors_g = [sum(colors_g[i:i+step]) // step for i in range(0, len(colors_g), step)]
            colors_b = [sum(colors_b[i:i+step]) // step for i in range(0, len(colors_b), step)]

        # Yeni renk paletini oluşturma
        renk_paleti = list(zip(colors_r, colors_g, colors_b))

        #------------------------------------------------------------------------------------------
        # Pixel art dönüşümü işlemi - 2
        for y in range(output_size):
            for x in range(output_size):
                # Bölgedeki piksellerin ortalama rengini al
                r_total, g_total, b_total = 0, 0, 0
                pixel_count = 0

                for j in range(y * region_count_y, (y + 1) * region_count_y):
                    for i in range(x * region_count_x, (x + 1) * region_count_x):
                        if i < width and j < height:
                            r, g, b = cevrilecek_resim.getpixel((i, j))
                            r_total += r
                            g_total += g
                            b_total += b
                            pixel_count += 1

                # Bölgenin ortalama rengini hesapla
                if pixel_count > 0:
                    r_avg = r_total // pixel_count
                    g_avg = g_total // pixel_count
                    b_avg = b_total // pixel_count

                    # En yakın renk paletindeki rengi bulma
                    min_distance = float('inf')
                    closest_color = None
                    for color in renk_paleti:
                        distance = (color[0] - r_avg) ** 2 + (color[1] - g_avg) ** 2 + (color[2] - b_avg) ** 2
                        if distance < min_distance:
                            min_distance = distance
                            closest_color = color

                    # Bölgeyi en yakın renk ile boyama
                    for j in range(y * region_count_y, (y + 1) * region_count_y):
                        for i in range(x * region_count_x, (x + 1) * region_count_x):
                            if i < width and j < height:
                                cevrilecek_resim.putpixel((i, j), closest_color)
        #------------------------------------------------------------------------------------------
        image_name = request.form['image_name']
        if image_name:
            cevrilecek_resim.save(f'{image_name}.png')
        else:
            cevrilecek_resim.save('donusturulmus_resim2.png')
        
        return "Resim başarıyla dönüştürüldü!"

    return "Resim seçilmedi!"

if __name__ == '__main__':
    app.run()
