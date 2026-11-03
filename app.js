const $ = (id) => document.getElementById(id);
const fmtDate = (iso) => new Intl.DateTimeFormat('en-US',{dateStyle:'full',timeZone:'Asia/Bangkok'}).format(new Date(`${iso}T12:00:00+07:00`));
function el(tag, className, value) { const node=document.createElement(tag); if(className)node.className=className;if(value!==undefined)node.textContent=value;return node; }
function render(data){
  $('editionDate').textContent=fmtDate(data.date);$('dateBadge').textContent=fmtDate(data.date);$('editionCount').textContent=`${data.stories.length} STORIES · ${data.mode==='ai'?'AI-ASSISTED DIGEST':'NEWS FEED EDITION'}`;
  $('updatedAt').textContent=`Updated ${new Intl.DateTimeFormat('en-US',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Bangkok'}).format(new Date(data.generated_at))} Bangkok`;
  const grid=$('storyGrid');grid.replaceChildren();
  data.stories.forEach((s,i)=>{
    const card=el('article','story');const top=el('div','story-top');top.append(el('span','category',s.category),el('span','number',String(i+1).padStart(2,'0')));
    const title=el('h3','',s.title), desc=el('p','',s.summary||'Open the original article for the full story.');
    const bottom=el('div','story-bottom');bottom.append(el('span','source',s.source||'News source'));
    const link=el('a','','Read original ↗');link.href=s.url;link.target='_blank';link.rel='noopener noreferrer';bottom.append(link);
    card.append(top,title,desc,bottom);grid.append(card);
  });$('status').textContent='';
}
async function loadEdition(file){$('status').textContent='Loading your edition…';try{const response=await fetch(`data/${encodeURIComponent(file)}.json`,{cache:'no-store'});if(!response.ok)throw Error('Edition unavailable');const data=await response.json();render(data);}catch(err){$('status').textContent='This edition could not be loaded. Please try again later.';}}
async function init(){try{const response=await fetch('data/index.json',{cache:'no-store'});if(!response.ok)throw Error('Archive unavailable');const archive=await response.json();const select=$('editionSelect');select.replaceChildren();if(!archive.length){$('status').textContent='Your first edition will appear after the first scheduled update.';return;}archive.forEach(d=>{const opt=document.createElement('option');opt.value=d;opt.textContent=fmtDate(d);select.append(opt)});select.addEventListener('change',()=>loadEdition(select.value));await loadEdition(archive[0]);}catch(e){$('status').textContent='The archive is not available yet. Run the news updater to create your first edition.';}}
init();
