class LibraryApp {
    constructor() {
        this.currentTable = 'libraries';
        this.currentPage = 1;
        this.pageSize = 10;
        this.currentData = [];
        this.searchTerm = '';
        this.sortField = '';
        this.sortDirection = 'asc';
        this.currentFilters = {};
        this.init();
    }

    init() {
        console.log("🚀 Initializing LibraryApp...");
        this.bindEvents();
        this.loadTableData();
        this.loadFormData();
        this.updateSortAndFilterOptions();
    }

    bindEvents() {
        console.log("🔧 Setting up event listeners...");

        // Навигация
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                console.log("📍 Navigation clicked:", e.target.dataset.target);
                this.showSection(e.target.dataset.target);
            });
        });

        // Выбор таблицы
        const tableSelect = document.getElementById('table-select');
        if (tableSelect) {
            tableSelect.addEventListener('change', (e) => {
                console.log("📊 Table selected:", e.target.value);
                this.currentTable = e.target.value;
                this.currentPage = 1;
                this.searchTerm = '';
                this.sortField = '';
                this.currentFilters = {};
                document.getElementById('search-input').value = '';
                this.loadTableData();
                this.updateSortAndFilterOptions();
            });
        }

        // Пагинация
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        if (prevBtn && nextBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.loadTableData();
                }
            });

            nextBtn.addEventListener('click', () => {
                this.currentPage++;
                this.loadTableData();
            });
        }

        // Добавление записи
        const addBtn = document.getElementById('add-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                console.log("➕ Add button clicked");
                this.showAddForm();
            });
        }

        // Поиск
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value;
                this.currentPage = 1;
                this.loadTableData();
            });
        }

        // Сортировка
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortField = e.target.value;
                this.loadTableData();
            });
        }

        // Фильтрация
        const filterSelect = document.getElementById('filter-select');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.currentFilters.field = e.target.value;
                this.showFilterInput();
            });
        }

        // Отчеты
        const reportSelect = document.getElementById('report-select');
        const generateReportBtn = document.getElementById('generate-report');
        if (reportSelect && generateReportBtn) {
            reportSelect.addEventListener('change', (e) => {
                this.updateReportFilters(e.target.value);
            });

            generateReportBtn.addEventListener('click', () => {
                this.generateReport();
            });
        }

        // Форма выдачи книг
        const subscriptionForm = document.getElementById('subscription-form-element');
        if (subscriptionForm) {
            subscriptionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createSubscription();
            });
        }

        // Модальное окно
        const closeBtn = document.querySelector('.close');
        const modal = document.getElementById('modal');
        if (closeBtn && modal) {
            closeBtn.addEventListener('click', () => {
                this.hideModal();
            });

            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }

        console.log("✅ All event listeners bound!");
    }

    showSection(sectionId) {
        console.log("🔄 Showing section:", sectionId);
        
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.getElementById(sectionId).classList.add('active');
        document.querySelector(`[data-target="${sectionId}"]`).classList.add('active');

        if (sectionId === 'reports') {
            this.updateReportFilters('library-stats');
        } else if (sectionId === 'subscription-form') {
            this.loadFormData();
        }
    }

    async loadTableData() {
        console.log("📥 Loading table data for:", this.currentTable);
        
        try {
            let url = `/api/${this.currentTable}/?skip=${(this.currentPage - 1) * this.pageSize}&limit=${this.pageSize}`;
            
            if (this.searchTerm) {
                url += `&search=${encodeURIComponent(this.searchTerm)}`;
            }
            
            if (this.sortField) {
                url += `&sort_by=${this.sortField}`;
            }

            // Добавляем фильтры
            Object.keys(this.currentFilters).forEach(key => {
                if (key !== 'field' && this.currentFilters[key]) {
                    url += `&${key}=${encodeURIComponent(this.currentFilters[key])}`;
                }
            });

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("📊 Data loaded:", data);
            this.currentData = data;
            this.renderTable(data);
            this.updatePagination();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showMessage('Ошибка загрузки данных', 'error');
        }
    }

    renderTable(data) {
        const table = document.getElementById('data-table');
        if (!table) {
            console.error('❌ Table element not found!');
            return;
        }

        const thead = table.querySelector('thead tr');
        const tbody = table.querySelector('tbody');

        // Очистка
        thead.innerHTML = '';
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align: center;">Нет данных</td></tr>';
            return;
        }

        // Заголовки
        const headers = Object.keys(data[0]);
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = this.formatHeader(header);
            th.addEventListener('click', () => this.sortTable(header));
            thead.appendChild(th);
        });

        // Добавляем колонку действий
        const actionsTh = document.createElement('th');
        actionsTh.textContent = 'Действия';
        thead.appendChild(actionsTh);

        // Данные
        data.forEach((row, index) => {
            const tr = document.createElement('tr');
            
            headers.forEach(header => {
                const td = document.createElement('td');
                let value = row[header];
                
                // Форматирование дат и чисел
                if (header.includes('_date') || header === 'created_at' || header === 'reg_date') {
                    if (value) {
                        const date = new Date(value);
                        value = date.toLocaleDateString('ru-RU');
                    }
                }
                
                if (header === 'price' || header === 'deposit') {
                    value = parseFloat(value).toFixed(2);
                }
                
                td.textContent = value || '-';
                tr.appendChild(td);
            });

            // Кнопки действий
            const actionsTd = document.createElement('td');
            
            const editBtn = document.createElement('button');
            editBtn.textContent = '✏️';
            editBtn.className = 'action-btn edit-btn';
            editBtn.title = 'Редактировать';
            editBtn.addEventListener('click', () => {
                console.log('Edit row:', row);
                this.showEditForm(row);
            });

            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = '🗑️';
            deleteBtn.className = 'action-btn delete-btn';
            deleteBtn.title = 'Удалить';
            deleteBtn.addEventListener('click', () => {
                console.log('Delete row:', row);
                this.deleteRecord(row);
            });

            actionsTd.appendChild(editBtn);
            actionsTd.appendChild(deleteBtn);
            tr.appendChild(actionsTd);

            tbody.appendChild(tr);
        });

        console.log("✅ Table rendered!");
    }

    formatHeader(header) {
        const headers = {
            'library_id': 'ID',
            'name': 'Название',
            'address': 'Адрес',
            'phone': 'Телефон',
            'created_at': 'Дата создания',
            'topic_id': 'ID Темы',
            'description': 'Описание',
            'author_id': 'ID Автора',
            'full_name': 'Полное имя',
            'birth_year': 'Год рождения',
            'country': 'Страна',
            'book_id': 'ID Книги',
            'title': 'Название',
            'publisher': 'Издатель',
            'publish_place': 'Место издания',
            'publish_year': 'Год издания',
            'quantity': 'Количество',
            'price': 'Цена',
            'reader_id': 'ID Читателя',
            'reg_date': 'Дата регистрации',
            'subscription_id': 'ID Подписки',
            'issue_date': 'Дата выдачи',
            'return_date': 'Дата возврата',
            'deposit': 'Залог',
            // Добавьте для отчета по ценам книг
            'library_name': 'Библиотека',
            'book_count': 'Количество книг',
            'avg_price': 'Средняя цена',
            'min_price': 'Минимальная цена',
            'max_price': 'Максимальная цена',
            'total_value': 'Общая стоимость'
        };
        return headers[header] || header.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    updateSortAndFilterOptions() {
        const sortSelect = document.getElementById('sort-select');
        const filterSelect = document.getElementById('filter-select');
        
        if (!sortSelect || !filterSelect) return;
        
        sortSelect.innerHTML = '<option value="">Без сортировки</option>';
        filterSelect.innerHTML = '<option value="">Без фильтра</option>';

        // Базовые поля для сортировки и фильтрации
        const commonFields = ['name', 'created_at', 'full_name', 'title'];
        
        commonFields.forEach(field => {
            const sortOption = document.createElement('option');
            sortOption.value = field;
            sortOption.textContent = this.formatHeader(field);
            sortSelect.appendChild(sortOption);

            const filterOption = document.createElement('option');
            filterOption.value = field;
            filterOption.textContent = this.formatHeader(field);
            filterSelect.appendChild(filterOption);
        });
    }

    showFilterInput() {
        const filterField = this.currentFilters.field;
        if (!filterField) return;

        // Удаляем старый input фильтра
        const oldInput = document.getElementById('filter-input');
        if (oldInput) oldInput.remove();

        const filterSelect = document.getElementById('filter-select');
        const filterInput = document.createElement('input');
        filterInput.type = 'text';
        filterInput.id = 'filter-input';
        filterInput.placeholder = `Фильтр по ${this.formatHeader(filterField)}`;
        filterInput.style.marginLeft = '10px';
        filterInput.style.padding = '8px 12px';
        filterInput.style.border = '1px solid #ddd';
        filterInput.style.borderRadius = '5px';

        filterInput.addEventListener('input', (e) => {
            this.currentFilters[filterField] = e.target.value;
            this.currentPage = 1;
            this.loadTableData();
        });

        filterSelect.parentNode.insertBefore(filterInput, filterSelect.nextSibling);
    }

    async showAddForm() {
        console.log("📝 Showing add form for:", this.currentTable);
        
        const modal = document.getElementById('modal');
        const form = document.getElementById('modal-form');
        const title = document.getElementById('modal-title');
        
        if (!modal || !form || !title) {
            console.error('❌ Modal elements not found!');
            return;
        }
        
        title.textContent = `Добавить ${this.formatHeader(this.currentTable)}`;
        form.innerHTML = this.generateFormFields();
        
        console.log("🔄 Form HTML generated, loading select options...");
        
        // Загружаем опции для select полей СРАЗУ ПОСЛЕ создания формы
        await this.loadModalSelectOptions();
        
        // Проверяем, что select'ы заполнились
        this.debugSelectValues();
        
        modal.style.display = 'block';

        // Обработка отправки формы
        form.onsubmit = async (e) => {
            e.preventDefault();
            await this.submitForm();
        };
    }

    // Добавьте метод для отладки значений select'ов
    debugSelectValues() {
        if (this.currentTable !== 'books') return;
        
        const selectIds = ['form-library_id', 'form-topic_id', 'form-author_id'];
        
        console.log("🔍 Debugging select values:");
        selectIds.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                console.log(`📋 ${selectId}:`, {
                    value: select.value,
                    options: Array.from(select.options).map(opt => ({
                        value: opt.value,
                        text: opt.text,
                        selected: opt.selected
                    }))
                });
            } else {
                console.error(`❌ Select not found: ${selectId}`);
            }
        });
    }

    async showEditForm(row) {
        console.log('✏️ Edit form called with:', row);
        
        const modal = document.getElementById('modal');
        const form = document.getElementById('modal-form');
        const title = document.getElementById('modal-title');
        
        if (!modal || !form || !title) {
            console.error('❌ Modal elements not found!');
            return;
        }
        
        // Правильно получаем ID для отображения в заголовке
        let id;
        switch(this.currentTable) {
            case 'libraries':
                id = row.library_id;
                break;
            case 'topics':
                id = row.topic_id;
                break;
            case 'authors':
                id = row.author_id;
                break;
            case 'books':
                id = row.book_id;
                break;
            case 'readers':
                id = row.reader_id;
                break;
            case 'subscriptions':
                id = row.subscription_id;
                break;
        }
        
        title.textContent = `Редактировать ${this.formatHeader(this.currentTable)} #${id}`;
        form.innerHTML = this.generateFormFields(row);
        
        // Загружаем опции для select полей
        await this.loadModalSelectOptions();
        
        // Заполняем значения формы
        this.fillFormWithData(row);
        
        modal.style.display = 'block';

        // Обработка отправки формы
        form.onsubmit = async (e) => {
            e.preventDefault();
            await this.submitForm(row);
        };
    }

    generateFormFields(data = {}) {
        const fieldsConfig = {
            libraries: [
                { name: 'name', type: 'text', label: 'Название', required: true },
                { name: 'address', type: 'text', label: 'Адрес', required: true },
                { name: 'phone', type: 'text', label: 'Телефон' }
            ],
            topics: [
                { name: 'name', type: 'text', label: 'Название', required: true },
                { name: 'description', type: 'textarea', label: 'Описание' }
            ],
            authors: [
                { name: 'full_name', type: 'text', label: 'Полное имя', required: true },
                { name: 'birth_year', type: 'number', label: 'Год рождения', min: 1500, max: new Date().getFullYear() },
                { name: 'country', type: 'text', label: 'Страна' }
            ],
            books: [
            { name: 'book_title', type: 'text', label: 'Название', required: true }, // Изменили name чтобы избежать конфликта
            { name: 'publisher', type: 'text', label: 'Издатель' },
            { name: 'publish_place', type: 'text', label: 'Место издания' },
            { name: 'publish_year', type: 'number', label: 'Год издания', min: 1500, max: new Date().getFullYear() },
            { name: 'quantity', type: 'number', label: 'Количество', min: 0 },
            { name: 'price', type: 'number', label: 'Цена', step: '0.01', min: 0 },
            { name: 'library_id', type: 'select', label: 'Библиотека', endpoint: 'libraries', required: true },
            { name: 'topic_id', type: 'select', label: 'Тема', endpoint: 'topics', required: true },
            { name: 'author_id', type: 'select', label: 'Автор', endpoint: 'authors', required: true }
        ],
            readers: [
                { name: 'full_name', type: 'text', label: 'Полное имя', required: true },
                { name: 'address', type: 'text', label: 'Адрес' },
                { name: 'phone', type: 'text', label: 'Телефон' }
            ],
            subscriptions: [
                { name: 'library_id', type: 'select', label: 'Библиотека', endpoint: 'libraries', required: true },
                { name: 'book_id', type: 'select', label: 'Книга', endpoint: 'books', required: true },
                { name: 'reader_id', type: 'select', label: 'Читатель', endpoint: 'readers', required: true },
                { name: 'issue_date', type: 'date', label: 'Дата выдачи' },
                { name: 'return_date', type: 'date', label: 'Дата возврата' },
                { name: 'deposit', type: 'number', label: 'Залог', step: '0.01', min: 0 }
            ]
        };

        const fields = fieldsConfig[this.currentTable] || [];
        let html = '';

        for (const field of fields) {
            html += `<div class="form-group">`;
            html += `<label for="form-${field.name}">${field.label}:${field.required ? ' *' : ''}</label>`; // Используем form- префикс
            
            if (field.type === 'select' && field.endpoint) {
                html += `<select id="form-${field.name}" ${field.required ? 'required' : ''}>`; // form- префикс
                html += `<option value="">Выберите...</option>`;
                html += `</select>`;
            } else if (field.type === 'textarea') {
                html += `<textarea id="form-${field.name}" ${field.required ? 'required' : ''}>${data[field.name] || ''}</textarea>`; // form- префикс
            } else {
                const value = data[field.name] || '';
                const attributes = [
                    field.required ? 'required' : '',
                    field.min ? `min="${field.min}"` : '',
                    field.max ? `max="${field.max}"` : '',
                    field.step ? `step="${field.step}"` : ''
                ].filter(attr => attr).join(' ');
                
                html += `<input type="${field.type}" id="form-${field.name}" value="${value}" ${attributes}>`; // form- префикс
            }
            
            html += `</div>`;
        }

        html += `<button type="submit">${data ? 'Обновить' : 'Добавить'}</button>`;
        return html;
    }

    async loadModalSelectOptions() {
        console.log("📥 Loading modal select options for:", this.currentTable);
        
        const fieldsConfig = {
            books: [
                { field: 'library_id', endpoint: 'libraries' },
                { field: 'topic_id', endpoint: 'topics' },
                { field: 'author_id', endpoint: 'authors' }
            ],
            subscriptions: [
                { field: 'library_id', endpoint: 'libraries' },
                { field: 'book_id', endpoint: 'books' },
                { field: 'reader_id', endpoint: 'readers' }
            ]
        };

        const fieldsToLoad = fieldsConfig[this.currentTable] || [];
        
        console.log("Fields to load:", fieldsToLoad);
        
        if (fieldsToLoad.length === 0) {
            console.log("ℹ️ No select fields to load for this table");
            return;
        }
        
        // Загружаем опции параллельно для скорости
        const loadPromises = fieldsToLoad.map(field => 
            this.loadSelectOptions(`form-${field.field}`, field.endpoint)
        );
        
        await Promise.all(loadPromises);
        console.log("✅ All select options loaded for", this.currentTable);
    }

    fillFormWithData(data) {
        console.log("📝 Filling form with data:", data);
        
        // Специальная обработка для книги (book_title вместо title)
        if (this.currentTable === 'books' && data.title) {
            data.book_title = data.title;
        }
        
        for (const key in data) {
            // Пробуем сначала новые ID с префиксом form-, потом старые
            let input = document.getElementById(`form-${key}`);
            if (!input) {
                input = document.getElementById(`modal-${key}`);
            }
            
            if (input) {
                input.value = data[key] || '';
                console.log(`✅ Filled ${input.id} with:`, data[key]);
            } else {
                console.warn(`⚠️ Input not found for key: ${key} (tried form-${key} and modal-${key})`);
            }
        }
    }

    async loadSelectOptions(selectId, endpoint) {
        try {
            console.log(`📥 Loading options for ${selectId} from ${endpoint}`);
            
            const response = await fetch(`/api/${endpoint}/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const select = document.getElementById(selectId);
            
            if (!select) {
                console.error(`❌ Select element not found: ${selectId}`);
                return;
            }
            
            console.log(`📊 Loaded ${data.length} records from ${endpoint}`);
            
            // Сохраняем текущее значение
            const currentValue = select.value;
            
            // Очищаем и добавляем опции
            select.innerHTML = '<option value="">Выберите...</option>';
            
            if (data.length === 0) {
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "Нет доступных записей";
                option.disabled = true;
                select.appendChild(option);
                console.warn(`⚠️ No records found for ${endpoint}`);
                return;
            }
            
            data.forEach(item => {
                const option = document.createElement('option');
                
                let idField, displayField;
                
                switch(endpoint) {
                    case 'libraries':
                        idField = 'library_id';
                        displayField = 'name';
                        break;
                    case 'topics':
                        idField = 'topic_id';
                        displayField = 'name';
                        break;
                    case 'authors':
                        idField = 'author_id';
                        displayField = 'full_name';
                        break;
                    case 'books':
                        idField = 'book_id';
                        displayField = 'title';
                        // Для книг добавляем информацию о количестве
                        const quantityInfo = item.quantity > 0 ? ` (${item.quantity} шт.)` : ' (нет в наличии)';
                        break;
                    case 'readers':
                        idField = 'reader_id';
                        displayField = 'full_name';
                        break;
                    default:
                        idField = 'id';
                        displayField = 'name';
                }
                
                if (!item[idField]) {
                    console.warn(`⚠️ Item missing ID field ${idField}:`, item);
                    return;
                }
                
                option.value = item[idField];
                
                // Форматируем текст опции
                let displayText = item[displayField];
                if (endpoint === 'books') {
                    // Для книг добавляем информацию о доступности
                    const quantityInfo = item.quantity > 0 ? ` (${item.quantity} шт.)` : ' (нет в наличии)';
                    displayText += quantityInfo;
                    
                    // Отключаем option если книга недоступна
                    if (item.quantity <= 0) {
                        option.disabled = true;
                    }
                }
                
                option.textContent = displayText || `Запись #${item[idField]}`;
                select.appendChild(option);
            });
            
            // Восстанавливаем предыдущее значение, если оно есть
            if (currentValue) {
                select.value = currentValue;
            }
            
            console.log(`✅ Loaded ${data.length} options for ${selectId}`);
            
        } catch (error) {
            console.error(`❌ Error loading options for ${selectId}:`, error);
            
            const select = document.getElementById(selectId);
            if (select) {
                select.innerHTML = '<option value="">Ошибка загрузки</option>';
            }
        }
    }

    async submitForm(data = null) {
        console.log('📤 Submit form called with data:', data);
        
        const payload = {};
        
        // Обновляем fieldsConfig с учетом новых имен полей
        const fieldsConfig = {
            libraries: ['name', 'address', 'phone'],
            topics: ['name', 'description'],
            authors: ['full_name', 'birth_year', 'country'],
            books: ['book_title', 'publisher', 'publish_place', 'publish_year', 'quantity', 'price', 'library_id', 'topic_id', 'author_id'], // book_title вместо title
            readers: ['full_name', 'address', 'phone'],
            subscriptions: ['library_id', 'book_id', 'reader_id', 'issue_date', 'return_date', 'deposit']
        };

        const fields = fieldsConfig[this.currentTable] || [];
        
        for (const field of fields) {
            // Пробуем сначала новые ID с префиксом form-, потом старые с modal-
            let input = document.getElementById(`form-${field}`);
            if (!input) {
                input = document.getElementById(`modal-${field}`);
                if (input) console.log(`⚠️ Using old ID: modal-${field}`);
            }
            
            if (input) {
                let value = input.value;
                
                console.log(`📝 Field: ${field}, Value: ${value}, Type: ${input.type}`);
                
                // Преобразование типов
                if (input.type === 'number') {
                    value = value ? parseFloat(value) : 0;
                    if (isNaN(value)) value = 0;
                } else if (field.includes('_id')) {
                    value = value ? parseInt(value) : null;
                    if (isNaN(value)) value = null;
                } else if (input.type === 'date' && !value) {
                    value = null;
                }
                
                // Для отправки на сервер используем правильные имена полей
                // book_title преобразуем в title для сервера
                const serverFieldName = field === 'book_title' ? 'title' : field;
                payload[serverFieldName] = value;
            } else {
                console.error(`❌ Input not found for field: ${field} (tried form-${field} and modal-${field})`);
            }
        }

        console.log('📦 Final payload to send:', JSON.stringify(payload, null, 2));

        // Валидация обязательных полей
        if (this.currentTable === 'books') {
            const requiredFields = ['title', 'library_id', 'topic_id', 'author_id']; // Используем server field names
            const missingFields = requiredFields.filter(field => !payload[field] && payload[field] !== 0);
            
            if (missingFields.length > 0) {
                this.showMessage(`Заполните обязательные поля: ${missingFields.map(f => this.formatHeader(f)).join(', ')}`, 'error');
                return;
            }
        }

        try {
            let response;
            let url;
            
            if (data) {
                // Обновление существующей записи
                let id;
                switch(this.currentTable) {
                    case 'libraries':
                        id = data.library_id;
                        break;
                    case 'topics':
                        id = data.topic_id;
                        break;
                    case 'authors':
                        id = data.author_id;
                        break;
                    case 'books':
                        id = data.book_id;
                        break;
                    case 'readers':
                        id = data.reader_id;
                        break;
                    case 'subscriptions':
                        id = data.subscription_id;
                        break;
                }
                
                if (!id) {
                    throw new Error('ID not found for update');
                }
                
                url = `/api/${this.currentTable}/${id}`;
                console.log(`🔄 Updating ${this.currentTable} at:`, url);
                
                response = await fetch(url, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                // Создание новой записи
                url = `/api/${this.currentTable}/`;
                console.log(`➕ Creating new ${this.currentTable} at:`, url);
                
                response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (response.ok) {
                const result = await response.json();
                this.hideModal();
                this.loadTableData();
                this.showMessage(data ? 'Запись обновлена!' : 'Запись добавлена!', 'success');
            } else {
                const error = await response.json();
                console.error('Submit error:', error);
                this.showMessage(`Ошибка: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Submit network error:', error);
            this.showMessage('Ошибка сети: ' + error.message, 'error');
        }
    }

    async deleteRecord(row) {
        console.log('🗑️ Delete record called with:', row);
        
        // Правильно получаем ID в зависимости от таблицы
        let id;
        let name;
        
        switch(this.currentTable) {
            case 'libraries':
                id = row.library_id;
                name = row.name;
                break;
            case 'topics':
                id = row.topic_id;
                name = row.name;
                break;
            case 'authors':
                id = row.author_id;
                name = row.full_name;
                break;
            case 'books':
                id = row.book_id;
                name = row.title;
                break;
            case 'readers':
                id = row.reader_id;
                name = row.full_name;
                break;
            case 'subscriptions':
                id = row.subscription_id;
                name = `подписка #${row.subscription_id}`;
                break;
            default:
                console.error('Unknown table:', this.currentTable);
                this.showMessage('Неизвестная таблица', 'error');
                return;
        }

        if (!id) {
            console.error('ID not found in row:', row);
            this.showMessage('Ошибка: ID не найден', 'error');
            return;
        }

        if (!confirm(`Вы уверены, что хотите удалить "${name}"?`)) {
            return;
        }

        try {
            console.log(`🗑️ Deleting ${this.currentTable} with ID:`, id);
            
            const response = await fetch(`/api/${this.currentTable}/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showMessage(`"${name}" успешно удален(а)!`, 'success');
                this.loadTableData(); // Перезагружаем таблицу
            } else {
                const error = await response.json();
                console.error('Delete error:', error);
                this.showMessage(`Ошибка удаления: ${error.detail}`, 'error');
                
                // Специальная обработка для читателей с активными подписками
                if (this.currentTable === 'readers' && error.detail && error.detail.includes('active subscriptions')) {
                    if (confirm('Хотите посмотреть активные подписки этого читателя?')) {
                        this.showReaderSubscriptions(id);
                    }
                }
            }
        } catch (error) {
            console.error('Network error:', error);
            this.showMessage('Ошибка сети при удалении', 'error');
        }
    }

    searchData(term) {
        this.searchTerm = term;
        this.currentPage = 1;
        this.loadTableData();
    }

    sortTable(field) {
        if (this.sortField === field) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortDirection = 'asc';
        }
        this.loadTableData();
    }

    updatePagination() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const pageInfo = document.getElementById('page-info');

        if (!prevBtn || !nextBtn || !pageInfo) return;

        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentData.length < this.pageSize;
        
        pageInfo.textContent = `Страница ${this.currentPage}`;
    }

    updateReportFilters(reportType) {
        const filtersDiv = document.getElementById('report-filters');
        if (!filtersDiv) return;
        
        filtersDiv.innerHTML = '';

        const filtersConfig = {
            'library-stats': [
                { name: 'min_books', type: 'number', label: 'Мин. книг', value: 0 }
            ],
            'author-stats': [
                { name: 'min_books', type: 'number', label: 'Мин. книг', value: 1 },
                { name: 'country', type: 'text', label: 'Страна' }
            ],
            'active-subscriptions': [
                { name: 'library_id', type: 'select', label: 'Библиотека', endpoint: 'libraries' }
            ],
            'book-prices': [
                { name: 'min_price', type: 'number', label: 'Мин. цена', value: 0 },
                { name: 'max_price', type: 'number', label: 'Макс. цена', value: 1000 },
                { name: 'topic_id', type: 'select', label: 'Тема', endpoint: 'topics' }
            ],
            'overdue-subscriptions': [
                { name: 'days_overdue', type: 'number', label: 'Дней просрочки', value: 7 }
            ]
        };

        const filters = filtersConfig[reportType] || [];
        
        filters.forEach(filter => {
            const div = document.createElement('div');
            div.className = 'form-group';
            
            const label = document.createElement('label');
            label.textContent = filter.label;
            label.style.fontSize = '12px';
            label.style.marginBottom = '2px';
            
            let input;
            if (filter.type === 'select' && filter.endpoint) {
                input = document.createElement('select');
                input.id = `report-${filter.name}`;
                input.style.padding = '4px 8px';
                input.style.fontSize = '12px';
                
                // Добавляем опцию "Все" для select'ов
                const allOption = document.createElement('option');
                allOption.value = '';
                allOption.textContent = 'Все';
                input.appendChild(allOption);
                
                this.loadSelectOptions(`report-${filter.name}`, filter.endpoint);
            } else {
                input = document.createElement('input');
                input.type = filter.type;
                input.id = `report-${filter.name}`;
                input.value = filter.value || '';
                input.style.padding = '4px 8px';
                input.style.fontSize = '12px';
                input.placeholder = filter.label;
            }
            
            div.appendChild(label);
            div.appendChild(input);
            filtersDiv.appendChild(div);
        });
    }

    async generateReport() {
        const reportType = document.getElementById('report-select').value;
        const filtersDiv = document.getElementById('report-filters');
        if (!filtersDiv) return;
        
        const inputs = filtersDiv.querySelectorAll('input, select');
        
        // Используем правильные URL для ваших API
        let url = `/reports/${reportType}/?`;
        const params = [];
        
        inputs.forEach(input => {
            const paramName = input.id.replace('report-', '');
            if (input.value && input.value !== '') {
                params.push(`${paramName}=${encodeURIComponent(input.value)}`);
            }
        });
        
        // Добавляем параметр сортировки если есть
        if (reportType === 'active-subscriptions') {
            params.push('sort_by=issue_date');
        }
        
        url += params.join('&');

        console.log(`🔍 Generating report from: ${url}`);

        try {
            const response = await fetch(url);
            console.log(`📊 Response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log(`✅ Report data received:`, data);
            
            if (data.length === 0) {
                this.showMessage('Нет данных для отчета', 'info');
            }
            
            this.renderReport(data, reportType);
            this.showMessage(`Отчет "${this.getReportName(reportType)}" сформирован!`, 'success');
            
        } catch (error) {
            console.error('Error generating report:', error);
            this.showMessage('Ошибка формирования отчета: ' + error.message, 'error');
            
            // Fallback на клиентскую генерацию если API недоступно
            await this.generateFallbackReport(reportType);
        }
    }

    // Fallback метод если API недоступно
    async generateFallbackReport(reportType) {
        console.log("🔄 Using fallback report generation...");
        
        try {
            let reportData = [];
            
            switch(reportType) {
                case 'active-subscriptions':
                    reportData = await this.generateActiveSubscriptionsFallback();
                    break;
                case 'library-stats':
                    reportData = await this.generateLibraryStatsFallback();
                    break;
                default:
                    throw new Error('Report type not supported in fallback');
            }
            
            this.renderReport(reportData, reportType);
            this.showMessage('Отчет сформирован (использованы резервные данные)', 'info');
            
        } catch (fallbackError) {
            console.error('Fallback also failed:', fallbackError);
            this.showMessage('Не удалось сформировать отчет', 'error');
        }
    }

    renderReport(data, reportType) {
        const table = document.getElementById('report-table');
        if (!table) {
            console.error('❌ Report table element not found!');
            return;
        }
        
        table.innerHTML = '';

        if (!data || data.length === 0) {
            table.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 20px;">Нет данных для отчета</td></tr>';
            return;
        }

        // Определяем заголовки в зависимости от типа отчета
        let headers = [];
        
        if (reportType === 'active-subscriptions') {
            headers = ['subscription_id', 'reader_name', 'book_title', 'library_name', 'issue_date', 'expected_return_date', 'status', 'deposit'];
        } else if (reportType === 'book-prices') {
            headers = ['library_name', 'book_count', 'avg_price', 'min_price', 'max_price', 'total_value'];
        } else {
            headers = Object.keys(data[0]);
        }

        // Заголовки отчета
        let thead = '<tr>';
        headers.forEach(header => {
            thead += `<th>${this.formatHeader(header)}</th>`;
        });
        thead += '</tr>';
        table.innerHTML = thead;

        // Данные отчета
        let tbody = '';
        data.forEach(row => {
            tbody += '<tr>';
            headers.forEach(header => {
                let value = row[header];
                let cellClass = '';
                
                // Форматирование чисел
                if (typeof value === 'number') {
                    if (header.includes('price') || header.includes('value') || header.includes('deposit')) {
                        value = value.toFixed(2);
                    }
                }
                
                // Форматирование дат
                if (header.includes('_date') && value && value !== '-') {
                    try {
                        const date = new Date(value);
                        value = date.toLocaleDateString('ru-RU');
                    } catch (e) {
                        // Оставляем как есть
                    }
                }
                
                // Стили для статуса
                if (header === 'status') {
                    if (row.status_type === 'active') {
                        cellClass = 'status-active';
                    } else if (row.status_type === 'overdue') {
                        cellClass = 'status-overdue';
                    } else if (row.status_type === 'error') {
                        cellClass = 'status-error';
                    }
                }
                
                // Для expected_return_date показываем "Не установлен" если нет даты
                if (header === 'expected_return_date' && (!value || value === '-')) {
                    value = 'Не установлен';
                }
                
                tbody += `<td class="${cellClass}">${value || '-'}</td>`;
            });
            tbody += '</tr>';
        });

        table.innerHTML += tbody;
        console.log(`✅ Report rendered with ${data.length} rows`);
    }

    async loadFormData() {
        try {
            // Загрузка читателей
            const readersResponse = await fetch('/api/readers/');
            const readers = await readersResponse.json();
            const readerSelect = document.getElementById('reader-select');
            if (readerSelect) {
                readerSelect.innerHTML = '<option value="">Выберите читателя</option>';
                readers.forEach(reader => {
                    const option = document.createElement('option');
                    option.value = reader.reader_id;
                    option.textContent = reader.full_name;
                    readerSelect.appendChild(option);
                });
            }

            // Загрузка книг
            const booksResponse = await fetch('/api/books/');
            const books = await booksResponse.json();
            const bookSelect = document.getElementById('book-select');
            if (bookSelect) {
                bookSelect.innerHTML = '<option value="">Выберите книгу</option>';
                books.forEach(book => {
                    if (book.quantity > 0) {
                        const option = document.createElement('option');
                        option.value = book.book_id;
                        option.textContent = `${book.title} (${book.quantity} шт.)`;
                        option.dataset.quantity = book.quantity;
                        bookSelect.appendChild(option);
                    }
                });
            }

            // Загрузка библиотек
            const librariesResponse = await fetch('/api/libraries/');
            const libraries = await librariesResponse.json();
            const librarySelect = document.getElementById('library-select');
            if (librarySelect) {
                librarySelect.innerHTML = '<option value="">Выберите библиотеку</option>';
                libraries.forEach(library => {
                    const option = document.createElement('option');
                    option.value = library.library_id;
                    option.textContent = library.name;
                    librarySelect.appendChild(option);
                });
            }

            // Обновление количества при выборе книги
            if (bookSelect) {
                bookSelect.addEventListener('change', (e) => {
                    const selectedOption = e.target.selectedOptions[0];
                    const quantity = selectedOption ? selectedOption.dataset.quantity : 0;
                    const bookQuantity = document.getElementById('book-quantity');
                    if (bookQuantity) {
                        bookQuantity.textContent = `Доступно: ${quantity} шт.`;
                    }
                });
            }

        } catch (error) {
            console.error('Error loading form data:', error);
        }
    }

    async createSubscription() {
        const readerSelect = document.getElementById('reader-select');
        const bookSelect = document.getElementById('book-select');
        const librarySelect = document.getElementById('library-select');
        const depositInput = document.getElementById('deposit');

        if (!readerSelect || !bookSelect || !librarySelect || !depositInput) {
            this.showMessage('Форма не найдена', 'error');
            return;
        }

        const formData = {
            reader_id: parseInt(readerSelect.value),
            book_id: parseInt(bookSelect.value),
            library_id: parseInt(librarySelect.value),
            deposit: parseFloat(depositInput.value) || 0
        };

        try {
            const response = await fetch('/api/subscriptions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showMessage('Книга успешно выдана!', 'success');
                document.getElementById('subscription-form-element').reset();
                const bookQuantity = document.getElementById('book-quantity');
                if (bookQuantity) {
                    bookQuantity.textContent = '';
                }
                // Обновляем список книг
                this.loadFormData();
            } else {
                this.showMessage(`Ошибка: ${result.detail}`, 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    }

    showMessage(message, type) {
        // Создаем временное уведомление
        const notification = document.createElement('div');
        notification.className = type;
        notification.textContent = message;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1000';
        notification.style.padding = '15px';
        notification.style.borderRadius = '5px';
        notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        notification.style.backgroundColor = type === 'error' ? '#f8d7da' : '#d4edda';
        notification.style.color = type === 'error' ? '#721c24' : '#155724';
        notification.style.border = type === 'error' ? '1px solid #f5c6cb' : '1px solid #c3e6cb';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    hideModal() {
        const modal = document.getElementById('modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
        // Fallback для активных подписок
    async generateActiveSubscriptionsFallback() {
        try {
            const response = await fetch('/api/subscriptions/?active_only=true');
            if (!response.ok) throw new Error('Failed to fetch subscriptions');
            
            const subscriptions = await response.json();
            const activeSubs = subscriptions.filter(sub => !sub.return_date);
            
            // Получаем детальную информацию для активных подписок
            const detailedSubs = [];
            
            for (const sub of activeSubs.slice(0, 50)) { // Ограничиваем для производительности
                try {
                    const [bookResponse, readerResponse, libraryResponse] = await Promise.all([
                        fetch(`/api/books/${sub.book_id}`).catch(() => ({ ok: false })),
                        fetch(`/api/readers/${sub.reader_id}`).catch(() => ({ ok: false })),
                        fetch(`/api/libraries/${sub.library_id}`).catch(() => ({ ok: false }))
                    ]);
                    
                    const book = bookResponse.ok ? await bookResponse.json() : { title: 'Неизвестно' };
                    const reader = readerResponse.ok ? await readerResponse.json() : { full_name: 'Неизвестно' };
                    const library = libraryResponse.ok ? await libraryResponse.json() : { name: 'Неизвестно' };
                    
                    detailedSubs.push({
                        subscription_id: sub.subscription_id,
                        reader_name: reader.full_name,
                        book_title: book.title,
                        library_name: library.name,
                        issue_date: sub.issue_date,
                        return_date: sub.return_date,
                        deposit: sub.deposit
                    });
                } catch (error) {
                    console.error('Error processing subscription:', error);
                }
            }
            
            return detailedSubs;
            
        } catch (error) {
            console.error('Fallback failed:', error);
            // Возвращаем тестовые данные
            return [
                {
                    subscription_id: 1,
                    reader_name: "Иван Иванов",
                    book_title: "Тестовая книга",
                    library_name: "Центральная библиотека",
                    issue_date: "2024-01-15",
                    return_date: null,
                    deposit: 100.00
                }
            ];
        }
    }

    // Fallback для статистики библиотек
    async generateLibraryStatsFallback() {
        try {
            const [librariesResponse, booksResponse] = await Promise.all([
                fetch('/api/libraries/'),
                fetch('/api/books/')
            ]);
            
            const libraries = librariesResponse.ok ? await librariesResponse.json() : [];
            const books = booksResponse.ok ? await booksResponse.json() : [];
            
            return libraries.map(library => {
                const libraryBooks = books.filter(book => book.library_id === library.library_id);
                const totalBooks = libraryBooks.length;
                const totalCopies = libraryBooks.reduce((sum, book) => sum + (book.quantity || 0), 0);
                const totalValue = libraryBooks.reduce((sum, book) => sum + (book.price || 0) * (book.quantity || 0), 0);
                
                return {
                    library_name: library.name,
                    total_books: totalBooks,
                    total_copies: totalCopies,
                    total_value: totalValue
                };
            });
            
        } catch (error) {
            console.error('Fallback failed:', error);
            return [
                {
                    library_name: "Центральная библиотека",
                    total_books: 15,
                    total_copies: 45,
                    total_value: 12500.50
                }
            ];
        }
    }
    // Добавьте этот метод для проверки доступности отчетов
    async checkReportsAvailability() {
        console.log('🔍 Checking reports API availability...');
        
        const reports = [
            'active-subscriptions',
            'library-stats', 
            'author-stats',
            'book-prices'
        ];
        
        for (const report of reports) {
            try {
                const response = await fetch(`/reports/${report}/`);
                console.log(`📋 ${report}: ${response.status} ${response.statusText}`);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log(`   ✅ Data: ${data.length} records`);
                }
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }
        getReportName(reportType) {
        const reportNames = {
            'library-stats': 'Статистика библиотек',
            'author-stats': 'Статистика авторов',
            'active-subscriptions': 'Активные подписки',
            'book-prices': 'Цены на книги',
            'overdue-subscriptions': 'Просроченные подписки'
        };
        return reportNames[reportType] || reportType;
    }
    // Добавьте этот метод в класс LibraryApp
    async generateActiveSubscriptionsReport() {
        const filtersDiv = document.getElementById('report-filters');
        const librarySelect = filtersDiv ? filtersDiv.querySelector('#report-library_id') : null;
        const libraryId = librarySelect ? librarySelect.value : null;
        
        // Используем рабочий эндпоинт с active_only=true
        let url = '/api/subscriptions/?active_only=true&limit=100';
        
        if (libraryId) {
            url += `&library_id=${libraryId}`;
        }
        
        console.log(`🔍 Fetching active subscriptions from: ${url}`);
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const activeSubscriptions = await response.json();
            console.log(`✅ Raw active subscriptions:`, activeSubscriptions);
            
            if (activeSubscriptions.length === 0) {
                return [{
                    subscription_id: 0,
                    reader_name: "Нет активных подписок",
                    book_title: "Все книги возвращены",
                    library_name: libraryId ? "Выбранная библиотека" : "-",
                    issue_date: "-",
                    return_date: null,
                    deposit: 0
                }];
            }
            
            // Обогащаем данные информацией о книгах, читателях и библиотеках
            const enrichedData = await this.enrichSubscriptionData(activeSubscriptions);
            console.log(`🎯 Enriched data:`, enrichedData);
            
            return enrichedData;
            
        } catch (error) {
            console.error('Error fetching active subscriptions:', error);
            throw error;
        }
    }

    // Метод для обогащения данных подписок
    async enrichSubscriptionData(subscriptions) {
        const enrichedData = [];
        
        for (const sub of subscriptions) {
            try {
                console.log(`📝 Processing subscription ${sub.subscription_id}:`, sub);
                
                // Получаем детальную информацию параллельно
                const [book, reader, library] = await Promise.all([
                    this.fetchItem(`/api/books/${sub.book_id}`, { title: 'Неизвестная книга' }),
                    this.fetchItem(`/api/readers/${sub.reader_id}`, { full_name: 'Неизвестный читатель' }),
                    this.fetchItem(`/api/libraries/${sub.library_id}`, { name: 'Неизвестная библиотека' })
                ]);
                
                console.log(`✅ Enriched:`, { book, reader, library });
                
                enrichedData.push({
                    subscription_id: sub.subscription_id,
                    reader_name: reader.full_name,
                    book_title: book.title,
                    library_name: library.name,
                    issue_date: sub.issue_date,
                    return_date: sub.return_date,
                    deposit: sub.deposit || 0
                });
                
            } catch (error) {
                console.error(`❌ Error enriching subscription ${sub.subscription_id}:`, error);
                
                // Добавляем базовую информацию даже если не удалось обогатить
                enrichedData.push({
                    subscription_id: sub.subscription_id,
                    reader_name: 'Ошибка загрузки',
                    book_title: 'Ошибка загрузки',
                    library_name: 'Ошибка загрузки',
                    issue_date: sub.issue_date,
                    return_date: sub.return_date,
                    deposit: sub.deposit || 0
                });
            }
        }
        
        return enrichedData;
    }

    // Вспомогательный метод для безопасного fetch
    async fetchItem(url, defaultValue = {}) {
        try {
            console.log(`🔍 Fetching: ${url}`);
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Fetched: ${url}`, data);
                return data;
            } else {
                console.warn(`⚠️ Fetch failed: ${url} - ${response.status}`);
            }
        } catch (error) {
            console.error(`❌ Fetch error: ${url} - ${error.message}`);
        }
        return defaultValue;
    }

    // Обновите метод generateReport
    async generateReport() {
        const reportType = document.getElementById('report-select').value;
        
        console.log(`📊 Generating report: ${reportType}`);

        try {
            let reportData = [];
            
            switch(reportType) {
                case 'active-subscriptions':
                    reportData = await this.generateActiveSubscriptionsReport();
                    break;
                case 'library-stats':
                    // Используем ваш существующий API
                    const response = await fetch('/reports/library-stats/');
                    if (!response.ok) throw new Error('Failed to fetch library stats');
                    reportData = await response.json();
                    break;
                case 'author-stats':
                    // Используем ваш существующий API
                    const authorResponse = await fetch('/reports/author-stats/');
                    if (!authorResponse.ok) throw new Error('Failed to fetch author stats');
                    reportData = await authorResponse.json();
                    break;
                case 'book-prices':
                    // Используем ваш существующий API
                    const bookResponse = await fetch('/reports/book-prices/');
                    if (!bookResponse.ok) throw new Error('Failed to fetch book prices');
                    reportData = await bookResponse.json();
                    break;
                default:
                    throw new Error('Unknown report type');
            }
            
            this.renderReport(reportData, reportType);
            this.showMessage(`Отчет "${this.getReportName(reportType)}" сформирован!`, 'success');
            
        } catch (error) {
            console.error('Error generating report:', error);
            this.showMessage('Ошибка формирования отчета: ' + error.message, 'error');
        }
    }
    getReportName(reportType) {
        const reportNames = {
            'library-stats': 'Статистика библиотек',
            'author-stats': 'Статистика авторов',
            'active-subscriptions': 'Активные подписки',
            'book-prices': 'Цены на книги',
            'overdue-subscriptions': 'Просроченные подписки'
        };
        return reportNames[reportType] || reportType;
    }
    // Метод для определения статуса подписки
    getSubscriptionStatus(subscription) {
        if (!subscription) return 'unknown';
        
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // Если return_date не установлен - активна
        if (!subscription.return_date || subscription.return_date === '-') {
            return 'active';
        }
        
        try {
            const returnDate = new Date(subscription.return_date);
            returnDate.setHours(0, 0, 0, 0);
            
            // Если дата возврата в будущем - активна
            if (returnDate > today) {
                return 'active';
            }
            // Если дата возврата в прошлом - просрочена
            else if (returnDate < today) {
                return 'overdue';
            }
            // Если сегодня последний день - активна (но скоро просрочится)
            else {
                return 'active';
            }
        } catch (error) {
            console.error('Error parsing date:', error);
            return 'unknown';
        }
    }

    // Обновим метод обогащения данных
    async enrichSubscriptionData(subscriptions) {
        const enrichedData = [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        for (const sub of subscriptions) {
            try {
                console.log(`📝 Processing subscription ${sub.subscription_id}:`, sub);
                
                // Получаем детальную информацию
                const [book, reader, library] = await Promise.all([
                    this.fetchItem(`/api/books/${sub.book_id}`, { title: 'Неизвестная книга' }),
                    this.fetchItem(`/api/readers/${sub.reader_id}`, { full_name: 'Неизвестный читатель' }),
                    this.fetchItem(`/api/libraries/${sub.library_id}`, { name: 'Неизвестная библиотека' })
                ]);
                
                // Определяем статус
                const status = this.getSubscriptionStatus(sub);
                let statusText = '';
                let daysInfo = '';
                
                switch(status) {
                    case 'active':
                        statusText = 'Активна';
                        if (sub.return_date) {
                            const returnDate = new Date(sub.return_date);
                            const daysLeft = Math.ceil((returnDate - today) / (1000 * 60 * 60 * 24));
                            daysInfo = ` (осталось ${daysLeft} дн.)`;
                        } else {
                            daysInfo = ' (без срока)';
                        }
                        break;
                    case 'overdue':
                        statusText = 'Просрочена';
                        if (sub.return_date) {
                            const returnDate = new Date(sub.return_date);
                            const daysOverdue = Math.ceil((today - returnDate) / (1000 * 60 * 60 * 24));
                            daysInfo = ` (+${daysOverdue} дн.)`;
                        }
                        break;
                    default:
                        statusText = 'Неизвестно';
                }
                
                enrichedData.push({
                    subscription_id: sub.subscription_id,
                    reader_name: reader.full_name,
                    book_title: book.title,
                    library_name: library.name,
                    issue_date: sub.issue_date,
                    return_date: sub.return_date,
                    expected_return_date: sub.return_date, // сохраняем оригинальную дату
                    deposit: sub.deposit || 0,
                    status: statusText + daysInfo,
                    status_type: status
                });
                
            } catch (error) {
                console.error(`❌ Error enriching subscription ${sub.subscription_id}:`, error);
                
                // Добавляем базовую информацию
                enrichedData.push({
                    subscription_id: sub.subscription_id,
                    reader_name: 'Ошибка загрузки',
                    book_title: 'Ошибка загрузки', 
                    library_name: 'Ошибка загрузки',
                    issue_date: sub.issue_date,
                    return_date: sub.return_date,
                    expected_return_date: sub.return_date,
                    deposit: sub.deposit || 0,
                    status: 'Ошибка',
                    status_type: 'error'
                });
            }
        }
        
        return enrichedData;
    }
    // Генератор отчета по ценам книг
    async generateBookPricesReport() {
        console.log('📊 Generating book prices report...');
        
        const filtersDiv = document.getElementById('report-filters');
        const minPriceInput = filtersDiv ? filtersDiv.querySelector('#report-min_price') : null;
        const maxPriceInput = filtersDiv ? filtersDiv.querySelector('#report-max_price') : null;
        const topicSelect = filtersDiv ? filtersDiv.querySelector('#report-topic_id') : null;
        
        const minPrice = minPriceInput ? parseFloat(minPriceInput.value) || 0 : 0;
        const maxPrice = maxPriceInput ? parseFloat(maxPriceInput.value) || 10000 : 10000;
        const topicId = topicSelect ? topicSelect.value : null;
        
        console.log(`🎯 Filters - Min: ${minPrice}, Max: ${maxPrice}, Topic: ${topicId}`);
        
        try {
            // Используем детальные книги для отчета
            const response = await fetch('/api/books/detailed/');
            if (!response.ok) {
                throw new Error('Failed to fetch detailed books');
            }
            
            const books = await response.json();
            console.log('📚 Books for report:', books);
            
            if (books.length === 0) {
                return [{
                    book_title: "Нет данных о книгах",
                    author_name: "-",
                    topic_name: "-", 
                    library_name: "-",
                    price: 0,
                    quantity: 0,
                    publish_year: "-"
                }];
            }
            
            // Фильтруем книги по цене
            let filteredBooks = books.filter(book => {
                const price = book.price ? parseFloat(book.price) : 0;
                const meetsPrice = price >= minPrice && price <= maxPrice;
                
                // Если выбрана тема, фильтруем по теме
                let meetsTopic = true;
                if (topicId) {
                    // Получаем информацию о теме для фильтрации
                    meetsTopic = book.topic_id == topicId;
                }
                
                return meetsPrice && meetsTopic;
            });
            
            console.log(`🎯 Filtered books: ${filteredBooks.length} of ${books.length}`);
            
            // Сортируем по цене (по убыванию)
            filteredBooks.sort((a, b) => {
                const priceA = a.price ? parseFloat(a.price) : 0;
                const priceB = b.price ? parseFloat(b.price) : 0;
                return priceB - priceA;
            });
            
            // Форматируем данные для отчета
            const reportData = filteredBooks.map(book => ({
                book_title: book.title || 'Без названия',
                author_name: book.author_name || 'Неизвестен',
                topic_name: book.topic_name || 'Без темы',
                library_name: book.library_name || 'Неизвестна',
                price: book.price ? parseFloat(book.price).toFixed(2) : '0.00',
                quantity: book.quantity || 0,
                publish_year: book.publish_year || 'Не указан'
            }));
            
            return reportData;
            
        } catch (error) {
            console.error('Error generating book prices report:', error);
            
            // Возвращаем тестовые данные
            return [
                {
                    book_title: "Тестовая книга 1",
                    author_name: "Тестовый автор",
                    topic_name: "Художественная литература",
                    library_name: "Центральная библиотека",
                    price: "500.00",
                    quantity: 5,
                    publish_year: 2023
                },
                {
                    book_title: "Тестовая книга 2", 
                    author_name: "Другой автор",
                    topic_name: "Научная литература",
                    library_name: "Центральная библиотека",
                    price: "750.50",
                    quantity: 3,
                    publish_year: 2024
                }
            ];
        }
    }
    

    // Вызовите в консоли: window.libraryApp.checkReportsAvailability()
    }

// Запуск приложения
document.addEventListener('DOMContentLoaded', () => {
    console.log("📚 Library App starting...");
    window.libraryApp = new LibraryApp();
});