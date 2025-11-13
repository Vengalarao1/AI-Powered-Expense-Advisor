const API_BASE = 'http://localhost:8000';

// DOM Elements
let currentTab = 'dashboard';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing AI Expense Advisor...');
    initializeApp();
    setupEventListeners();
    loadDashboardData();
    loadSalary();
});

function initializeApp() {
    // Set active tab
    const navItem = document.querySelector(`[data-tab="${currentTab}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
    document.getElementById(currentTab).classList.add('active');
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const tab = this.getAttribute('data-tab');
            switchTab(tab);
        });
    });

    // Enter key for expense description
    document.getElementById('expenseDescription').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            categorizeExpense();
        }
    });
}

function switchTab(tabName) {
    console.log('Switching to tab:', tabName);
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const navItem = document.querySelector(`[data-tab="${tabName}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }

    // Update content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
        tab.style.display = 'none';
    });
    
    const tabElement = document.getElementById(tabName);
    if (tabElement) {
        tabElement.classList.add('active');
        tabElement.style.display = 'block';
    }

    currentTab = tabName;

    // Load tab-specific data
    switch(tabName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'budget':
            loadBudgetSuggestions();
            break;
        case 'predictions':
            loadPredictions();
            break;
    }
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        console.log(`Making API call to: ${API_BASE}${endpoint}`);
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showNotification('Error connecting to server. Make sure the Flask server is running.', 'error');
        throw error;
    }
}

// Expense Management
async function categorizeExpense() {
    const description = document.getElementById('expenseDescription').value.trim();
    
    if (!description) {
        showNotification('Please enter a description', 'warning');
        return;
    }

    try {
        const result = await apiCall('/categorize', {
            method: 'POST',
            body: JSON.stringify({ description })
        });

        document.getElementById('expenseCategory').value = result.category;
        
        // Show AI suggestion
        const suggestionEl = document.getElementById('aiSuggestion');
        const suggestionText = document.getElementById('suggestionText');
        const confidenceBadge = document.getElementById('confidenceBadge');
        
        suggestionText.textContent = `AI suggests: ${result.category}`;
        confidenceBadge.textContent = `${Math.round(result.confidence * 100)}% confident`;
        
        suggestionEl.classList.remove('hidden');
        
    } catch (error) {
        console.error('Categorization failed:', error);
    }
}

async function addExpense() {
    const description = document.getElementById('expenseDescription').value.trim();
    const amount = parseFloat(document.getElementById('expenseAmount').value);
    const category = document.getElementById('expenseCategory').value;

    if (!description || !amount || amount <= 0) {
        showNotification('Please fill all fields with valid values', 'warning');
        return;
    }

    try {
        await apiCall('/expenses', {
            method: 'POST',
            body: JSON.stringify({
                description,
                amount,
                category: category || 'Other'
            })
        });

        // Clear form
        document.getElementById('expenseDescription').value = '';
        document.getElementById('expenseAmount').value = '';
        document.getElementById('expenseCategory').value = '';
        document.getElementById('aiSuggestion').classList.add('hidden');

        showNotification('Expense added successfully!', 'success');
        
        // Refresh dashboard
        if (currentTab === 'dashboard') {
            loadDashboardData();
        }

    } catch (error) {
        console.error('Failed to add expense:', error);
    }
}

// Dashboard Functions
async function loadDashboardData() {
    try {
        console.log('Loading dashboard data...');
        const [expensesResponse, analyticsResponse] = await Promise.all([
            apiCall('/expenses'),
            apiCall('/analytics/categories')
        ]);

        updateDashboardStats(analyticsResponse);
        updateRecentExpenses(expensesResponse.expenses);
        renderSimpleCategoryChart(analyticsResponse);
        
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

function updateDashboardStats(analytics) {
    document.getElementById('totalSpent').textContent = `₹${analytics.total_spending?.toFixed(2) || '0'}`;
    document.getElementById('categoryCount').textContent = Object.keys(analytics.category_totals || {}).length;
    
    calculateRemainingBalance();
}

async function calculateRemainingBalance() {
    try {
        const salaryResponse = await apiCall('/salary');
        const salary = salaryResponse.monthly_salary || 0;
        
        const analyticsResponse = await apiCall('/analytics/categories');
        const currentMonthSpending = analyticsResponse.total_spending || 0;
        
        const remaining = salary - currentMonthSpending;
        
        const remainingEl = document.getElementById('remainingBalance');
        remainingEl.textContent = `₹${remaining.toFixed(2)}`;
        
        if (remaining < 0) {
            remainingEl.classList.add('negative');
        } else {
            remainingEl.classList.remove('negative');
        }
    } catch (error) {
        console.error('Failed to calculate remaining balance:', error);
    }
}

function updateRecentExpenses(expenses) {
    const container = document.getElementById('recentExpensesList');
    const recentExpenses = expenses.slice(0, 5);

    if (recentExpenses.length === 0) {
        container.innerHTML = '<p class="no-data">No expenses yet. Add your first expense!</p>';
        return;
    }

    container.innerHTML = recentExpenses.map(expense => `
        <div class="expense-item">
            <div class="expense-info">
                <div class="expense-desc">${escapeHtml(expense.description)}</div>
                <div class="expense-meta">
                    ${expense.category} • ${new Date(expense.date).toLocaleDateString()}
                </div>
            </div>
            <div class="expense-amount">₹${expense.amount.toFixed(2)}</div>
        </div>
    `).join('');
}

// Simple chart using HTML/CSS instead of Plotly
function renderSimpleCategoryChart(analytics) {
    const container = document.getElementById('categoryChart');
    const categories = Object.keys(analytics.category_totals || {});
    const amounts = Object.values(analytics.category_totals || {});
    
    if (categories.length === 0) {
        container.innerHTML = '<p class="no-data">No data available for chart</p>';
        return;
    }

    const total = amounts.reduce((sum, amount) => sum + amount, 0);
    
    const chartHTML = `
        <div class="simple-chart">
            <h3>Spending by Category</h3>
            <div class="chart-bars">
                ${categories.map((category, index) => {
                    const amount = amounts[index];
                    const percentage = total > 0 ? (amount / total * 100) : 0;
                    const colors = ['#4361ee', '#7209b7', '#4cc9f0', '#f8961e', '#f72585', '#3a0ca3'];
                    const color = colors[index % colors.length];
                    
                    return `
                    <div class="chart-bar-container">
                        <div class="chart-bar-label">${category}</div>
                        <div class="chart-bar">
                            <div class="chart-bar-fill" style="width: ${percentage}%; background-color: ${color};"></div>
                        </div>
                        <div class="chart-bar-value">₹${amount.toFixed(2)} (${percentage.toFixed(1)}%)</div>
                    </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = chartHTML;
}

// Analytics Functions
async function loadAnalytics() {
    try {
        const [monthlyResponse, categoriesResponse] = await Promise.all([
            apiCall('/analytics/monthly'),
            apiCall('/analytics/categories')
        ]);

        renderSimpleMonthlyTrend(monthlyResponse.monthly_data);
        renderSimpleCategoryBreakdown(categoriesResponse.category_totals);
        
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

function renderSimpleMonthlyTrend(monthlyData) {
    const container = document.getElementById('monthlyTrendChart');
    const months = Object.keys(monthlyData || {}).reverse();
    
    if (months.length === 0) {
        container.innerHTML = '<p class="no-data">No monthly data available</p>';
        return;
    }

    const categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare'];
    const colors = ['#4361ee', '#7209b7', '#4cc9f0', '#f8961e', '#f72585', '#3a0ca3'];
    
    let html = `
        <div class="simple-chart">
            <h3>Monthly Spending Trend</h3>
            <div class="monthly-trend">
    `;
    
    months.forEach(month => {
        const monthData = monthlyData[month];
        const monthTotal = Object.values(monthData || {}).reduce((sum, amount) => sum + amount, 0);
        
        html += `
            <div class="month-row">
                <div class="month-label">${month}</div>
                <div class="month-bars">
                    ${categories.map((category, index) => {
                        const amount = monthData?.[category] || 0;
                        const percentage = monthTotal > 0 ? (amount / monthTotal * 100) : 0;
                        return `
                        <div class="month-category-bar" style="width: ${percentage}%; background-color: ${colors[index]};" 
                             title="${category}: ₹${amount.toFixed(2)}">
                        </div>
                        `;
                    }).join('')}
                </div>
                <div class="month-total">₹${monthTotal.toFixed(2)}</div>
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="chart-legend">
                ${categories.map((category, index) => `
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: ${colors[index]}"></span>
                        <span class="legend-label">${category}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function renderSimpleCategoryBreakdown(categoryTotals) {
    const container = document.getElementById('categoryBreakdownChart');
    const categories = Object.keys(categoryTotals || {});
    const amounts = Object.values(categoryTotals || {});
    
    if (categories.length === 0) {
        container.innerHTML = '<p class="no-data">No category data available</p>';
        return;
    }

    // Sort by amount (descending)
    const sortedData = categories.map((category, index) => ({
        category,
        amount: amounts[index]
    })).sort((a, b) => b.amount - a.amount);

    const maxAmount = Math.max(...amounts);
    
    const html = `
        <div class="simple-chart">
            <h3>Spending by Category</h3>
            <div class="breakdown-chart">
                ${sortedData.map(item => {
                    const percentage = maxAmount > 0 ? (item.amount / maxAmount * 100) : 0;
                    return `
                    <div class="breakdown-row">
                        <div class="breakdown-label">${item.category}</div>
                        <div class="breakdown-bar-container">
                            <div class="breakdown-bar" style="width: ${percentage}%;"></div>
                        </div>
                        <div class="breakdown-value">₹${item.amount.toFixed(2)}</div>
                    </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Budget Suggestions
async function loadBudgetSuggestions() {
    try {
        const response = await apiCall('/budget/suggestions');
        renderBudgetSuggestions(response.suggestions);
    } catch (error) {
        console.error('Failed to load budget suggestions:', error);
    }
}

function renderBudgetSuggestions(suggestions) {
    const container = document.getElementById('budgetSuggestions');
    
    if (!suggestions || suggestions.length === 0) {
        container.innerHTML = '<p class="no-data">No budget suggestions available</p>';
        return;
    }

    // Update salary display in budget header
    const salary = document.getElementById('monthlySalary').textContent;
    document.getElementById('budgetSalaryDisplay').textContent = `Salary: ${salary}`;

    container.innerHTML = suggestions.map(suggestion => {
        // create a safe category class (lowercase, non-alnum -> dash)
        const catClass = 'category-' + (suggestion.category || 'other')
            .toString()
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-');

        // Special styling for summary card
        const isSummary = suggestion.category === "Monthly Summary";
        const summaryClass = isSummary ? 'summary-card' : '';
        
        // Calculate percentage for progress bar (except for summary)
        const percentage = !isSummary && suggestion.budget_limit > 0 ? 
            Math.min((suggestion.current_spending / suggestion.budget_limit) * 100, 100) : 0;
        
        return `
        <div class="suggestion-card ${suggestion.status} ${catClass} ${summaryClass}">
            <div class="suggestion-header">
                <span class="suggestion-category">${suggestion.category}</span>
                ${!isSummary ? `
                <span class="suggestion-percentage">
                    ${Math.round(percentage)}%
                </span>
                ` : ''}
            </div>
            <div class="suggestion-amount ${suggestion.status}">
                ₹${suggestion.current_spending.toFixed(2)} / ₹${suggestion.budget_limit.toFixed(2)}
            </div>
            <div class="suggestion-text">
                ${suggestion.suggestion}
            </div>
            ${!isSummary ? `
            <div class="budget-progress">
                <div class="progress-bar ${suggestion.status}" 
                     style="width: ${percentage}%">
                </div>
            </div>
            ` : ''}
        </div>
    `;
    }).join('');
}

// Predictions
async function loadPredictions() {
    try {
        const response = await apiCall('/predict/next-month');
        renderPrediction(response.prediction);
    } catch (error) {
        console.error('Failed to load predictions:', error);
    }
}

function renderPrediction(prediction) {
    const container = document.getElementById('predictionContent');
    
    if (!prediction || prediction.predicted_amount === 0) {
        container.innerHTML = '<p>Not enough data to make predictions. Add more expenses to enable AI predictions.</p>';
        return;
    }

    container.innerHTML = `
        <div class="prediction-metric">
            <strong>Predicted Amount:</strong> ₹${prediction.predicted_amount}
        </div>
        <div class="prediction-metric">
            <strong>Confidence:</strong> ${prediction.confidence}
        </div>
        <div class="prediction-metric">
            <strong>Trend:</strong> ${prediction.trend}
        </div>
    `;
}

// Export
async function exportCSV() {
    try {
        const response = await fetch(`${API_BASE}/export/csv`);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `expenses_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('CSV exported successfully!', 'success');
    } catch (error) {
        console.error('Export failed:', error);
        showNotification('Export failed', 'error');
    }
}

// Salary management
async function loadSalary() {
    try {
        const response = await apiCall('/salary');
        const salary = response.monthly_salary || 0;
        document.getElementById('monthlySalary').textContent = `₹${salary.toFixed(2)}`;
    } catch (error) {
        console.error('Failed to load salary:', error);
    }
}

function openSalaryModal() {
    const salary = prompt('Enter your monthly salary (₹):', '25000');
    if (salary !== null && salary !== '') {
        setSalary(parseFloat(salary));
    }
}

async function setSalary(amount) {
    if (!amount || amount < 0) {
        showNotification('Please enter a valid salary amount', 'warning');
        return;
    }

    try {
        const response = await apiCall('/salary', {
            method: 'POST',
            body: JSON.stringify({ monthly_salary: amount })
        });

        document.getElementById('monthlySalary').textContent = `₹${response.monthly_salary.toFixed(2)}`;
        showNotification(`Salary set to ₹${response.monthly_salary.toFixed(2)}`, 'success');
        
        // Refresh data
        calculateRemainingBalance();
        if (currentTab === 'dashboard') {
            loadDashboardData();
        }
        if (currentTab === 'budget') {
            loadBudgetSuggestions();
        }
    } catch (error) {
        console.error('Failed to set salary:', error);
    }
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        document.body.removeChild(notification);
    }, 3000);
}

function getNotificationColor(type) {
    const colors = {
        success: '#4cc9f0',
        error: '#f72585',
        warning: '#f8961e',
        info: '#4361ee'
    };
    return colors[type] || '#4361ee';
}