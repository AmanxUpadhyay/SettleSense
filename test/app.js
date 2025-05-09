// SettleSense App with IndexedDB CRUD
const DB_NAME = 'settleSenseDB';
const DB_VERSION = 1;
const STORE_NAME = 'entries';

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function addEntry(entry) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.add(entry);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function getAllEntries() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.getAll();
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function deleteEntry(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.delete(id);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

async function updateEntry(entry) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.put(entry);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

// UI Logic
const form = document.querySelector('.entry-form');
const activityList = document.querySelector('.activity-list');
const netBalanceEl = document.querySelector('.balance');

function getAvatar(name, type) {
  if (type === 'owe') {
    return 'https://img.icons8.com/color/48/000000/person-female.png';
  } else {
    return 'https://img.icons8.com/color/48/000000/person-male.png';
  }
}

function renderEntries(entries) {
  let net = 0;
  activityList.innerHTML = '';
  entries.forEach(entry => {
    const item = document.createElement('div');
    item.className = 'activity-item ' + (entry.type === 'owe' ? 'owe' : 'they-owe');
    item.innerHTML = `
      <img class="avatar-img" src="${getAvatar(entry.name, entry.type)}" alt="${entry.name} avatar" />
      <div class="activity-info">
        <span class="name">${entry.name}</span>
        <span class="desc">${entry.note || ''}</span>
      </div>
      <div class="activity-amount ${entry.type}">
        ${entry.type === 'owe' ? 'You owe' : 'They owe'} £${entry.amount}
      </div>
      <button class="edit-btn" title="Edit">✏️</button>
      <button class="delete-btn" title="Delete">🗑️</button>
    `;
    // Delete
    item.querySelector('.delete-btn').onclick = async () => {
      if (confirm('Are you sure you want to delete this entry?')) {
        await deleteEntry(entry.id);
        loadEntries();
      }
    };
    // Edit (open popup)
    item.querySelector('.edit-btn').onclick = () => openEditPopup(entry);
    activityList.appendChild(item);
    net += entry.type === 'owe' ? -Number(entry.amount) : Number(entry.amount);
  });
  // Piggy illustration
  const piggy = document.createElement('div');
  piggy.className = 'piggy-illustration';
  piggy.innerHTML = '<img src="pig.png" alt="Piggy Bank Mascot">';
  activityList.appendChild(piggy);
  // Net balance
  netBalanceEl.textContent = (net >= 0 ? '£ ' : '-£ ') + Math.abs(net);
  netBalanceEl.className = 'balance ' + (net >= 0 ? 'positive' : 'negative');
}

// Popup for editing
function openEditPopup(entry) {
  // Create overlay
  let overlay = document.createElement('div');
  overlay.className = 'popup-overlay';
  overlay.innerHTML = `
    <div class="popup-window">
      <h2 class="popup-title">Edit Entry</h2>
      <form class="popup-form">
        <label>Name</label>
        <input type="text" class="edit-name" value="${entry.name}" required>
        <label>Note</label>
        <input type="text" class="edit-note" value="${entry.note || ''}">
        <label>Type</label>
        <select class="edit-type">
          <option value="owe" ${entry.type === 'owe' ? 'selected' : ''}>You owe</option>
          <option value="they-owe" ${entry.type === 'they-owe' ? 'selected' : ''}>They owe</option>
        </select>
        <label>Amount</label>
        <input type="number" class="edit-amount" value="${entry.amount}" min="0" step="0.01" required>
        <div class="popup-actions">
          <button type="submit" class="save-btn">Save</button>
          <button type="button" class="cancel-btn">Cancel</button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(overlay);
  // Focus first input
  overlay.querySelector('.edit-name').focus();
  // Save
  overlay.querySelector('.popup-form').onsubmit = async (e) => {
    e.preventDefault();
    if (confirm('Are you sure you want to update this entry?')) {
      const newName = overlay.querySelector('.edit-name').value.trim();
      const newNote = overlay.querySelector('.edit-note').value.trim();
      const newType = overlay.querySelector('.edit-type').value;
      const newAmount = overlay.querySelector('.edit-amount').value.trim();
      if (!newName || !newAmount) return alert('Name and amount required!');
      await updateEntry({ id: entry.id, name: newName, note: newNote, type: newType, amount: newAmount });
      document.body.removeChild(overlay);
      loadEntries();
    }
  };
  // Cancel
  overlay.querySelector('.cancel-btn').onclick = () => {
    document.body.removeChild(overlay);
  };
  // Close on overlay click (not popup)
  overlay.onclick = (e) => {
    if (e.target === overlay) document.body.removeChild(overlay);
  };
}

async function loadEntries() {
  const entries = await getAllEntries();
  renderEntries(entries);
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  // Read type before any UI changes
  const type = document.getElementById('oweBtn').classList.contains('active') ? 'owe' : 'they-owe';
  const name = form.querySelector('.name-input').value.trim();
  const amount = form.querySelector('.money-input').value.trim();
  const noteInput = form.querySelector('.note-input');
  const note = noteInput.value.trim();
  if (!name || !amount) return;
  await addEntry({ name, amount, note, type });
  form.reset();
  document.getElementById('oweBtn').classList.add('active');
  document.getElementById('theyOweBtn').classList.remove('active');
  noteInput.blur(); // Blur note input to prevent accidental double submit
  loadEntries();
});

document.getElementById('oweBtn').addEventListener('click', () => {
  document.getElementById('oweBtn').classList.add('active');
  document.getElementById('theyOweBtn').classList.remove('active');
});
document.getElementById('theyOweBtn').addEventListener('click', () => {
  document.getElementById('theyOweBtn').classList.add('active');
  document.getElementById('oweBtn').classList.remove('active');
});

window.addEventListener('DOMContentLoaded', loadEntries);
