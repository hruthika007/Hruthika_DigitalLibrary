/**
 * Digital Library & E-Book Circulation Portal
 * Client-Side Interactivity, Instant Search, Due-Date & Fine Calculator
 */

document.addEventListener('DOMContentLoaded', function () {
    initCatalogSearch();
    initIssueFormCalculator();
    initReturnFineCalculator();
    initStandaloneCalculator();
    initTableQuickSearch();
});

/**
 * 1. JavaScript Instant Search & Filter for Book Catalog
 */
function initCatalogSearch() {
    const searchInput = document.getElementById('catalog-search');
    const bookGrid = document.getElementById('books-grid');
    if (!bookGrid) return;

    const bookCards = Array.from(bookGrid.querySelectorAll('.book-card-col'));
    const countDisplay = document.getElementById('books-count-display');
    const noResultsMsg = document.getElementById('no-books-found');
    const clearBtn = document.getElementById('clear-search-btn');
    const genrePills = document.querySelectorAll('.genre-filter-pill');
    const stockFilterSelect = document.getElementById('stock-filter-select');

    let currentGenre = 'all';
    let currentStock = 'all';

    function filterBooks() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        let visibleCount = 0;

        bookCards.forEach(col => {
            const title = col.getAttribute('data-title') || '';
            const author = col.getAttribute('data-author') || '';
            const genre = col.getAttribute('data-genre') || '';
            const isbn = col.getAttribute('data-isbn') || '';
            const isAvailable = col.getAttribute('data-available') === 'true';

            // Check search text query across title, author, genre, ISBN
            const matchesQuery = !query || 
                title.includes(query) || 
                author.includes(query) || 
                genre.toLowerCase().includes(query) || 
                isbn.includes(query);

            // Check genre pill filter
            const matchesGenre = (currentGenre === 'all') || (genre.toLowerCase() === currentGenre.toLowerCase());

            // Check stock availability
            let matchesStock = true;
            if (currentStock === 'in_stock') {
                matchesStock = isAvailable;
            } else if (currentStock === 'out_of_stock') {
                matchesStock = !isAvailable;
            }

            if (matchesQuery && matchesGenre && matchesStock) {
                col.style.display = '';
                visibleCount++;
            } else {
                col.style.display = 'none';
            }
        });

        if (countDisplay) {
            countDisplay.textContent = `Showing ${visibleCount} of ${bookCards.length} books`;
        }

        if (noResultsMsg) {
            noResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }

        if (clearBtn) {
            clearBtn.style.display = query.length > 0 ? 'inline-block' : 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterBooks);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            if (searchInput) searchInput.value = '';
            filterBooks();
            if (searchInput) searchInput.focus();
        });
    }

    if (stockFilterSelect) {
        stockFilterSelect.addEventListener('change', function () {
            currentStock = this.value;
            filterBooks();
        });
    }

    genrePills.forEach(pill => {
        pill.addEventListener('click', function (e) {
            e.preventDefault();
            genrePills.forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            currentGenre = this.getAttribute('data-genre') || 'all';
            filterBooks();
        });
    });

    // Run initial filter in case params are preset
    filterBooks();
}

/**
 * 2. Interactive Due-Date Calculator on Book Issue Workflow
 * Automatically sets and previews due date to +14 days from issue date.
 */
function initIssueFormCalculator() {
    const issueDateInput = document.getElementById('issue-date-input');
    const dueDateInput = document.getElementById('due-date-input');
    const previewDueDateBadge = document.getElementById('preview-due-date-badge');

    if (!issueDateInput || !dueDateInput) return;

    function updateDueDate() {
        if (!issueDateInput.value) return;

        const parts = issueDateInput.value.split('-');
        if (parts.length === 3) {
            const issueDate = new Date(parts[0], parts[1] - 1, parts[2]);
            const dueDate = new Date(issueDate);
            dueDate.setDate(dueDate.getDate() + 14);

            const yyyy = dueDate.getFullYear();
            const mm = String(dueDate.getMonth() + 1).padStart(2, '0');
            const dd = String(dueDate.getDate()).padStart(2, '0');
            const formatted = `${yyyy}-${mm}-${dd}`;

            // Only override due date if user hasn't manually entered a custom one
            if (!dueDateInput.dataset.manuallyChanged) {
                dueDateInput.value = formatted;
            }

            if (previewDueDateBadge) {
                const options = { year: 'numeric', month: 'short', day: 'numeric' };
                previewDueDateBadge.textContent = dueDate.toLocaleDateString(undefined, options) + ' (+14 days)';
            }
        }
    }

    issueDateInput.addEventListener('change', updateDueDate);
    dueDateInput.addEventListener('input', function() {
        this.dataset.manuallyChanged = "true";
    });

    updateDueDate();
}

/**
 * 3. Book Return Workflow - Real-time Overdue Fine Calculator
 */
function initReturnFineCalculator() {
    const returnDateInput = document.getElementById('return-date-input');
    const dueDateElement = document.getElementById('record-due-date-val');
    const fineRateElement = document.getElementById('daily-fine-rate-val');

    const lateDaysDisplay = document.getElementById('calc-late-days');
    const fineAmountDisplay = document.getElementById('calc-fine-amount');
    const statusNoticeDisplay = document.getElementById('calc-status-notice');

    if (!returnDateInput || !dueDateElement) return;

    const dueDateStr = dueDateElement.getAttribute('data-due-date');
    const fineRate = parseFloat(fineRateElement ? fineRateElement.getAttribute('data-rate') : '1.00') || 1.00;

    function calculateReturnFine() {
        if (!returnDateInput.value || !dueDateStr) return;

        const dueParts = dueDateStr.split('-');
        const returnParts = returnDateInput.value.split('-');

        const dueDate = new Date(dueParts[0], dueParts[1] - 1, dueParts[2]);
        const returnDate = new Date(returnParts[0], returnParts[1] - 1, returnParts[2]);

        const diffTime = returnDate.getTime() - dueDate.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays > 0) {
            const fine = (diffDays * fineRate).toFixed(2);
            if (lateDaysDisplay) lateDaysDisplay.textContent = `${diffDays} day(s) late`;
            if (fineAmountDisplay) {
                fineAmountDisplay.textContent = `$${fine}`;
                fineAmountDisplay.className = 'text-danger fw-bold fs-3';
            }
            if (statusNoticeDisplay) {
                statusNoticeDisplay.innerHTML = `<div class="alert alert-warning py-2 mb-0">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i> Book is overdue by <strong>${diffDays} days</strong>. Overdue fine of <strong>$${fine}</strong> applies.
                </div>`;
            }
        } else {
            if (lateDaysDisplay) lateDaysDisplay.textContent = `0 days (On Time)`;
            if (fineAmountDisplay) {
                fineAmountDisplay.textContent = `$0.00`;
                fineAmountDisplay.className = 'text-success fw-bold fs-3';
            }
            if (statusNoticeDisplay) {
                statusNoticeDisplay.innerHTML = `<div class="alert alert-success py-2 mb-0">
                    <i class="bi bi-check-circle-fill me-2"></i> Returned on or before due date. <strong>No fine required!</strong>
                </div>`;
            }
        }
    }

    returnDateInput.addEventListener('change', calculateReturnFine);
    returnDateInput.addEventListener('input', calculateReturnFine);
    calculateReturnFine();
}

/**
 * 4. Dedicated Standalone Due-Date & Overdue Fine Calculator Page
 */
function initStandaloneCalculator() {
    const calcIssueDate = document.getElementById('calc-standalone-issue');
    const calcDaysDuration = document.getElementById('calc-standalone-duration');
    const calcReturnDate = document.getElementById('calc-standalone-return');
    const calcDailyRate = document.getElementById('calc-standalone-rate');

    if (!calcIssueDate || !calcDaysDuration || !calcReturnDate) return;

    const outDueDate = document.getElementById('out-due-date');
    const outTotalBorrowed = document.getElementById('out-total-borrowed');
    const outDaysOverdue = document.getElementById('out-days-overdue');
    const outFineTotal = document.getElementById('out-fine-total');
    const outStatusBanner = document.getElementById('out-status-banner');

    function compute() {
        if (!calcIssueDate.value || !calcReturnDate.value) return;

        const duration = parseInt(calcDaysDuration.value, 10) || 14;
        const rate = parseFloat(calcDailyRate.value) || 1.00;

        const issueParts = calcIssueDate.value.split('-');
        const returnParts = calcReturnDate.value.split('-');

        const issueDate = new Date(issueParts[0], issueParts[1] - 1, issueParts[2]);
        const returnDate = new Date(returnParts[0], returnParts[1] - 1, returnParts[2]);

        const dueDate = new Date(issueDate);
        dueDate.setDate(dueDate.getDate() + duration);

        // Date format
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        if (outDueDate) outDueDate.textContent = dueDate.toLocaleDateString(undefined, options);

        // Days borrowed
        const borrowedDiff = Math.max(0, Math.ceil((returnDate.getTime() - issueDate.getTime()) / (1000 * 60 * 60 * 24)));
        if (outTotalBorrowed) outTotalBorrowed.textContent = `${borrowedDiff} Days`;

        // Overdue calculation
        const overdueDiff = Math.ceil((returnDate.getTime() - dueDate.getTime()) / (1000 * 60 * 60 * 24));

        if (overdueDiff > 0) {
            const fine = (overdueDiff * rate).toFixed(2);
            if (outDaysOverdue) outDaysOverdue.textContent = `${overdueDiff} Days Overdue`;
            if (outFineTotal) outFineTotal.textContent = `$${fine}`;

            if (outStatusBanner) {
                outStatusBanner.className = 'alert alert-danger d-flex align-items-center gap-2 mb-4';
                outStatusBanner.innerHTML = `
                    <i class="bi bi-exclamation-octagon-fill fs-4"></i>
                    <div>
                        <strong>Circulation Status: OVERDUE!</strong><br>
                        Book was returned ${overdueDiff} days after the ${duration}-day borrowing period. Total fine calculated: <strong>$${fine}</strong>.
                    </div>
                `;
            }
        } else {
            if (outDaysOverdue) outDaysOverdue.textContent = `0 Days (Grace Period Valid)`;
            if (outFineTotal) outFineTotal.textContent = `$0.00`;

            if (outStatusBanner) {
                outStatusBanner.className = 'alert alert-success d-flex align-items-center gap-2 mb-4';
                outStatusBanner.innerHTML = `
                    <i class="bi bi-check-circle-fill fs-4"></i>
                    <div>
                        <strong>Circulation Status: ON TIME!</strong><br>
                        Book returned within allowed ${duration} days limit. Zero fine is charged.
                    </div>
                `;
            }
        }
    }

    [calcIssueDate, calcDaysDuration, calcReturnDate, calcDailyRate].forEach(input => {
        if (input) {
            input.addEventListener('input', compute);
            input.addEventListener('change', compute);
        }
    });

    compute();
}

/**
 * 5. Instant Table Search Helper (for Circulation table and Member table)
 */
function initTableQuickSearch() {
    const tableSearchInput = document.getElementById('table-quick-search');
    const table = document.querySelector('.searchable-table');

    if (!tableSearchInput || !table) return;

    tableSearchInput.addEventListener('input', function () {
        const query = this.value.toLowerCase().trim();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    });
}
