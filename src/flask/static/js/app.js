'use strict';

const API_BASE = location.origin;
const $list = document.getElementById('list');
const $tpl = document.getElementById('itemTpl');
const $refresh = document.getElementById('refreshBtn');
const $add = document.getElementById('addBtn');
const $time = document.getElementById('timeInput');
const $msg = document.getElementById('msgInput');

async function fetchJSON(url, options){
  const res = await fetch(url, options);
  if(!res.ok) throw new Error('HTTP '+res.status);
  return await res.json();
}

function render(items){
  $list.innerHTML = '';
  for(const it of items){
    const li = $tpl.content.firstElementChild.cloneNode(true);
    li.querySelector('.time').textContent = it.time;
    li.querySelector('.content').textContent = it.message;
    // 携带但不显示 group_id / message_id
    li.dataset.groupId = it.group_id;
    li.dataset.messageId = it.message_id;
    li.querySelector('.delete').addEventListener('click', async () => {
      if(!confirm('确认删除？')) return;
      try{
        await fetchJSON(`${API_BASE}/api/messages`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ group_id: li.dataset.groupId, message_id: li.dataset.messageId })
        });
        await load();
      }catch(err){
        alert('删除失败: '+err.message);
      }
    });
    $list.appendChild(li);
  }
}

async function load(){
  try{
    const data = await fetchJSON(`${API_BASE}/api/messages`);
    render(data.items || []);
  }catch(err){
    $list.innerHTML = `<li class="item">加载失败：${err.message}</li>`;
  }
}

$refresh.addEventListener('click', load);

document.addEventListener('DOMContentLoaded', load);

$add.addEventListener('click', async () => {
  const time = ($time.value || '').trim();
  const message = ($msg.value || '').trim();
  if(!time || !message){
    alert('请填写时间与内容');
    return;
  }
  try{
    await fetchJSON(`${API_BASE}/api/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time, message })
    });
    $msg.value = '';
    await load();
  }catch(err){
    alert('添加失败：'+err.message);
  }
});


