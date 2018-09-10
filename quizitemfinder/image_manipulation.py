from PIL import Image, ImageOps

def paste_cover(img, rect0, cover_color=(255, 255, 255, 255)):
    img_width  = rect0[1][0] - rect0[0][0]
    img_height = rect0[1][1] - rect0[0][1]
    img_x = rect0[0][0]
    img_y = rect0[0][1]
    border_size=3

    cover = Image.new('RGBA', (img_width, img_height), cover_color)
    cover_with_border = ImageOps.expand(cover,border=border_size,fill='blue')
    #img.paste(cover, (img_x, img_y))
    
    img.putalpha(255)
    cover_with_border.putalpha(cover_color[3])
    img.alpha_composite(cover_with_border, (img_x-border_size, img_y-border_size))

    #cover.putalpha(cover_color[3])
    #img.alpha_composite(cover, (img_x, img_y))
    #print(img_header_rects)

    #return img    


def paste_rects_on_sheet(sheet_img, rects):
    img = sheet_img.copy()
    for rect in rects['headers']:
        paste_cover(img, rect, (200, 255, 255, 100))
    for rect in rects['items']:
        paste_cover(img, rect, (255, 200, 255, 100))
    return img.convert('RGB')

