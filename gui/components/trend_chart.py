from __future__ import annotations
import tkinter as tk
import customtkinter as ctk
from core.timezone import format_pht
from gui.theme import MUTED, PRIMARY, SUCCESS, SURFACE_ALT, WARNING


class TrendChart(ctk.CTkFrame):
    """Small Canvas line chart with click/hover detail and an empty state."""
    def __init__(self, master, title: str, unit: str, series: list[tuple[str, str, list[dict], str]], **kwargs):
        super().__init__(master, corner_radius=12, **kwargs); self.title, self.unit, self.series, self.points = title, unit, series, []
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=14, pady=(12, 0))
        self.detail = ctk.CTkLabel(self, text="Last 10 relevant runs", text_color=MUTED); self.detail.pack(anchor="w", padx=14)
        self.canvas = tk.Canvas(self, height=210, highlightthickness=0, bg="#14212C"); self.canvas.pack(fill="x", padx=10, pady=(4, 12)); self.canvas.bind("<Configure>", lambda _: self.draw()); self.canvas.bind("<Motion>", self.hover); self.draw()
    def draw(self):
        c=self.canvas; c.delete("all"); width=max(c.winfo_width(),300); height=210; active=[(name,key,data,color) for name,key,data,color in self.series if data]
        if not active: c.create_text(width/2,height/2,text="No data yet — run a check to see a trend.",fill="#9FB0C2",font=("Segoe UI",11)); return
        values=[item[key] for _,key,data,_ in active for item in data]; top=max(max(values)*1.12, 1); left,right,top_y,bottom=45,width-16,16,height-38
        for fraction in (0, .5, 1):
            y=bottom-(bottom-top_y)*fraction; c.create_line(left,y,right,y,fill="#2B3A46"); c.create_text(left-6,y,text=f"{top*fraction:.0f}",fill="#9FB0C2",anchor="e",font=("Segoe UI",9))
        self.points=[]
        for name,key,data,color in active:
            coords=[]
            for i,item in enumerate(data):
                x=left+(right-left)*(i/(max(len(data)-1,1))); y=bottom-(item[key]/top)*(bottom-top_y);coords.extend((x,y));self.points.append((x,y,name,item,key))
            if len(coords)>2:c.create_line(*coords,fill=color,width=2,smooth=True)
            for x,y in zip(coords[::2],coords[1::2]):c.create_oval(x-3,y-3,x+3,y+3,fill=color,outline="")
        labels=active[0][2]
        for i,item in enumerate(labels):
            if i in (0,len(labels)-1) or len(labels)<=5:
                x=left+(right-left)*(i/(max(len(labels)-1,1)));c.create_text(x,bottom+16,text=format_pht(item["label"]).split(",")[0],fill="#9FB0C2",font=("Segoe UI",8))
        self.detail.configure(text=" · ".join(f"{name} ({self.unit})" for name,_,data,_ in active))
    def hover(self,event):
        if not self.points:return
        x,y,name,item,key=min(self.points,key=lambda point:(point[0]-event.x)**2+(point[1]-event.y)**2)
        if (x-event.x)**2+(y-event.y)**2<900:self.detail.configure(text=f"{name}: {item[key]} {self.unit} · {format_pht(item['label'])}")
