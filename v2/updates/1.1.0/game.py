"""ACE Adventures 2: independent game state and deterministic character roulette."""
import json,random
from pathlib import Path

PATHS={"Rogue":[("Thief",35),("Ranger",25),("Assassin",30),("Arcane Trickster",10)],"Mage":[("Elementalist",45),("Spellweaver",30),("Runesage",18),("Archon Apprentice",7)],"Fighter":[("Martial Artist",25),("Knight",25),("Swordsman",24),("Barbarian",18),("Paladin",8)],"Vessel":[("Monk",28),("Druid",25),("Spirit Fighter",23),("Warden",18),("Oracle Vessel",6)]}
ELEMENTS={"basic":["Earth","Water","Fire","Air"],"special":["Lightning","Gravity","Blood","Illusion","Light","Dark","Support"],"legendary":["Time","Creation","Chaos"]}
SPELLS={"Earth":["Ground Tremble","Pebble Shot","Mud Slap"],"Water":["Water Shot","Ice Shard","Splash"],"Air":["Wind Gust","Air Cutter","Air Twist"],"Fire":["Flame Flick","Firewall","Heat Wave"],"Lightning":["Electric Whip","Lightning Dash","Static Shock"],"Gravity":["Downfall","Micro-Psychokinesis","Gravitational Push"],"Blood":["Blood Drain","Hemorrhage","Sanguine Strike"],"Illusion":["Mirage","Phantom Strike","Shape Shift"],"Light":["Blinding Light","Heavenly Bullet","Divine Shield"],"Dark":["Shadow Step","Nightmare","Dark Pulse"],"Support":["Healing Wave","Protective Aura","Mana Boost"],"Time":["Slow Mo Bubble","Temporal Shift","Chrono Dash"],"Creation":["Construct","Materialize","Form"],"Chaos":["Mind Jumble","Randomize","Unpredictable Strike"]}
MOVES={"Thief":["Quick Hands","Pocket Sand","Nimble Escape"],"Ranger":["Quick Shot","Mark Target","Woodland Step"],"Assassin":["Backstab","Silent Step","Weakpoint"],"Arcane Trickster":["Minor Mirage","Phantom Hand","Illusory Feint"],"Martial Artist":["Palm Strike","Counter Stance","Sweeping Kick"],"Knight":["Shield Bash","Guard","Defensive Advance"],"Swordsman":["Precision Cut","Blade Parry","Riposte"],"Barbarian":["Wild Swing","War Cry","Brutal Charge"],"Paladin":["Sacred Strike","Minor Blessing","Guardian Stance"],"Monk":["Palm Strike","Breath Focus","Spirit Guard"],"Druid":["Vine Snare","Seed Spark","Nature's Touch"],"Spirit Fighter":["Soul Jab","Spirit Ward","Echo Step"],"Warden":["Guardian Step","Root Guard","Staff Sweep"],"Oracle Vessel":["Omen Glimpse","Fate Nudge","Whisper Ward"]}
RACES=["Human","Elf","Dwarf","Halfling","Orc","Tiefling","Gnome"]
def create_character(name,age,cls):
    if cls not in PATHS or not 1<=len(name.strip())<=32 or not 10<=int(age)<=120:raise ValueError("Invalid character details")
    path=random.choices([x for x,_ in PATHS[cls]],weights=[w for _,w in PATHS[cls]])[0]
    magic="None"
    if cls=="Mage" or path=="Arcane Trickster":
        tier=random.choices(["basic","special","legendary"],weights=[35,50,15])[0]
        magic=random.choice(ELEMENTS[tier])
    else:magic={"Druid":"Nature","Warden":"Nature","Monk":"Ki","Spirit Fighter":"Spirit","Oracle Vessel":"Omen","Paladin":"Light"}.get(path,"None")
    stats={k:max(6,min(20,random.randint(8,15)+v)) for k,v in zip(["STR","DEX","CON","INT","WIS","CHA"],{"Rogue":[0,3,1,1,1,0],"Mage":[-1,1,0,3,2,1],"Fighter":[3,1,2,0,0,0],"Vessel":[1,2,2,1,2,0]}[cls])}
    hp=max(8,{"Rogue":18,"Mage":13,"Fighter":25,"Vessel":21}[cls]+(stats["CON"]-10)//2+random.randint(-3,3))
    mana=max(0,{"Rogue":6,"Mage":24,"Fighter":3,"Vessel":15}[cls]+random.randint(-2,4))
    return {"name":name.strip(),"age":int(age),"class":cls,"path":path,"magic":magic,"race":random.choice(RACES),"level":1,"xp":0,"stats":stats,"hp":hp,"max_hp":hp,"mana":mana,"max_mana":mana,"skills":random.sample(["Perception","Stealth","Athletics","Acrobatics","Arcana","Persuasion","Insight","Survival","Investigation","Nature"],4),"moves":SPELLS[magic] if cls=="Mage" else MOVES[path],"passives":[path+" Training"],"inventory":[{"Rogue":"Worn Daggers","Mage":"Ashwood Staff","Fighter":"Iron Sword","Vessel":"Pilgrim Staff"}[cls],"Travel Rations"],"gold":random.randint(7,35),"sprite_seed":random.randrange(2**31)}
def new_campaign(title,players):
    if not 1<=len(title.strip())<=60 or not 1<=players<=8:raise ValueError("Invalid campaign details")
    return {"title":title.strip(),"players":players,"character":None,"history":[],"location":"Ironwood Crossing","created":__import__("datetime").datetime.now().isoformat()}
def campaign_path(root,id):
    if not id.isalnum():raise ValueError("Invalid campaign ID")
    return root/"campaigns"/(id+".json")
def save_campaign(root,id,data):
    p=campaign_path(root,id);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(".tmp");tmp.write_text(json.dumps(data,indent=2));tmp.replace(p)
def list_campaigns(root):
    result=[]
    for p in sorted((root/"campaigns").glob("*.json")) if (root/"campaigns").exists() else []:
        try:
            d=json.loads(p.read_text());result.append((p.stem,d))
        except (ValueError,OSError):pass
    return result
def roll_d20(modifier=0,dc=13):
    n=random.randint(1,20);total=n+modifier
    degree="Critical Success" if n==20 else "Critical Failure" if n==1 else "Exceptional Success" if total>=dc+5 else "Success" if total>=dc else "Partial Success" if total>=dc-3 else "Failure"
    return {"roll":n,"modifier":modifier,"total":total,"dc":dc,"degree":degree}

# v1.1 encounter engine: deterministic rules, persistent opponent and transparent D20.
def begin_encounter(campaign):
    if campaign.get("enemy") and campaign["enemy"].get("hp",0)>0:
        return "An opponent is already in combat."
    enemy=random.choice(["Moss Goblin","Thorn Wolf","Forest Wisp"])
    campaign["enemy"]={"name":enemy,"hp":16,"max_hp":16,"ac":12,"cover":False}
    return "A "+enemy+" emerges near the Ironwood path!"

def attempt_action(campaign,text):
    hero=campaign.get("character")
    if not hero:raise ValueError("Create a character first.")
    if hero["hp"]<=0:raise ValueError("You are incapacitated.")
    text=text.strip()
    if not text:raise ValueError("Describe your action.")
    t=text.lower()
    active=campaign.get("enemy")
    known=next((m for m in hero["moves"] if m.lower() in t),None)
    magic_words=("fireball","flame flick","cast ","spell ","lightning","teleport","time stop")
    if any(word in t for word in magic_words) and not known:
        if hero["magic"]=="None":
            raise ValueError("Your character does not have that magic. Try an ability you possess.")
        if "teleport" in t or "time stop" in t:
            raise ValueError("That is beyond your current Level 1 abilities.")
    if known and hero["mana"]<3:raise ValueError("Not enough mana for your technique (3 needed).")
    combat=bool(active) and any(x in t for x in ("attack","strike","stab","shoot","hit ","slash","blast","kick","punch"))
    if active and known:combat=True
    stat="INT" if hero["class"]=="Mage" and known else "CHA" if any(x in t for x in ("persuad","convinc","bargain","negotia")) else "DEX" if any(x in t for x in ("sneak","hide","escape","dodge","slip")) else "STR" if combat or any(x in t for x in ("push","climb","jump")) else "WIS"
    bonus=(hero["stats"][stat]-10)//2
    dc=active["ac"] if combat else 13
    die=roll_d20(bonus,dc)
    degree=die["degree"]
    if known:hero["mana"]-=3
    notes=[]
    if combat and active:
        if degree in ("Success","Exceptional Success","Critical Success"):
            damage=random.randint(1,6)+max(0,bonus)
            if degree=="Critical Success":damage*=2
            active["hp"]=max(0,active["hp"]-damage)
            notes.append("You deal %d damage to %s."%(damage,active["name"]))
        if active["hp"]==0:
            notes.append("%s defeated. +10 XP and +8 gold."%active["name"])
            hero["xp"]=hero.get("xp",0)+10
            hero["gold"]+=8
            campaign["enemy"]=None
        else:
            retaliation=random.randint(1,4)
            hero["hp"]=max(0,hero["hp"]-retaliation)
            notes.append("%s retaliates for %d HP."%(active["name"],retaliation))
    elif any(x in t for x in ("smoke","cover","escape")):
        if degree in ("Success","Exceptional Success","Critical Success") and ("dry" in t or "leaves" in t):
            campaign["cover"]=True
            notes.append("Smoke and cover now obscure the path.")
        else:notes.append("No reliable cover is created.")
    else:
        notes.append("The attempt "+("succeeds." if degree in ("Success","Exceptional Success","Critical Success") else "partly works, with a complication." if degree=="Partial Success" else "does not succeed."))
    event=text+"\nD20 %s %+d vs DC %s: %s. "%(die["roll"],bonus,dc,degree)+" ".join(notes)
    campaign.setdefault("history",[]).append(event)
    return die,event
