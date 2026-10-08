import json,random,os,sys,re,hashlib,threading,urllib.request,webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
VERSION="0.2.0"
BASE="https://raw.githubusercontent.com/LGBerlin/ACE-Adventures/main"
DATA=Path.home()/"Library"/"Application Support"/"ACE Adventures"
DATA.mkdir(parents=True,exist_ok=True)
SAVE=DATA/"save.json"
PATHS={"Rogue":[("Thief",35),("Ranger",25),("Assassin",30),("Arcane Trickster",10)],"Mage":[("Elementalist",45),("Spellweaver",30),("Runesage",18),("Archon Apprentice",7)],"Fighter":[("Martial Artist",25),("Knight",25),("Swordsman",24),("Barbarian",18),("Paladin",8)],"Vessel":[("Monk",28),("Druid",25),("Spirit Fighter",23),("Warden",18),("Oracle Vessel",6)]}
SPELLS={"Earth":"Ground Tremble,Pebble Shot,Mud Slap","Water":"Water Shot,Ice Shard,Splash","Air":"Wind Gust,Air Cutter,Air Twist","Fire":"Flame Flick,Firewall,Heat Wave","Lightning":"Electric Whip,Lightning Dash,Static Shock","Gravity":"Downfall,Micro-Psychokinesis,Gravitational Push","Blood":"Blood Drain,Hemorrhage,Sanguine Strike","Illusion":"Mirage,Phantom Strike,Shape Shift","Light":"Blinding Light,Heavenly Bullet,Divine Shield","Dark":"Shadow Step,Nightmare,Dark Pulse","Support":"Healing Wave,Protective Aura,Mana Boost","Time":"Slow Mo Bubble,Temporal Shift,Chrono Dash","Creation":"Construct,Materialize,Form","Chaos":"Mind Jumble,Randomize,Unpredictable Strike"}
MOVES={"Thief":"Quick Hands,Pocket Sand,Nimble Escape","Ranger":"Quick Shot,Mark Target,Woodland Step","Assassin":"Backstab,Silent Step,Weakpoint","Arcane Trickster":"Minor Mirage,Phantom Hand,Illusory Feint","Martial Artist":"Palm Strike,Counter Stance,Sweeping Kick","Knight":"Shield Bash,Guard,Defensive Advance","Swordsman":"Precision Cut,Blade Parry,Riposte","Barbarian":"Wild Swing,War Cry,Brutal Charge","Paladin":"Sacred Strike,Minor Blessing,Guardian Stance","Monk":"Palm Strike,Breath Focus,Spirit Guard","Druid":"Vine Snare,Seed Spark,Nature's Touch","Spirit Fighter":"Soul Jab,Spirit Ward,Echo Step","Warden":"Guardian Step,Root Guard,Staff Sweep","Oracle Vessel":"Omen Glimpse,Fate Nudge,Whisper Ward"}
SKILLS="Acrobatics,Animal Handling,Arcana,Athletics,Deception,History,Insight,Intimidation,Investigation,Medicine,Nature,Perception,Performance,Persuasion,Religion,Sleight of Hand,Stealth,Survival".split(",")
SHOP={"Health Potion":12,"Mana Potion":14,"Smoke Bomb":20,"Iron Dagger":25}
def initial():return {"character":None,"history":[],"enemy":None,"pending":None,"place":"Ironwood Crossing","seed":random.randrange(100000)}
def load():
 try:
  d=json.loads(SAVE.read_text())
  return d if "character" in d else initial()
 except (OSError,ValueError):return initial()
def save(s):
 tmp=SAVE.with_suffix(".tmp");tmp.write_text(json.dumps(s,indent=2));tmp.replace(SAVE)
def weighted(options):return random.choices([a for a,b in options],weights=[b for a,b in options])[0]
def character(cl,name,age):
 if cl not in PATHS:raise ValueError("Choose a valid class")
 if not 1<=len(name.strip())<=32:raise ValueError("Enter a name")
 if not 10<=int(age)<=120:raise ValueError("Age must be from 10 to 120")
 path=weighted(PATHS[cl])
 affinity=weighted([(x,35/4) for x in ["Earth","Water","Fire","Air"]]+[(x,50/7) for x in ["Lightning","Gravity","Blood","Illusion","Light","Dark","Support"]]+[(x,15/3) for x in ["Time","Creation","Chaos"]]) if cl=="Mage" or path=="Arcane Trickster" else {"Druid":"Nature","Spirit Fighter":"Spirit","Monk":"Ki","Warden":"Nature","Oracle Vessel":"Omen","Paladin":"Light"}.get(path,"None")
 stats={k:max(6,min(20,random.randint(8,15)+v)) for k,v in zip(["STR","DEX","CON","INT","WIS","CHA"],{"Rogue":[0,3,1,1,1,0],"Mage":[-1,1,0,3,2,1],"Fighter":[3,1,2,0,0,0],"Vessel":[1,2,2,1,2,0]}[cl])}
 hp=max(8,{"Rogue":18,"Mage":13,"Fighter":25,"Vessel":21}[cl]+(stats["CON"]-10)//2+random.randint(-3,3))
 mana=max(0,{"Rogue":6,"Mage":24,"Fighter":3,"Vessel":15}[cl]+random.randint(-2,4))
 moves=(SPELLS[affinity] if cl=="Mage" else MOVES[path]).split(",")
 weapon={"Rogue":"Worn Daggers","Mage":"Ashwood Staff","Fighter":"Iron Sword","Vessel":"Pilgrim Staff"}[cl]
 return {"name":name.strip(),"age":int(age),"class":cl,"path":path,"magic":affinity,"race":random.choice(["Human","Elf","Dwarf","Halfling","Orc","Tiefling","Gnome"]),"level":1,"xp":0,"abilities":stats,"hp":hp,"max_hp":hp,"mana":mana,"max_mana":mana,"ac":10+(stats["DEX"]-10)//2+(2 if cl=="Fighter" else 1),"hit_die":{"Rogue":"d8","Mage":"d6","Fighter":"d10","Vessel":"d8"}[cl],"skills":random.sample(SKILLS,5),"moves":moves,"passives":[affinity+" Affinity" if affinity!="None" else "Battle Instinct"],"items":[weapon,"Travel Rations"],"gold":random.randint(7,35),"background":random.choice(["Wanderer","Exile","Scholar","Scout","Monastery Novice"]),"sprite_seed":random.randrange(100000)}
def log(s,a,r):s["history"].append({"action":a,"result":r});s["history"]=s["history"][-60:]
def plan(s,a):
 c=s["character"];t=a.lower()
 if not a.strip():raise ValueError("Describe an action")
 if s["pending"]:raise ValueError("Roll the waiting D20 first")
 if c["hp"]<=0:raise ValueError("Your character is incapacitated")
 if "find enemy" in t or "encounter" in t:
  if not s["enemy"]:s["enemy"]={"name":random.choice(["Moss Goblin","Forest Wisp","Rootling"]),"hp":16,"max_hp":16,"ac":12}
  return {"immediate":"A "+s["enemy"]["name"]+" appears!"}
 if t.startswith("buy "):
  item=next((i for i in SHOP if i.lower() in t),None)
  if item is None:return {"immediate":"The merchant does not stock that item."}
  if c["gold"]<SHOP[item]:return {"immediate":"Not enough gold."}
  c["gold"]-=SHOP[item];c["items"].append(item);return {"immediate":"Bought "+item+" for "+str(SHOP[item])+" gold."}
 if "drink potion" in t or "use health potion" in t or "use mana potion" in t:
  item="Mana Potion" if "mana" in t else "Health Potion"
  if item not in c["items"]:return {"immediate":"No "+item+" available."}
  c["items"].remove(item);stat="mana" if item=="Mana Potion" else "hp";c[stat]=min(c["max_"+stat],c[stat]+10)
  return {"immediate":"Used "+item+"."}
 if "rest" in t and not s["enemy"]:
  for k in ("hp","mana"):c[k]=min(c["max_"+k],c[k]+5)
  return {"immediate":"You recover 5 HP and mana."}
 move=next((m for m in c["moves"] if m.lower() in t),None)
 magical=any(w in t for w in ["cast ","spell","fireball","magic","teleport","flame","illusion","freeze"])
 if magical and move is None:
  if c["magic"]=="None":return {"immediate":"You do not possess that magical ability."}
  if any(w in t for w in ["teleport","stop time","resurrect"]):return {"immediate":"That exceeds your current abilities."}
  move="Improvised "+c["magic"]+" magic"
 if move and c["mana"]<3:return {"immediate":"Not enough mana."}
 social=any(x in t for x in ["persuad","convinc","negotia","bargain","talk ","intimidat","lie to"])
 stealth=any(x in t for x in ["sneak","hide","escape","steal","pickpocket","slip past"])
 physical=any(x in t for x in ["jump","climb","push","leap","dodge"])
 attack=bool(s["enemy"]) and (bool(move) or any(x in t for x in ["attack","strike","stab","shoot","hit ","slash","punch","blast"]))
 attribute="INT" if move and c["class"]=="Mage" else "CHA" if social else "DEX" if stealth else "STR" if physical or (attack and c["class"]=="Fighter") else "DEX" if attack else "WIS"
 bonus=(c["abilities"][attribute]-10)//2+(2 if (social and "Persuasion" in c["skills"]) or (stealth and "Stealth" in c["skills"]) else 0)
 s["pending"]={"action":a[:700],"attribute":attribute,"bonus":bonus,"dc":s["enemy"]["ac"] if attack else 14 if social or stealth or move else 12,"attack":attack,"move":move}
 return {"pending":s["pending"]}
def narrate(s,p,rule):
 c=s["character"]
 system="You are a fantasy RPG narrator. Write 40-90 words in second person describing exactly the outcome given. Do not change HP, gold, equipment or dice results. Do not print reasoning. Respect the player's creative tactical intent."
 content=json.dumps({"character":c["class"]+" / "+c["path"],"magic":c["magic"],"moves":c["moves"],"location":s["place"],"recent":s["history"][-4:],"action":p["action"],"mechanical_outcome":rule})
 req=urllib.request.Request("http://127.0.0.1:11434/api/chat",json.dumps({"model":"qwen3.5:4b","stream":False,"think":False,"messages":[{"role":"system","content":system},{"role":"user","content":content}],"options":{"num_predict":180}}).encode(),{"Content-Type":"application/json"})
 try:
  with urllib.request.urlopen(req,timeout=90) as r: return json.load(r)["message"]["content"].strip() or rule
 except Exception:return "The world reacts to your attempt. "+rule
def roll(s):
 p=s["pending"]
 if not p:raise ValueError("No roll is pending")
 c=s["character"];die=random.randint(1,20);total=die+p["bonus"];dc=p["dc"]
 degree="Critical Success" if die==20 else "Critical Failure" if die==1 else "Exceptional Success" if total>=dc+5 else "Success" if total>=dc else "Partial Success" if total>=dc-3 else "Failure"
 rule=f"D20 {die} {p['bonus']:+d} = {total} vs DC {dc}: {degree}."
 if p["move"]:c["mana"]-=3
 if p["attack"] and s["enemy"]:
  if degree in ("Critical Success","Exceptional Success","Success"):
   damage=random.randint(1,6)+max(1,p["bonus"]);damage*=2 if degree=="Critical Success" else 1
   s["enemy"]["hp"]=max(0,s["enemy"]["hp"]-damage);rule+=f" Dealt {damage} damage."
  if s["enemy"]["hp"]<=0:
   s["enemy"]=None;c["gold"]+=9;c["xp"]+=10;rule+=" Enemy defeated; earned 9 gold and 10 XP."
  else:
   damage=random.randint(1,4);c["hp"]=max(0,c["hp"]-damage);rule+=f" Enemy counterattack dealt {damage} damage."
 story=narrate(s,p,rule);log(s,p["action"],rule+"\n"+story);s["pending"]=None;save(s)
 return {"die":die,"bonus":p["bonus"],"total":total,"dc":dc,"degree":degree,"rule":rule,"story":story}
def updater(install):
 with urllib.request.urlopen(BASE+"/latest.json",timeout=15) as r: m=json.load(r)
 if tuple(map(int,m["version"].split(".")))<=tuple(map(int,VERSION.split("."))):return {"message":"Already up to date (v"+VERSION+")."}
 files=m.get("files",[])
 if len(files)!=1 or files[0].get("path")!="adventures.py":raise ValueError("Invalid update manifest")
 f=files[0];url=f.get("url","")
 if not url.startswith(BASE+"/updates/") or urlsplit(url).hostname!="raw.githubusercontent.com" or not re.fullmatch("[0-9a-f]{64}",f.get("sha256","")):raise ValueError("Untrusted update")
 if not install:return {"message":"Version "+m["version"]+" available"}
 with urllib.request.urlopen(url,timeout=30) as r:raw=r.read(2000001)
 if len(raw)>2000000 or hashlib.sha256(raw).hexdigest()!=f["sha256"]:raise ValueError("Update SHA-256 failed")
 tmp=DATA/"adventures.new";tmp.write_bytes(raw);tmp.replace(DATA/"adventures.py")
 return {"message":"Updated to "+m["version"]+". Quit and reopen the app."}
HTML=r'''<!doctype html><html><head><meta charset="utf-8"><title>ACE Adventures</title><style>
*{box-sizing:border-box}body{margin:0;background:#24201d;color:#e9dec5;font:13px Monaco,monospace}header{background:#423b34;border-bottom:5px ridge #b39167;padding:10px 18px;display:flex;justify-content:space-between}button{background:#746650;border:3px ridge #bba17a;color:#ffefd0;font:inherit;padding:7px;margin:3px;cursor:pointer}button:hover{background:#9a825a}input,textarea{background:#292822;color:#f8eccf;border:3px inset #8c7e67;font:inherit;padding:8px;width:100%}.panel{border:5px ridge #a78c66;background:#4a433a;padding:10px;margin:9px}.panel h3{background:#797164;margin:-10px -10px 10px;padding:8px;border-bottom:2px solid #23201b;font-size:14px}#layout{display:grid;grid-template-columns:285px 1fr 245px;max-width:1300px;margin:auto;gap:5px}#start{max-width:540px;margin:50px auto}#start button{padding:20px}.row{display:flex;gap:5px;flex-wrap:wrap}.stat{background:#2e2b27;border:2px solid #81735d;padding:7px;flex:1}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:4px}.muted{color:#bbb2a2}#sprite{width:100%;height:225px;image-rendering:pixelated;background:#bcb2a2;border:4px ridge #998669}#log{height:270px;overflow:auto;background:#292722;border:3px inset #746b5d;padding:8px;white-space:pre-wrap}.entry{border-bottom:1px solid #655c4c;padding:9px 0}.entry b{color:#f0c786}#map{display:grid;grid-template-columns:repeat(13,1fr);max-width:600px;margin:10px auto;border:4px ridge #997d52}.tile{aspect-ratio:1;display:grid;place-items:center;background:#52704a;font-size:20px}.tile:nth-child(2n){background:#5b7650}#modal{position:fixed;inset:0;background:#0a0808d9;display:none;align-items:center;justify-content:center}#dicebox{text-align:center;background:#443b33;border:8px ridge #bba078;padding:25px;max-width:480px}#die{font-size:95px;text-shadow:4px 4px #171318;color:#b4cbea}section[hidden],#layout[hidden],#start[hidden]{display:none}@media(max-width:1000px){#layout{grid-template-columns:1fr 2fr}#right{grid-column:1/-1}}@media(max-width:650px){#layout{display:block}}</style></head><body>
<header><strong>⚔ ACE ADVENTURES</strong><span>RETRO D20 RPG · v0.2.0</span><div><button onclick="update(false)">Check Updates</button><button onclick="update(true)">Install Update</button></div></header><p id="notice" class="muted" style="text-align:center"></p>
<div id="start" class="panel"><h3>CHARACTER ROULETTE — ONE ROLL ONLY</h3><p>Choose only your name, age, and class. All other traits are permanently randomised.</p><label>Name<input id="name" maxlength="32"></label><label>Age<input id="age" type="number" value="20" min="10" max="120"></label><p>Choose your class:</p><div id="classes"><button onclick="cls('Rogue')">Rogue</button><button onclick="cls('Mage')">Mage</button><button onclick="cls('Fighter')">Fighter</button><button onclick="cls('Vessel')">Vessel</button></div><p id="chosen"></p><button onclick="create()">🎲 GENERATE PERMANENT CHARACTER</button></div>
<div id="layout" hidden><aside><div class="panel"><h3>CHARACTER SHEET</h3><div id="identity"></div><div id="vitals" class="row"></div><div class="grid" id="stats"></div></div><div class="panel"><h3>SKILLS</h3><div id="skills"></div></div><div class="panel"><h3>PASSIVES</h3><div id="passives"></div></div></aside>
<main><div class="panel"><h3>THE WORLD</h3><div id="map"></div><div id="enemy"></div><div><button onclick="action('Find enemy')">Encounter</button><button onclick="action('Rest')">Rest</button></div></div><div class="panel"><h3>STORY & DICE LOG</h3><div id="log"></div><textarea rows="3" id="input" placeholder="Type any action or strategy. Example: I use my fire magic to ignite dry leaves and make smoke so I can escape."></textarea><button onclick="action()">ATTEMPT ACTION</button></div><div class="panel"><h3>SHOP</h3><div id="shop"></div></div></main>
<aside id="right"><div class="panel"><h3>PIXEL CHARACTER</h3><canvas id="sprite" width="96" height="96"></canvas></div><div class="panel"><h3>PATH / MAGIC TYPE</h3><div id="path"></div></div><div class="panel"><h3>MOVESET · ACTIVE</h3><div id="moves"></div></div><div class="panel"><h3>EQUIPMENT</h3><div id="items"></div></div></aside></div>
<div id="modal"><div id="dicebox"><h3>🎲 D20 ACTION CHECK</h3><p id="check"></p><div id="die">20</div><p id="dc"></p><button id="rollbtn" onclick="roll()">ROLL D20</button><div id="outcome"></div><button id="continue" hidden onclick="closeDie()">CONTINUE</button></div></div>
<script>
let S,C,selected;const $=x=>document.getElementById(x),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path,data){let r=await fetch(path,data===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)}),j=await r.json();if(!r.ok)throw Error(j.error||"Failed");return j}
function cls(x){selected=x;$("chosen").textContent="Chosen: "+x}
async function create(){try{if(!confirm("One roll only. This character cannot be rerolled. Continue?"))return;await api("/api/create",{cls:selected,name:$("name").value,age:$("age").value});refresh()}catch(e){$("notice").textContent=e.message}}
function paint(c){let q=$("sprite").getContext("2d");q.imageSmoothingEnabled=false;let r=(x,y,w,h,k)=>{q.fillStyle=k;q.fillRect(x,y,w,h)};r(0,0,96,96,"#bcb2a2");r(16,74,65,10,"#815f47");r(24,84,50,7,"#6a4c3c");r(39,25,21,15,"#3c322d");r(43,38,13,15,"#cda681");let color={Rogue:"#496956",Mage:"#685792",Fighter:"#627990",Vessel:"#a17d56"}[c.class];r(40,53,20,24,color);r(33,55,8,19,color);r(60,55,7,19,color);r(43,77,7,13,"#3b342d");r(53,77,7,13,"#3b342d");r(46,44,2,2,"#222");r(54,44,2,2,"#222");r(30,55,3,31,"#d3c4a7")}
function map(seed){let h="";for(let y=0;y<8;y++)for(let x=0;x<13;x++){let n=(x*31+y*53+seed)%17;h+='<div class="tile" style="background:'+(y===4?"#977d59":n===2?"#6a795d":"")+'">'+(x===6&&y===4?"🧙":n===3?"🌲":n===5?"🌿":"")+"</div>"}$("map").innerHTML=h}
function render(){C=S.character;$("start").hidden=!!C;$("layout").hidden=!C;if(!C)return;$("identity").innerHTML="<b>"+esc(C.name)+"</b> · Age "+C.age+"<br>Lv "+C.level+" "+esc(C.race)+" "+esc(C.class);$("vitals").innerHTML=[["AC",C.ac],["HP",C.hp+"/"+C.max_hp],["MP",C.mana+"/"+C.max_mana],["HIT",C.hit_die]].map(x=>'<div class="stat">'+x[0]+"<br>"+x[1]+"</div>").join("");$("stats").innerHTML=Object.entries(C.abilities).map(([k,v])=>'<div class="stat">'+k+"<br>"+v+"</div>").join("");$("skills").innerHTML=C.skills.map(x=>"• "+esc(x)+"<br>").join("");$("passives").textContent=C.passives.join(", ");$("path").innerHTML="<b>"+esc(C.path)+"</b><br>Affinity: "+esc(C.magic);$("moves").innerHTML=C.moves.map(x=>'<button onclick="action('+JSON.stringify(x).replace(/"/g,"&quot;")+')">'+esc(x)+"</button>").join("");$("items").innerHTML=C.items.map(x=>"• "+esc(x)+"<br>").join("")+"<p>Gold: "+C.gold+"</p>";$("log").innerHTML=S.history.slice(-14).map(x=>'<div class="entry"><b>'+esc(x.action)+"</b><br>"+esc(x.result)+"</div>").join("");$("enemy").textContent=S.enemy?S.enemy.name+" · HP "+S.enemy.hp+"/"+S.enemy.max_hp:"No enemy currently present";$("shop").innerHTML=[["Health Potion",12],["Mana Potion",14],["Smoke Bomb",20],["Iron Dagger",25]].map(([x,p])=>'<button onclick="action('+JSON.stringify("Buy "+x).replace(/"/g,"&quot;")+')">'+esc(x)+" "+p+"g</button>").join("");paint(C);map(S.seed);if(S.pending)showDie(S.pending)}
async function refresh(){S=await api("/api/state");render()}
async function action(a){a=a||$("input").value;try{$("notice").textContent="Checking action...";let r=await api("/api/action",{action:a});$("input").value="";await refresh();$("notice").textContent=r.immediate||"Roll the D20."}catch(e){$("notice").textContent=e.message}}
function showDie(p){$("modal").style.display="flex";$("check").textContent=p.action;$("dc").textContent=p.attribute+" modifier "+p.bonus+" · Difficulty "+p.dc;$("rollbtn").hidden=false;$("continue").hidden=true;$("outcome").textContent="";$("die").textContent="20"}
async function roll(){try{$("rollbtn").disabled=true;let j=await api("/api/roll",{});await refresh();$("modal").style.display="flex";$("die").textContent=j.die;$("outcome").innerHTML="<h3>"+esc(j.degree)+"</h3><p>"+esc(j.rule)+"</p><p>"+esc(j.story)+"</p>";$("rollbtn").hidden=true;$("continue").hidden=false;$("rollbtn").disabled=false}catch(e){$("notice").textContent=e.message;$("rollbtn").disabled=false}}
function closeDie(){$("modal").style.display="none"}
async function update(install){try{$("notice").textContent="Checking GitHub...";let r=await api("/api/update",{install});$("notice").textContent=r.message}catch(e){$("notice").textContent=e.message}}
refresh()
</script></body></html>'''
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=="/":return self.send_html(HTML)
  if self.path=="/api/state":return self.send_json(load())
  self.send_json({"error":"Not found"},404)
 def do_POST(self):
  try:
   n=int(self.headers.get("Content-Length","0"))
   if n>100000:raise ValueError("Request too large")
   data=json.loads(self.rfile.read(n)) if n else {}
   if self.path=="/api/create":
    s=load()
    if s["character"]:raise ValueError("Character already exists. No rerolls.")
    s["character"]=character(data.get("cls"),str(data.get("name","")),data.get("age",20));log(s,"Character created","Your path is "+s["character"]["path"]);save(s);return self.send_json({"ok":True})
   if self.path=="/api/action":
    s=load()
    if not s["character"]:raise ValueError("Create a character first")
    action=str(data.get("action",""))[:700];r=plan(s,action)
    if "immediate" in r:log(s,action,r["immediate"])
    save(s);return self.send_json(r)
   if self.path=="/api/roll":
    s=load();return self.send_json(roll(s))
   if self.path=="/api/update":return self.send_json(updater(bool(data.get("install"))))
   self.send_json({"error":"Not found"},404)
  except Exception as e:self.send_json({"error":str(e)},400)
 def send_json(self,obj,status=200):
  b=json.dumps(obj).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def send_html(self,obj):
  b=obj.encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def log_message(self,*a):pass
def main():
 latest=DATA/"adventures.py"
 if latest.is_file() and Path(__file__).resolve()!=latest.resolve():os.execv("/usr/bin/env",["env","python3",str(latest),*sys.argv[1:]])
 srv=ThreadingHTTPServer(("127.0.0.1",0),Handler);url="http://127.0.0.1:"+str(srv.server_port)
 if "--native" in sys.argv:(DATA/"server-port").write_text(str(srv.server_port))
 else:threading.Timer(.7,lambda:webbrowser.open(url)).start()
 print(url,flush=True);srv.serve_forever()
if __name__=="__main__":main()
