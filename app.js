const $ = (id) => document.getElementById(id);
const fmtDate = (iso) => new Intl.DateTimeFormat('en-US',{dateStyle:'full',timeZone:'Asia/Bangkok'}).format(new Date(`${iso}T12:00:00+07:00`));
function el(tag, className, value) { const node=document.createElement(tag); if(className)node.className=className;if(value!==undefined)node.textContent=value;return node; }
const CHIP={'must-know':'Must-know','worth-knowing':'Worth knowing','just-for-fun':'Just for fun'};
const TAGS={'must-know':' · ★ MUST-KNOW','worth-knowing':' · WORTH KNOWING','just-for-fun':' · JUST FOR FUN'};
function renderBriefing(data){const box=$('briefing'),b=data.briefing;box.replaceChildren();if(!b||!b.big_picture){box.hidden=true;return;}box.hidden=false;box.append(el('span','eyebrow','TODAY, IN A NUTSHELL'),el('p','briefing-big',b.big_picture));const pick=data.stories[b.top_pick];if(pick&&b.top_pick_why){const p=el('p','briefing-pick');p.append(el('strong','','If you read only one thing: '),document.createTextNode(pick.title+' — '+b.top_pick_why));box.append(p);}}
function basics(s){const has=s.background||(s.jargon&&s.jargon.length)||(s.views&&s.views.length);if(!has)return null;const d=el('details','basics');d.append(el('summary','','Know the basics'));if(s.background)d.append(el('p','',s.background));if(s.views&&s.views.length){const v=el('div','views');v.append(el('strong','','How different sides describe it'));const ul=el('ul');s.views.forEach(x=>ul.append(el('li','',x)));v.append(ul);d.append(v);}if(s.jargon&&s.jargon.length){const l=el('dl','jargon');s.jargon.forEach(x=>l.append(el('dt','',x.term),el('dd','',x.meaning)));d.append(l);}return d;}
function renderLearn(data){const box=$('learn'),l=data.learn;box.replaceChildren();if(!l||!l.term||!l.explainer){box.hidden=true;return;}box.hidden=false;box.append(el('span','eyebrow','Learn one thing'),el('h3','',l.term),el('p','learn-text',l.explainer));if(l.why_in_news)box.append(el('p','learn-why',l.why_in_news));}
function render(data){
  $('editionDate').textContent=fmtDate(data.date);$('dateBadge').textContent=fmtDate(data.date);$('editionCount').textContent=`${data.stories.length} STORIES · ${data.mode==='ai'?'THE TEA, AI-ASSISTED':'NEWS FEED EDITION'}`;
  $('updatedAt').textContent=`Updated ${new Intl.DateTimeFormat('en-US',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Bangkok'}).format(new Date(data.generated_at))} Bangkok`;
  const grid=$('storyGrid');grid.replaceChildren();renderBriefing(data);
  data.stories.forEach((s,i)=>{
    const card=el('article','story'+(s.importance==='must-know'?' must':''));const top=el('div','story-top');top.append(el('span','category',s.category),el('span','chip chip-'+(s.importance||'none'),CHIP[s.importance]||''));
    const title=el('h3','',s.title), desc=el('p','',s.summary||'Couldn’t get enough of this one to spill the tea reliably. Read the original report for the details.');
    if(s.why_it_matters){const why=el('p','story-why');why.append(el('strong','','So basically… '),document.createTextNode(s.why_it_matters));card.append(top,title,why,desc);}else{card.append(top,title,desc);}
    if(s.uncertainty){const uncertain=el('p','story-uncertainty');uncertain.append(el('strong','','Still unconfirmed: '),document.createTextNode(s.uncertainty));card.append(uncertain);}
    const extra=basics(s);if(extra)card.append(extra);if(s.category==='Money')card.append(el('p','money-note','General information, not financial advice.'));const bottom=el('div','story-bottom');bottom.append(el('span','source',s.source||'News source'));
    const link=el('a','','Read original ↗');link.href=s.url;link.target='_blank';link.rel='noopener noreferrer';bottom.append(link);
    card.append(bottom);grid.append(card);
  });renderLearn(data);$('status').textContent='';
}
async function loadEdition(file){$('status').textContent='Loading your edition…';try{const response=await fetch(`data/${encodeURIComponent(file)}.json`,{cache:'no-store'});if(!response.ok)throw Error('Edition unavailable');const data=await response.json();render(data);}catch(err){$('status').textContent='This edition could not be loaded. Please try again later.';}}
async function init(){try{const response=await fetch('data/index.json',{cache:'no-store'});if(!response.ok)throw Error('Archive unavailable');const archive=await response.json();const select=$('editionSelect');select.replaceChildren();if(!archive.length){$('status').textContent='Your first edition will appear after the first scheduled update.';return;}archive.forEach(d=>{const opt=document.createElement('option');opt.value=d;opt.textContent=fmtDate(d);select.append(opt)});select.addEventListener('change',()=>loadEdition(select.value));await loadEdition(archive[0]);}catch(e){$('status').textContent='The archive is not available yet. Run the news updater to create your first edition.';}}
init();
