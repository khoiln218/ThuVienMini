'use strict';
const $ = s => document.querySelector(s);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let user, page='dashboard', bookData=[], readerData=[];
async function api(path, method='GET', body){
  const response=await fetch('/api'+path,{method,headers:{'Content-Type':'application/json','X-Library-Request':'1'},body:body===undefined?undefined:JSON.stringify(body)});
  const data=await response.json();
  if(!response.ok){if(response.status===401 && path!='/login')showLogin();throw new Error(Array.isArray(data.detail)?data.detail.map(e=>e.loc.slice(1).join('.')+': '+e.msg).join('\n'):data.detail||'Không thể thực hiện yêu cầu');}
  return data;
}
function notice(message,error=false){const el=$('#notification');el.textContent=message;el.hidden=false;el.style.background=error?'#fbe9e1':'#e4eee3';}
function showLogin(){$('#app-view').hidden=true;$('#login-view').hidden=false;$('#editor').close();}
async function enter(){user=await api('/me');$('#login-view').hidden=true;$('#app-view').hidden=false;$('#user-label').textContent=user.username+' · '+(user.role==='admin'?'Quản trị viên':'Thủ thư');$('#today').textContent=new Date().toLocaleDateString('vi-VN',{weekday:'long',day:'numeric',month:'long',year:'numeric'});await navigate(page);}
async function navigate(next){page=next;document.querySelectorAll('.page').forEach(el=>el.hidden=el.id!==page);document.querySelectorAll('nav button').forEach(el=>el.classList.toggle('active',el.dataset.page===page));$('#page-title').textContent={dashboard:'Tổng quan thư viện',books:'Kho sách',readers:'Quản lý độc giả',loans:'Mượn & trả sách'}[page];await refresh();}
function empty(cols,text='Chưa có dữ liệu'){return `<tr><td colspan="${cols}" class="empty">${text}</td></tr>`;}
function badge(l){return `<span class="badge ${l.status==='overdue'?'late':l.status==='returned'?'done':''}">${l.status==='returned'?'Đã trả':l.status==='overdue'?'Quá hạn '+l.overdue_days+' ngày':'Đang mượn'}</span>`;}
async function refresh(){
 if(page==='dashboard'){
  const [s,late]=await Promise.all([api('/stats'),api('/loans?status=overdue')]);
  $('#stats').innerHTML=[['Đầu sách',s.titles,s.copies+' bản trong kho'],['Bản có sẵn',s.available,s.readers+' độc giả hoạt động'],['Đang mượn',s.borrowing,s.returned+' phiếu đã trả'],['Phiếu quá hạn',s.overdue,'Cần theo dõi hoàn trả']].map((x,i)=>`<div class="stat ${i===3?'alert':''}"><span>${x[0]}</span><strong>${x[1]}</strong><span>${x[2]}</span></div>`).join('');
  $('#overdue-list').innerHTML=late.slice(0,6).map(l=>`<div class="list-item"><div><b>${esc(l.title)}</b><small>${esc(l.name)} · Phiếu #${l.id} · Hạn ${l.due_on}</small></div><div>${badge(l)}<br><button class="action" data-return="${l.id}">Trả sách</button></div></div>`).join('')||'<p class="empty">Không có phiếu quá hạn.</p>';
  $('#top-books').innerHTML=s.top_books.map((b,i)=>`<div class="list-item"><span>${i+1}. ${esc(b.title)}</span><b>${b.count} lượt</b></div>`).join('')||'<p class="empty">Chưa có lượt mượn.</p>';
 }else if(page==='books'){
  bookData=await api('/books?q='+encodeURIComponent($('#book-search input').value));
  $('#book-rows').innerHTML=bookData.map(b=>`<tr><td>${esc(b.code)}</td><td class="text-wrap"><b>${esc(b.title)}</b><small>${esc(b.author)}</small></td><td>${esc(b.category)}</td><td>${b.total}</td><td><span class="badge ${b.available?'':'late'}">${b.available}</span></td><td><button class="action" data-edit-book="${b.id}">Sửa</button>${user.role==='admin'?`<button class="action danger" data-remove="books/${b.id}">Ngừng</button>`:''}</td></tr>`).join('')||empty(6,'Không tìm thấy sách.');
 }else if(page==='readers'){
  readerData=await api('/readers?q='+encodeURIComponent($('#reader-search input').value));
  $('#reader-rows').innerHTML=readerData.map(r=>`<tr><td>${esc(r.code)}</td><td>${esc(r.name)}</td><td>${esc(r.phone)||'—'}</td><td><button class="action" data-edit-reader="${r.id}">Sửa</button>${user.role==='admin'?`<button class="action danger" data-remove="readers/${r.id}">Ngừng</button>`:''}</td></tr>`).join('')||empty(4,'Không tìm thấy độc giả.');
 }else{
  const rows=await api('/loans?status='+$('#loan-status').value);
  $('#loan-rows').innerHTML=rows.map(l=>`<tr><td class="text-wrap"><b>${esc(l.title)}</b><small>#${l.id} · ${esc(l.book_code)}</small></td><td>${esc(l.name)}<small>${esc(l.reader_code)}</small></td><td>${l.borrowed_on}</td><td>${l.due_on}</td><td>${badge(l)}</td><td>${l.returned_on?`<small>Trả: ${l.returned_on}</small>`:`<button class="action" data-return="${l.id}">Trả sách</button>`}</td></tr>`).join('')||empty(6);
 }
}
function field(label,name,value='',extra=''){return `<label>${label}<input name="${name}" value="${esc(value)}" ${extra}></label>`;}
function editor(title,fields,save){$('#editor-title').textContent=title;$('#editor-fields').innerHTML=fields;$('#editor-error').textContent='';$('#editor-form').onsubmit=async event=>{event.preventDefault();const button=event.submitter;button.disabled=true;try{await save(Object.fromEntries(new FormData(event.target)));$('#editor').close();await refresh();notice('Đã lưu thay đổi.');}catch(e){$('#editor-error').textContent=e.message;}finally{button.disabled=false;}};$('#editor').showModal();}
function editBook(id){const b=bookData.find(x=>x.id===id)||{};editor(id?'Chỉnh sửa sách':'Thêm sách mới',field('Mã sách','code',b.code,'required maxlength="30"')+field('Tên sách','title',b.title,'required maxlength="200"')+field('Tác giả','author',b.author,'required maxlength="100"')+field('Thể loại','category',b.category,'required maxlength="60"')+field('Tổng số bản','total',b.total??1,'type="number" min="0" max="999" step="1" required'),data=>api('/books'+(id?'/'+id:''),id?'PUT':'POST',{...data,total:Number(data.total)}));}
function editReader(id){const r=readerData.find(x=>x.id===id)||{};editor(id?'Chỉnh sửa độc giả':'Thêm độc giả',field('Mã độc giả','code',r.code,'required maxlength="30"')+field('Họ và tên','name',r.name,'required maxlength="100"')+field('Điện thoại (không bắt buộc)','phone',r.phone,'maxlength="20" type="tel"'),data=>api('/readers'+(id?'/'+id:''),id?'PUT':'POST',data));}
async function newLoan(){const [books,readers]=await Promise.all([api('/books'),api('/readers')]);const available=books.filter(b=>b.available>0);if(!available.length||!readers.length){notice('Cần có sách còn bản và độc giả hoạt động trước khi lập phiếu.',true);return;}editor('Lập phiếu mượn',`<label>Độc giả<select name="reader_id" required>${readers.map(r=>`<option value="${r.id}">${esc(r.code+' · '+r.name)}</option>`).join('')}</select></label><label>Sách<select name="book_id" required>${available.map(b=>`<option value="${b.id}">${esc(b.code+' · '+b.title)} (còn ${b.available})</option>`).join('')}</select></label>`+field('Số ngày mượn','days',14,'type="number" min="1" max="30" step="1" required')+'<p class="hint">Một phiếu = một bản sách. Mỗi độc giả được giữ tối đa 5 bản. Hạn trả được tính từ ngày hôm nay.</p>',data=>api('/loans','POST',Object.fromEntries(Object.entries(data).map(([k,v])=>[k,Number(v)]))));}
$('#login-form').onsubmit=async e=>{e.preventDefault();e.submitter.disabled=true;$('#login-error').textContent='';try{await api('/login','POST',Object.fromEntries(new FormData(e.target)));e.target.reset();await enter();}catch(err){$('#login-error').textContent=err.message;}finally{e.submitter.disabled=false;}};
$('#logout').onclick=async()=>{try{await api('/logout','POST');showLogin();}catch(e){notice(e.message,true);}};
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;try{if(b.dataset.page)await navigate(b.dataset.page);if(b.dataset.editBook)editBook(Number(b.dataset.editBook));if(b.dataset.editReader)editReader(Number(b.dataset.editReader));if(b.dataset.remove&&confirm('Ngừng hoạt động bản ghi này? Lịch sử mượn trả vẫn được giữ.')){await api('/'+b.dataset.remove,'DELETE');await refresh();notice('Đã ngừng hoạt động bản ghi.');}if(b.dataset.return&&confirm('Xác nhận đã nhận lại sách của phiếu #'+b.dataset.return+'?')){b.disabled=true;const r=await api('/loans/'+b.dataset.return+'/return','POST');await refresh();notice(r.message+(r.overdue_days?' · Quá hạn '+r.overdue_days+' ngày.':'.'));}}catch(err){notice(err.message,true);}finally{b.disabled=false;}});
$('#add-book').onclick=()=>editBook();$('#add-reader').onclick=()=>editReader();
for(const id of ['#quick-borrow','#add-loan'])$(id).onclick=()=>newLoan().catch(e=>notice(e.message,true));
for(const id of ['#close-editor','#cancel-editor'])$(id).onclick=()=>$('#editor').close();
for(const id of ['#book-search','#reader-search'])$(id).onsubmit=e=>{e.preventDefault();refresh().catch(e=>notice(e.message,true));};
$('#loan-status').onchange=()=>refresh().catch(e=>notice(e.message,true));
enter().catch(showLogin);
