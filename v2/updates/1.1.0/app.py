"""ACE Adventures 2 native Tk window. Standard library; no browser required."""
from __future__ import annotations
import json,sys,uuid
from pathlib import Path
import tkinter as tk
from tkinter import ttk,messagebox
from game import new_campaign,create_character,save_campaign,list_campaigns,roll_d20,begin_encounter,attempt_action
from updater import activate,load_active
from urllib.request import urlopen,Request
from pixel_art import forest,character,d20

APP_ROOT=Path.home()/"Library"/"Application Support"/"ACE Adventures 2"
BACKGROUND="#211b1a";PANEL="#3b3028";GOLD="#d9b982";INK="#f0e5cd";BUTTON="#67513b"
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ACE Adventures 2 — Adventure 1.1.0")
        self.geometry("1150x740")
        self.minsize(820,570)
        self.configure(bg=BACKGROUND)
        self.active_id=None;self.data=None
        self.home()
    def clear(self):
        for w in self.winfo_children():w.destroy()
    def label(self,where,text,size=13,**kw):
        return tk.Label(where,text=text,font=("Menlo",size,"bold" if size>=19 else "normal"),fg=INK,bg=kw.get("bg",PANEL),anchor=kw.get("anchor","w"),wraplength=kw.get("wraplength",0))
    def button(self,where,text,command):
        return tk.Button(where,text=text,command=command,fg=INK,bg=BUTTON,activebackground="#93754a",activeforeground="white",font=("Menlo",12),relief="ridge",bd=4,padx=14,pady=9)
    def frame(self,where,**kw):
        return tk.Frame(where,bg=kw.get("bg",PANEL),highlightbackground=GOLD,highlightthickness=2)
    def header(self):
        h=self.frame(self,bg="#30251f");h.pack(fill="x",padx=12,pady=10)
        self.label(h,"⚔ ACE ADVENTURES 2  ·  ENCOUNTERS v1.1.0",22,bg="#30251f").pack(side="left",padx=14,pady=9)
        self.button(h,"Check Updates",self.check_updates).pack(side="right",padx=10)
        self.button(h,"Campaign Library",self.home).pack(side="right",padx=10)
    def check_updates(self):
        """The initial app checks GitHub; activation requires an explicit user click."""
        try:
            url="https://raw.githubusercontent.com/LGBerlin/ACE-Adventures/main/v2/latest.json"
            with urlopen(Request(url,headers={"User-Agent":"ACE-Adventures-2"}),timeout=15) as resp:
                manifest=json.load(resp)
            installed=load_active(APP_ROOT/"updates")["version"]
            if manifest["version"] == installed:
                messagebox.showinfo("Updates","You have the latest version.")
                return
            if not messagebox.askyesno("ACE Adventures Update","Version "+manifest["version"]+" is available. Download and verify it?"):
                return
            activate(APP_ROOT/"updates",manifest)
            messagebox.showinfo("Update downloaded","The update was verified. Quit and reopen ACE Adventures 2 to load it.")
        except Exception as exc:
            messagebox.showerror("Update problem",str(exc))

    def home(self):
        self.clear();self.header()
        body=self.frame(self,bg=BACKGROUND);body.pack(fill="both",expand=True,padx=12,pady=(0,12))
        side=self.frame(body);side.pack(side="left",fill="y",padx=8,pady=8)
        self.label(side,"CAMPAIGNS",19).pack(padx=15,pady=15)
        self.button(side,"+ NEW CAMPAIGN",self.new_campaign_screen).pack(fill="x",padx=12,pady=8)
        entries=list_campaigns(APP_ROOT)
        detail=self.frame(body);detail.pack(side="left",fill="both",expand=True,padx=8,pady=8)
        self.label(detail,"CHOOSE YOUR ADVENTURE",24).pack(padx=20,pady=22)
        for id,c in entries:
            name=c.get("title","Untitled")
            self.button(side,name,lambda cid=id:self.open_campaign(cid)).pack(fill="x",padx=12,pady=4)
        art=tk.Canvas(detail,width=720,height=260,highlightthickness=3,highlightbackground=GOLD)
        art.pack(fill="x",padx=22,pady=(14,16));forest(art)
        if entries:
            id,c=entries[-1];self.label(detail,c.get("title","Untitled"),22).pack(padx=20,pady=10)
            hero=c.get("character")
            self.label(detail,hero["name"]+" · Level "+str(hero["level"])+" · "+hero["path"] if hero else "Character not yet generated",14).pack(padx=20,pady=12)
            self.button(detail,"CONTINUE ADVENTURE →",lambda:self.open_campaign(id)).pack(padx=20,pady=20)
        else:
            self.label(detail,"Your journey begins with a new campaign.",16).pack(padx=20,pady=35)
    def new_campaign_screen(self):
        self.clear();self.header();p=self.frame(self);p.pack(fill="x",padx=70,pady=35)
        self.label(p,"CREATE NEW CAMPAIGN",23).pack(padx=25,pady=20)
        name=tk.Entry(p,font=("Menlo",15));name.pack(fill="x",padx=25,pady=12)
        self.label(p,"Players (party expansion planned)",12).pack(padx=25,pady=8)
        players=tk.Spinbox(p,from_=1,to=8,font=("Menlo",15),width=5);players.pack(padx=25,pady=5)
        def create():
            try:
                data=new_campaign(name.get(),int(players.get()))
                id=uuid.uuid4().hex
                save_campaign(APP_ROOT,id,data);self.open_campaign(id)
            except ValueError as e:messagebox.showerror("Invalid campaign",str(e))
        self.button(p,"CREATE CAMPAIGN",create).pack(padx=25,pady=22)
    def open_campaign(self,id):
        p=APP_ROOT/"campaigns"/(id+".json")
        try:self.data=json.loads(p.read_text())
        except Exception as e:return messagebox.showerror("Campaign error",str(e))
        self.active_id=id
        if self.data.get("character"):self.character_sheet()
        else:self.character_creation()
    def save(self):
        if self.active_id and self.data:save_campaign(APP_ROOT,self.active_id,self.data)
    def character_creation(self):
        self.clear();self.header();p=self.frame(self);p.pack(fill="x",padx=70,pady=35)
        self.label(p,"CHARACTER ROULETTE — ONE PERMANENT ROLL",19).pack(padx=20,pady=15)
        self.label(p,"Choose a name, age, and one of four classes. Everything else is random.",12).pack(padx=20,pady=8)
        self.label(p,"Name",13).pack(padx=20,pady=5)
        name=tk.Entry(p,font=("Menlo",14));name.pack(padx=20,pady=5)
        self.label(p,"Age",13).pack(padx=20,pady=5)
        age=tk.Spinbox(p,from_=10,to=120,width=6,font=("Menlo",14));age.pack(padx=20,pady=5)
        chosen=tk.StringVar(value="")
        row=self.frame(p);row.pack(padx=20,pady=12)
        for cls in ("Rogue","Mage","Fighter","Vessel"):
            self.button(row,cls,lambda x=cls:chosen.set(x)).pack(side="left",padx=5)
        selected=self.label(p,"No class selected",13);selected.pack(pady=5)
        chosen.trace_add("write",lambda *_:selected.configure(text="SELECTED CLASS: "+chosen.get()))
        def generate():
            if self.data.get("character"):return
            try:
                hero=create_character(name.get(),age.get(),chosen.get())
            except ValueError as e:return messagebox.showerror("Character details",str(e))
            if not messagebox.askyesno("Permanent roll","Your class, name and age are chosen. All other results are permanent. Generate character?"):return
            self.data["character"]=hero;self.data["history"].append("Your character enters Ironwood Crossing.")
            self.save();self.character_sheet()
        self.button(p,"GENERATE PERMANENT CHARACTER",generate).pack(padx=20,pady=16)
    def character_sheet(self):
        self.clear();self.header();c=self.data["character"]
        columns=self.frame(self,bg=BACKGROUND);columns.pack(fill="both",expand=True,padx=12,pady=8)
        left=self.frame(columns);left.pack(side="left",fill="both",expand=True,padx=6,pady=5)
        right=self.frame(columns);right.pack(side="left",fill="both",expand=True,padx=6,pady=5)
        for heading,lines in [
          ("IDENTITY",["NAME    "+c["name"],"AGE     "+str(c["age"]),"CLASS   "+c["class"],"PATH    "+c["path"],"RACE    "+c["race"],"MAGIC   "+c["magic"],"LEVEL   "+str(c["level"])]),
          ("VITALS",["HP      "+str(c["hp"])+"/"+str(c["max_hp"]),"MANA    "+str(c["mana"])+"/"+str(c["max_mana"]),"GOLD    "+str(c["gold"])]),
          ("ATTRIBUTES",[k+"  "+str(v) for k,v in c["stats"].items()]),
          ("SKILLS",c["skills"])]:
            panel=self.frame(left);panel.pack(fill="x",padx=10,pady=6)
            self.label(panel,heading,17).pack(padx=12,pady=8)
            for line in lines:self.label(panel,line,12).pack(anchor="w",padx=12,pady=2)
        portrait=self.frame(right);portrait.pack(fill="x",padx=10,pady=6)
        self.label(portrait,"CHARACTER SPRITE",17).pack(padx=12,pady=8)
        canvas=tk.Canvas(portrait,width=210,height=210,bg="#b9ad96",highlightthickness=3,highlightbackground=GOLD)
        canvas.pack(pady=8)
        character(canvas,c,x=37,y=20,scale=6)
        self.label(portrait,c["race"]+"  /  "+c["class"]+"  /  "+c["path"],12).pack(padx=12,pady=6)
        for heading,lines in [("MOVESET",c["moves"]),("PASSIVES",c["passives"]),("EQUIPMENT",c["inventory"])]:
            panel=self.frame(right);panel.pack(fill="x",padx=10,pady=6)
            self.label(panel,heading,17).pack(padx=12,pady=8)
            for line in lines:self.label(panel,line,12).pack(anchor="w",padx=12,pady=3)
        encounter=self.frame(right);encounter.pack(fill="x",padx=10,pady=8)
        self.label(encounter,"IRONWOOD ENCOUNTER",17).pack(padx=12,pady=8)
        enemy=self.data.get("enemy")
        if enemy and enemy.get("hp",0)>0:
            self.label(encounter,enemy["name"]+"  HP "+str(enemy["hp"])+"/"+str(enemy["max_hp"]),13).pack(padx=12,pady=4)
        else:
            self.label(encounter,"No enemy currently present",12).pack(padx=12,pady=4)
        def find_enemy():
            message=begin_encounter(self.data)
            self.data.setdefault("history",[]).append(message)
            self.save();self.character_sheet()
        self.button(encounter,"FIND AN ENCOUNTER",find_enemy).pack(padx=12,pady=7)
        self.label(encounter,"Recent: "+str(self.data.get("history",["The forest awaits."])[-1])[-180:],11,wraplength=340).pack(padx=12,pady=6)
        actions=self.frame(right);actions.pack(fill="x",padx=10,pady=10)
        self.label(actions,"TYPE YOUR ACTION",17).pack(padx=12,pady=8)
        entry=tk.Entry(actions,font=("Menlo",12));entry.pack(fill="x",padx=12,pady=8)
        def act():
            text=entry.get().strip()
            if not text:return
            try:
                result,event=attempt_action(self.data,text)
            except ValueError as e:
                messagebox.showwarning("Action not possible",str(e))
                return
            self.save()
            self.show_dice(result,event)
            self.character_sheet()
        self.button(actions,"ATTEMPT ACTION · ROLL D20",act).pack(padx=12,pady=10)
        self.button(actions,"SAVE & RETURN TO CAMPAIGNS",self.return_home).pack(padx=12,pady=9)
    def show_dice(self,result,description):
        pop=tk.Toplevel(self)
        pop.title("D20 — Outcome")
        pop.configure(bg=BACKGROUND)
        pop.geometry("360x430")
        pop.transient(self)
        pop.grab_set()
        self.label(pop,"THE D20 HAS SPOKEN",20,bg=BACKGROUND).pack(padx=20,pady=14)
        die=tk.Canvas(pop,width=250,height=215,bg=BACKGROUND,highlightthickness=0)
        die.pack()
        d20(die,result["roll"])
        self.label(pop,result["degree"].upper(),19,bg=BACKGROUND).pack(padx=18,pady=9)
        self.label(pop,"Roll %s  %+d  =  %s  vs DC %s"%(result["roll"],result["modifier"],result["total"],result["dc"]),12,bg=BACKGROUND).pack(pady=5)
        self.label(pop,description,11,bg=BACKGROUND,wraplength=310).pack(pady=6,padx=16)
        self.button(pop,"CONTINUE",pop.destroy).pack(pady=10)

    def return_home(self):
        self.save();self.active_id=None;self.data=None;self.home()

if __name__=="__main__":App().mainloop()
