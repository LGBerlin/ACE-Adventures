"""Retro pixel art assets rendered deterministically with Tkinter Canvas.
Every visual is a function of the saved seed and character data.
No external model, image file, or download is needed for the initial visuals.
"""
import random
COLORS={"Rogue":"#53775d","Mage":"#7966b3","Fighter":"#718ca3","Vessel":"#a58c68"}

def pixel(canvas,x,y,size,color):
    canvas.create_rectangle(x,y,x+size,y+size,fill=color,outline=color)

def character(canvas,hero,x=100,y=34,scale=5):
    rng=random.Random(hero.get("sprite_seed",1))
    cl=hero["class"];race=hero["race"]
    skin={"Human":"#dcb28a","Elf":"#f0c39c","Dwarf":"#c99172","Halfling":"#d6a07c","Orc":"#91ac76","Tiefling":"#bd8399","Gnome":"#e7bd8a"}.get(race,"#d7ab88")
    coat=COLORS.get(cl,"#667c64");hair=rng.choice(["#3b292b","#a47144","#d0ba80","#647280"])
    # Draw exact reusable block map for an 18x30 character.
    blocks=[]
    def block(px,py,w,h,col):
        blocks.append((px,py,w,h,col))
    block(3,27,15,2,"#52483b")
    block(7,22,3,5,"#3b3537");block(12,22,3,5,"#3b3537")
    block(5,12,12,12,"#303139");block(6,13,10,10,coat)
    block(3,13,3,10,coat);block(16,13,3,10,coat)
    block(4,22,2,2,skin);block(17,22,2,2,skin)
    block(7,6,9,9,skin);block(6,5,11,3,hair);block(6,7,2,6,hair)
    block(9,11,1,1,"#20232a");block(14,11,1,1,"#20232a")
    if race=="Tiefling":block(8,2,2,4,"#453144");block(14,2,2,4,"#453144")
    if race=="Elf":block(4,9,3,2,skin);block(16,9,3,2,skin)
    if cl=="Mage":block(1,9,2,18,"#a28b68");block(0,6,4,5,"#82b6d9")
    if cl=="Fighter":block(20,12,2,15,"#c4d1d3");block(18,19,6,2,"#baa071")
    if cl=="Rogue":block(20,19,1,8,"#c0c4cc")
    if cl=="Vessel":block(1,11,2,17,"#b8a685");block(0,8,4,4,"#7ac499")
    for bx,by,w,h,color in blocks:
        canvas.create_rectangle(x+bx*scale,y+by*scale,x+(bx+w)*scale,y+(by+h)*scale,fill=color,outline=color)

def forest(canvas,width=740,height=260,seed=231):
    rng=random.Random(seed)
    canvas.delete("all")
    canvas.configure(bg="#172b30")
    # Layered pixel environment.
    for band,color in [(0,"#203c3e"),(60,"#28473e"),(117,"#355848"),(185,"#5b644a"),(227,"#807252")]:
        canvas.create_rectangle(0,band,width,height,fill=color,outline=color)
    for n in range(110):
        x=rng.randrange(width);y=rng.randrange(20,214)
        depth=1 if y<95 else 2 if y<160 else 3
        trunk="#253b34" if depth==1 else "#283d33"
        foliage=rng.choice(["#315346","#385f49","#456b4c"])
        canvas.create_rectangle(x,y,x+depth*4,y+65,fill=trunk,outline=trunk)
        radius=depth*10
        for layer in range(3):
            canvas.create_rectangle(x-radius+layer*4,y-radius-layer*5,x+radius-layer*4,y+radius//2,fill=foliage,outline=foliage)
    # Ruined gateway silhouettes.
    canvas.create_rectangle(width//2-60,90,width//2-35,210,fill="#849289",outline="#495b55",width=3)
    canvas.create_rectangle(width//2+35,90,width//2+60,210,fill="#849289",outline="#495b55",width=3)
    canvas.create_rectangle(width//2-60,79,width//2+60,105,fill="#91a39a",outline="#495b55",width=3)
    canvas.create_rectangle(width//2-35,105,width//2+35,210,fill="#1a302e",outline="#1a302e")
    for i in range(30):
        x=rng.randrange(width);y=rng.randrange(180,height)
        canvas.create_rectangle(x,y,x+4,y+4,fill=rng.choice(["#bdac73","#749a64","#e1cb8b"]),outline="")

def d20(canvas,value="20"):
    canvas.delete("all")
    cx,cy=125,110
    points=[cx,12,cx+100,83,cx+64,193,cx-64,193,cx-100,83]
    canvas.create_polygon(points,fill="#6486ad",outline="#c2d4ec",width=5)
    canvas.create_line(cx,12,cx,62,cx-100,83,cx,142,cx+100,83,cx,62,fill="#d2e2ed",width=3)
    canvas.create_line(cx-64,193,cx,142,cx+64,193,fill="#d2e2ed",width=3)
    canvas.create_text(cx,110,text=str(value),fill="#fff3d9",font=("Menlo",46,"bold"))
