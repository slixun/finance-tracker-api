const API_BASE = 'http://127.0.0.1:8000/api/v1';
const TOKEN_KEY = 'financeTrackerToken';
const USER_KEY = 'financeTrackerUser';

let authMode = 'login';
let accessToken = localStorage.getItem(TOKEN_KEY);
let currentUser = localStorage.getItem(USER_KEY);
let wallets = [];
let operations = [];

const currencySymbols = {
    kzt: 'KZT',
    usd: 'USD',
    eur: 'EUR',
    rub: 'RUB',
    btc: 'BTC'
};

document.addEventListener('DOMContentLoaded', () => {
    bindModalResets();
    setAuthMode('login');

    if (accessToken) {
        loadCurrentUser();
    }
});

function authHeaders(extra = {}) {
    return {
        ...extra,
        Authorization: `Bearer ${accessToken}`
    };
}

function setAuthMode(mode) {
    authMode = mode;
    document.getElementById('loginTab').classList.toggle('active', mode === 'login');
    document.getElementById('registerTab').classList.toggle('active', mode === 'register');
    document.getElementById('authSubmit').textContent = mode === 'login' ? 'Sign in' : 'Create account';
}

async function submitAuth(event) {
    event.preventDefault();

    const username = document.getElementById('authLogin').value.trim();
    const password = document.getElementById('authPassword').value;

    if (!username || !password) {
        showToast('Missing fields', 'Enter both login and password.', true);
        return;
    }

    if (authMode === 'register') {
        await register(username, password);
        return;
    }

    await login(username, password);
}

async function register(login, password) {
    try {
        const response = await apiFetch('/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login, password })
        }, false);

        if (!response.ok) {
            showToast('Registration failed', await responseMessage(response), true);
            return;
        }

        showToast('Account created', 'You can now sign in with your password.');
        setAuthMode('login');
    } catch {
        showToast('Connection error', 'Could not reach the API.', true);
    }
}

async function login(login, password) {
    const formData = new URLSearchParams();
    formData.set('username', login);
    formData.set('password', password);

    try {
        const response = await apiFetch('/users/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        }, false);

        if (!response.ok) {
            showToast('Sign in failed', await responseMessage(response), true);
            return;
        }

        const data = await response.json();
        accessToken = data.access_token;
        localStorage.setItem(TOKEN_KEY, accessToken);
        await loadCurrentUser();
    } catch {
        showToast('Connection error', 'Could not reach the API.', true);
    }
}

async function loadCurrentUser() {
    const response = await apiFetch('/users/me');

    if (!response.ok) {
        logout(false);
        return;
    }

    const user = await response.json();
    currentUser = user.login;
    localStorage.setItem(USER_KEY, currentUser);
    showDashboard();
}

function showDashboard() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    document.getElementById('currentUser').textContent = currentUser;
    loadAllData();
}

function logout(showMessage = true) {
    accessToken = null;
    currentUser = null;
    wallets = [];
    operations = [];
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    document.getElementById('authSection').style.display = 'grid';
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('authPassword').value = '';
    if (showMessage) showToast('Signed out', 'Your local session was cleared.');
}

async function loadAllData() {
    await loadWallets();
    await loadOperations();
    await loadTotalBalance();
    updateWalletSelects();
}

async function apiFetch(path, options = {}, includeAuth = true) {
    const headers = includeAuth ? authHeaders(options.headers || {}) : (options.headers || {});
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

    if (response.status === 401 && includeAuth) {
        logout(false);
        showToast('Session expired', 'Please sign in again.', true);
    }

    return response;
}

async function responseMessage(response) {
    const data = await response.json().catch(() => ({}));

    if (Array.isArray(data.detail)) {
        return data.detail.map(item => item.msg).join(' ');
    }

    return data.detail || 'Something went wrong.';
}

async function loadWallets() {
    const response = await apiFetch('/wallets');

    if (!response.ok) {
        wallets = [];
        renderWallets();
        return;
    }

    wallets = (await response.json()).map(normalizeWallet);
    renderWallets();
    updateWalletSelects();
}

async function loadOperations() {
    const params = new URLSearchParams();
    const walletId = document.getElementById('filterWallet')?.value;
    const dateFrom = document.getElementById('filterDateFrom')?.value;
    const dateTo = document.getElementById('filterDateTo')?.value;

    if (walletId) params.set('wallet_id', walletId);
    if (dateFrom) params.set('date_from', `${dateFrom}T00:00:00`);
    if (dateTo) params.set('date_to', `${dateTo}T23:59:59`);

    const query = params.toString() ? `?${params}` : '';
    const response = await apiFetch(`/operations${query}`);

    if (!response.ok) {
        operations = [];
        renderOperations();
        return;
    }

    operations = (await response.json()).map(normalizeOperation);
    renderOperations();
}

async function loadTotalBalance() {
    const response = await apiFetch('/balance');
    const totalBalance = document.getElementById('totalBalance');

    if (!response.ok) {
        totalBalance.textContent = '0.00 KZT';
        return;
    }

    const data = await response.json();
    totalBalance.textContent = `${formatAmount(data.total_balance)} KZT`;
}

function normalizeWallet(wallet) {
    return {
        ...wallet,
        balance: Number(wallet.balance || 0),
        currency: String(wallet.currency || '').toLowerCase()
    };
}

function normalizeOperation(operation) {
    return {
        ...operation,
        amount: Number(operation.amount || 0),
        new_balance: Number(operation.new_balance || 0),
        currency: String(operation.currency || '').toLowerCase()
    };
}

function renderWallets() {
    document.getElementById('walletCount').textContent = wallets.length;
    const host = document.getElementById('walletList');

    if (!wallets.length) {
        host.innerHTML = '<div class="empty-state">No wallets yet. Add one to start tracking money.</div>';
        return;
    }

    host.innerHTML = wallets.map(wallet => `
        <article class="wallet-item">
            <div>
                <strong>${escapeHtml(wallet.name)}</strong>
                <span>${currencyLabel(wallet.currency)}</span>
            </div>
            <div class="wallet-balance">
                <strong>${formatAmount(wallet.balance)}</strong>
                <span>${currencyLabel(wallet.currency)}</span>
            </div>
            <div class="wallet-actions">
                <button class="btn btn-outline-secondary btn-sm" type="button" onclick="editWallet(${wallet.id})">
                    Edit
                </button>
                <button class="btn btn-outline-danger btn-sm" type="button" onclick="deleteWallet(${wallet.id})">
                    Delete
                </button>
            </div>
        </article>
    `).join('');
}

function renderOperations() {
    document.getElementById('operationCount').textContent = operations.length;
    const tbody = document.getElementById('operationsTable');

    if (!operations.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-row">No operations found.</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = operations
        .slice()
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .map(operation => {
            const wallet = wallets.find(item => item.id === operation.wallet_id);
            const typeClass = operation.type === 'income'
                ? 'type-income'
                : operation.type === 'expense'
                    ? 'type-expense'
                    : 'type-transfer';

            return `
                <tr>
                    <td>${formatDate(operation.created_at)}</td>
                    <td><span class="type-pill ${typeClass}">${operation.type}</span></td>
                    <td>${escapeHtml(wallet?.name || 'Unknown')}</td>
                    <td>${escapeHtml(operation.category || '-')}</td>
                    <td class="text-end">${formatAmount(operation.amount)} ${currencyLabel(operation.currency)}</td>
                    <td class="text-end">${formatAmount(operation.new_balance)} ${currencyLabel(operation.currency)}</td>
                </tr>
            `;
        }).join('');
}

function updateWalletSelects() {
    const walletOptions = wallets.map(wallet => `
        <option value="${wallet.id}">
            ${escapeHtml(wallet.name)} - ${formatAmount(wallet.balance)} ${currencyLabel(wallet.currency)}
        </option>
    `).join('');
    const emptyOption = '<option value="">No wallets available</option>';

    ['incomeWallet', 'expenseWallet', 'transferFrom', 'transferTo', 'interestWallet'].forEach(id => {
        const select = document.getElementById(id);
        if (select) select.innerHTML = wallets.length ? walletOptions : emptyOption;
    });

    const filterWallet = document.getElementById('filterWallet');
    if (filterWallet) {
        const selected = filterWallet.value;
        filterWallet.innerHTML = `<option value="">All wallets</option>${walletOptions}`;
        filterWallet.value = selected;
    }
}

async function saveWallet() {
    const id = document.getElementById('walletId').value;
    const name = document.getElementById('walletName').value.trim();
    const currency = document.getElementById('walletCurrency').value;
    const balance = Number(document.getElementById('walletBalance').value || 0);

    if (!name) {
        showToast('Missing name', 'Enter a wallet name.', true);
        return;
    }

    const path = id ? `/wallets/${id}` : '/wallets';
    const method = id ? 'PUT' : 'POST';
    const body = id
        ? { name, balance }
        : { name, currency, initial_balance: balance };

    const response = await apiFetch(path, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    if (!response.ok) {
        showToast('Wallet error', await responseMessage(response), true);
        return;
    }

    closeModal('walletModal');
    showToast('Wallet saved', id ? 'Wallet updated.' : 'Wallet created.');
    await loadAllData();
}

function editWallet(id) {
    const wallet = wallets.find(item => item.id === id);
    if (!wallet) return;

    document.getElementById('walletId').value = wallet.id;
    document.getElementById('walletName').value = wallet.name;
    document.getElementById('walletCurrency').value = wallet.currency;
    document.getElementById('walletCurrency').disabled = true;
    document.getElementById('walletBalance').value = wallet.balance;
    document.getElementById('walletSubmit').textContent = 'Update wallet';
    document.querySelector('#walletModal .modal-title').textContent = 'Edit wallet';
    bootstrap.Modal.getOrCreateInstance(document.getElementById('walletModal')).show();
}

async function deleteWallet(id) {
    const wallet = wallets.find(item => item.id === id);
    if (!wallet) return;

    if (!confirm(`Delete wallet "${wallet.name}"?`)) return;

    const response = await apiFetch(`/wallets/${id}`, { method: 'DELETE' });

    if (!response.ok) {
        showToast('Delete failed', await responseMessage(response), true);
        return;
    }

    showToast('Wallet deleted', 'The wallet was removed.');
    await loadAllData();
}

async function addOperation(type) {
    const prefix = type === 'income' ? 'income' : 'expense';
    const walletId = Number(document.getElementById(`${prefix}Wallet`).value);
    const amount = Number(document.getElementById(`${prefix}Amount`).value || 0);
    const description = document.getElementById(`${prefix}Description`).value.trim();
    const wallet = wallets.find(item => item.id === walletId);

    if (!wallet) {
        showToast('No wallet selected', 'Choose a wallet first.', true);
        return;
    }

    if (amount <= 0) {
        showToast('Invalid amount', 'Amount must be greater than zero.', true);
        return;
    }

    const response = await apiFetch(`/operations/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            wallet_name: wallet.name,
            amount,
            description: description || type
        })
    });

    if (!response.ok) {
        showToast('Operation failed', await responseMessage(response), true);
        return;
    }

    closeModal(`${prefix}Modal`);
    showToast('Operation saved', `${capitalize(type)} added.`);
    await loadAllData();
}

async function transferMoney() {
    const fromWalletId = Number(document.getElementById('transferFrom').value);
    const toWalletId = Number(document.getElementById('transferTo').value);
    const amount = Number(document.getElementById('transferAmount').value || 0);

    if (fromWalletId === toWalletId) {
        showToast('Invalid transfer', 'Choose two different wallets.', true);
        return;
    }

    if (amount <= 0) {
        showToast('Invalid amount', 'Amount must be greater than zero.', true);
        return;
    }

    const response = await apiFetch('/operations/transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            from_wallet_id: fromWalletId,
            to_wallet_id: toWalletId,
            amount
        })
    });

    if (!response.ok) {
        showToast('Transfer failed', await responseMessage(response), true);
        return;
    }

    closeModal('transferModal');
    showToast('Transfer complete', 'Balances were updated.');
    await loadAllData();
}

async function calculateWalletInterest() {
    const walletId = document.getElementById('interestWallet').value;
    const months = Number(document.getElementById('interestMonths').value || 1);

    if (!walletId) {
        showToast('No wallet selected', 'Choose a wallet first.', true);
        return;
    }

    const response = await apiFetch(`/interest/${walletId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_in_months: months })
    });

    if (!response.ok) {
        showToast('Interest error', await responseMessage(response), true);
        return;
    }

    const result = await response.json();
    document.getElementById('singleInterestResult').innerHTML = interestCard(result);
}

async function calculateAllInterest(source = 'quick') {
    const fieldId = source === 'modal' ? 'interestMonths' : 'quickInterestMonths';
    const months = Number(document.getElementById(fieldId)?.value || 1);

    const response = await apiFetch('/interest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_in_months: months })
    });

    if (!response.ok) {
        showToast('Interest error', await responseMessage(response), true);
        return;
    }

    const data = await response.json();
    const rows = data.wallet_interest_list.length
        ? data.wallet_interest_list.map(interestCard).join('')
        : '<div class="empty-state">No KZT or USD wallets are eligible for interest.</div>';

    document.getElementById('interestResults').innerHTML = `
        <div class="interest-total">Total interest: ${formatAmount(data.total_interest)} KZT</div>
        ${rows}
    `;
    showToast('Interest calculated', 'The forecast was updated.');
}

function interestCard(result) {
    const wallet = wallets.find(item => item.id === result.wallet_id);
    const currency = currencyLabel(result.currency);

    return `
        <div class="interest-card">
            <strong>${escapeHtml(wallet?.name || `Wallet ${result.wallet_id}`)}</strong>
            <span>Interest: ${formatAmount(result.interest)} ${currency}</span>
            <span>New balance: ${formatAmount(result.new_balance)} ${currency}</span>
        </div>
    `;
}

function resetFilters() {
    document.getElementById('filterWallet').value = '';
    document.getElementById('filterDateFrom').value = '';
    document.getElementById('filterDateTo').value = '';
    loadOperations();
}

function bindModalResets() {
    document.getElementById('walletModal').addEventListener('hidden.bs.modal', () => {
        document.getElementById('walletId').value = '';
        document.getElementById('walletName').value = '';
        document.getElementById('walletCurrency').value = 'kzt';
        document.getElementById('walletCurrency').disabled = false;
        document.getElementById('walletBalance').value = '0';
        document.getElementById('walletSubmit').textContent = 'Create wallet';
        document.querySelector('#walletModal .modal-title').textContent = 'Add wallet';
    });

    ['income', 'expense'].forEach(prefix => {
        document.getElementById(`${prefix}Modal`).addEventListener('hidden.bs.modal', () => {
            document.getElementById(`${prefix}Amount`).value = '';
            document.getElementById(`${prefix}Description`).value = '';
        });
    });

    document.getElementById('transferModal').addEventListener('hidden.bs.modal', () => {
        document.getElementById('transferAmount').value = '';
    });

    ['incomeModal', 'expenseModal', 'transferModal', 'interestModal'].forEach(id => {
        document.getElementById(id).addEventListener('show.bs.modal', updateWalletSelects);
    });
}

function closeModal(id) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(id));
    if (modal) modal.hide();
}

function showToast(title, message, isError = false) {
    const toastEl = document.getElementById('toastNotification');
    document.getElementById('toastTitle').textContent = title;
    document.getElementById('toastBody').textContent = message;
    toastEl.classList.toggle('toast-error', isError);
    bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3200 }).show();
}

function formatAmount(value) {
    return Number(value || 0).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8
    });
}

function formatDate(value) {
    return new Date(value).toLocaleString('en-US', {
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function currencyLabel(currency) {
    return currencySymbols[String(currency || '').toLowerCase()] || String(currency || '').toUpperCase();
}

function capitalize(value) {
    return value.charAt(0).toUpperCase() + value.slice(1);
}

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}
