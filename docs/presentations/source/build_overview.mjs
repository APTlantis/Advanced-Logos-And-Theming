import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const runtime=process.env.APT_THEME_NODE_MODULES || 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {Presentation,PresentationFile}=await import(pathToFileURL(runtime+'/\u0040oai/artifact-tool/dist/artifact_tool.mjs').href);
const root=path.resolve('.');
const data=JSON.parse(await fs.readFile('docs/presentations/source/overview-content.json','utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
p.theme.colorScheme={name:'Aptlantis-Black-Gold',themeColors:data.colors};
p.theme.defaultFont='Arial';
function text(s,value,left,top,width,height,size=28,color='lt1',bold=false){
 const sh=s.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
 sh.text=value; sh.text.style={typeface:'Arial',fontSize:size,color,bold}; return sh;
}
const tableOwners=[];
function table(s,values,top=206,height=380,widths){
 const rows=values.length,columns=values[0].length;
 const t=s.tables.add({rows,columns,left:64,top,width:1152,height,columnWidths:widths || Array(columns).fill(1152/columns),values});
 t.cells.block({row:0,column:0,rowCount:rows,columnCount:columns}).assign({margins:{top:8,bottom:6,left:14,right:14}});
 for(let r=0;r<rows;r++)for(let c=0;c<columns;c++){
  const cell=t.getCell(r,c); cell.fill=r===0?'dk2':'dk1';
  cell.text.style={typeface:'Arial',fontSize:25,color:r===0?'accent1':'lt1',bold:r===0};
 }
 return t;
}
for(const [i,c] of data.slides.entries()){
 const s=p.slides.add(); s.background.fill='dk1';
 text(s,'APTLANTIS  /  LOGOS AND THEMING',64,22,900,30,16,'accent2');
 text(s,String(i+1).padStart(2,'0')+' / 24',1110,22,106,30,16,'accent2');
 if(c.kind==='cover'){
  text(s,c.title,64,138,635,145,64,'accent1',true);
  text(s,c.lead,64,315,615,116,34,'lt1');
  text(s,c.groups[0][0],64,467,610,45,26,'accent1',true);
  text(s,c.groups[0][1],64,515,610,87,26,'lt1');
  const bytes=await fs.readFile('output/blackgold/source/apt-zig-dark-logo.png');
  s.images.add({blob:new Uint8Array(bytes),contentType:'image/png',alt:'Preserved Aptlantis Zig artwork used for the Black-Gold run',fit:'contain',position:{left:731,top:118,width:485,height:485}});
  text(s,c.groups[1][0],64,645,1000,32,20,'accent2');
 }else{
  text(s,c.title,64,70,1152,64,42,'accent1',true);
  text(s,c.lead,64,143,1152,66,28,'accent2');
  if(c.kind==='palette'){
   const entries=Object.entries(data.palette);
   const values=Array.from({length:8},(_,r)=>Array.from({length:4},(_,col)=>{const [id,v]=entries[r*4+col];return id+'   '+v.hex;}));
   const t=table(s,values,220,410,[288,288,288,288]);tableOwners.push(i+1);
   for(let r=0;r<8;r++)for(let col=0;col<4;col++){
    const [id,v]=entries[r*4+col];const cell=t.getCell(r,col);cell.fill=v.hex;
    cell.text.style={typeface:'Arial',fontSize:23,color:v.oklch.l>.65?'dk1':'lt1',bold:true};
   }
  }else if(c.table){
   const cols=c.table[0].length;
   table(s,c.table,222,c.table.length>6?414:390,cols===2?(i===18?[410,742]:i===22?[430,722]:[365,787]):cols===3?[365,210,577]:[480,224,224,224]);tableOwners.push(i+1);
  }else{
   for(const [g,[heading,body]] of c.groups.entries()){
    const y=235+g*132;
    text(s,heading,64,y,1100,42,30,'accent1',true);
    text(s,body,64,y+48,1100,74,29,'lt1');
   }
  }
  text(s,'LOCAL PILOT · 8 OCT 2026',64,674,650,26,16,'accent2');
  text(s,'Black-Gold · image-derived dark theme',795,674,421,26,16,'accent2');
 }
 const sourceNotes=c.sources.map(v=>{const hit=data.sources.find(x=>x.source===v);return hit?hit.path+'\nSHA-256 '+hit.sha256:v;}).join('\n\n');
 s.speakerNotes.text=c.notes.replaceAll(/(?<=\d)(?=[a-zA-Z])/g,' ')+'\n\nPRIMARY SOURCES (captured 2026-10-08)\n'+sourceNotes;
}
await fs.mkdir('.build/overview',{recursive:true});
const file=await PresentationFile.exportPptx(p);
await file.save('.build/overview/draft.pptx');
await fs.writeFile('.build/overview/table-owners.json',JSON.stringify(tableOwners));
console.log('Exported 24 slides; native tables on '+tableOwners.join(', '));
