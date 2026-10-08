// Local, repeatable editable PowerPoint sample. No theme installation.
import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const [modulePath, input, output] = process.argv.slice(2);
const {Presentation, PresentationFile} = await import(pathToFileURL(modulePath).href);
const {name, slots, roles} = JSON.parse(await fs.readFile(input, 'utf8'));
const deck = Presentation.create({slideSize: {width: 1280, height: 720}});
deck.theme.colorScheme = {name, themeColors: slots};
function slide(title) {
  const s = deck.slides.add();
  s.background.fill = 'dk1';
  if (title) text(s, title, 64, 48, 1152, 74, 44, 'accent1', true);
  return s;
}
function text(s, value, left, top, width, height, size=28, color='lt1', bold=false) {
  const shape = s.shapes.add({geometry:'textbox', position:{left,top,width,height}, fill:'none', line:{fill:'none',width:0}});
  shape.text = value;
  shape.text.style = {typeface:'Arial', fontSize:size, color, bold};
  return shape;
}
let s = slide();
text(s, name, 80, 210, 1120, 170, 60, 'accent1', true);
text(s, 'Dark theme · PowerPoint sample', 80, 420, 1120, 64, 30, 'lt2');
s = slide('Typography and content');
text(s, 'A presentation shaped by its source palette', 64, 164, 1136, 90, 38, 'accent2', true);
text(s, 'Body text should stay readable through longer passages. This sample uses the native Office theme slots for its text and chart colors.', 64, 300, 1080, 130, 30);
text(s, 'Secondary text and supporting detail', 64, 490, 1080, 52, 26, 'lt2');
text(s, 'Hyperlink color', 64, 566, 530, 50, 26, 'hlink');
text(s, 'Followed hyperlink color', 630, 566, 580, 50, 26, slots.folHlink);
s = slide('Office color slots');
const entries = Object.entries(slots);
const table = s.tables.add({rows:13,columns:4,left:64,top:142,width:1152,height:520,columnWidths:[190,350,250,362],values:[['Office slot','Mapped role','Color','Swatch'],...entries.map(([key,color])=>[key,roles[key],color,''])]});
table.cells.block({row:0,column:0,rowCount:13,columnCount:4}).assign({margins:{top:2,bottom:2,left:12,right:12}});
for(let r=0;r<13;r++) for(let c=0;c<4;c++) {
  const cell=table.getCell(r,c);
  cell.fill=r===0?'dk2':'dk1';
  cell.text.style={typeface:'Arial',fontSize:24,color:r===0?'accent1':'lt1',bold:r===0};
  if(r>0 && c===3) cell.fill=entries[r-1][0]==='folHlink'?slots.folHlink:entries[r-1][0];
}
s = slide('Accent colors in an editable chart');
text(s, 'Illustrative sample values · no measured project data',64,130,1152,44,24,'lt2');
s.charts.add('bar', {
  position:{left:64,top:210,width:1152,height:450},
  categories:['Sample A','Sample B'],
  series:Array.from({length:6},(_,i)=>({name:`Accent ${i+1}`,values:[4+i,10-i],fill:`accent${i+1}`})),
  barOptions:{direction:'column',grouping:'clustered'},
  hasLegend:true,legend:{position:'bottom',textStyle:{typeface:'Arial',fontSize:24,fill:'lt1'}},
  chartFill:'dk1',plotAreaFill:'dk1',
  xAxis:{textStyle:{typeface:'Arial',fontSize:24,fill:'lt1'}},
  yAxis:{textStyle:{typeface:'Arial',fontSize:24,fill:'lt1'},majorGridlines:{fill:'lt2',width:1}},
});
await (await PresentationFile.exportPptx(deck)).save(output);
