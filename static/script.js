class GeminiAeon {
    constructor() {
        this.isThinking = false;
        this.currentTheme = 'light';
        this.attachedFiles = [];
        this.currentMode = 'ai'; // 'ai', 'web', 'auto'
        this.chatHistory = [];
        this.currentChatId = this.generateChatId();

        this.initializeElements();
        this.setupEventListeners();
        this.loadTheme();
        this.loadChatHistory();
        this.loadModePreference();
        this.initializeWelcomeScreen();
    }

    generateChatId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeElements() {
        // Core elements
        this.sidebar = document.getElementById('sidebar');
        this.menuToggle = document.getElementById('menuToggle');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.chatArea = document.getElementById('chatArea');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.thinkingIndicator = document.getElementById('thinkingIndicator');
        this.chatHistoryContainer = document.getElementById('chatHistory');

        // Mode elements
        this.aiModeBtn = document.getElementById('aiModeBtn');
        this.webModeBtn = document.getElementById('webModeBtn');
        this.autoModeBtn = document.getElementById('autoModeBtn');
        this.modeBadge = document.getElementById('modeBadge');
        this.modeHint = document.getElementById('modeHint');
        this.modeIndicator = document.getElementById('modeIndicator');
        // NOTE: removed currentModeElement because the HTML doesn't have #currentMode

        // Input elements
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.attachBtn = document.getElementById('attachBtn');
        this.imageBtn = document.getElementById('imageBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.fileInput = document.getElementById('fileInput');
        this.imageInput = document.getElementById('imageInput');
        this.themeToggle = document.getElementById('themeToggle'); // <- FIXED: was missing

        // Modals and previews
        this.uploadPreview = document.getElementById('uploadPreview');
        this.previewItems = document.getElementById('previewItems');
        this.clearPreview = document.getElementById('clearPreview');
        this.settingsModal = document.getElementById('settingsModal');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsClose = document.getElementById('settingsClose');

        // Quick prompts
        this.promptChips = document.querySelectorAll('.prompt-chip');
        this.newChatBtn = document.getElementById('newChatBtn');
    }

    setupEventListeners() {
        // Guard existence before binding listeners (prevents null-read errors)
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (this.messageInput) {
            this.messageInput.addEventListener('input', () => {
                this.autoResizeTextarea();
                this.updateSendButton();
            });

            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    if (e.shiftKey) return;
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Mode selection
        if (this.aiModeBtn) this.aiModeBtn.addEventListener('click', () => this.setMode('ai'));
        if (this.webModeBtn) this.webModeBtn.addEventListener('click', () => this.setMode('web'));
        if (this.autoModeBtn) this.autoModeBtn.addEventListener('click', () => this.setMode('auto'));

        // File handling
        if (this.attachBtn) this.attachBtn.addEventListener('click', () => this.fileInput && this.fileInput.click());
        if (this.imageBtn) this.imageBtn.addEventListener('click', () => this.imageInput && this.imageInput.click());
        if (this.fileInput) this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        if (this.imageInput) this.imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
        if (this.clearPreview) this.clearPreview.addEventListener('click', () => this.clearAttachedFiles());

        // Voice input
        if (this.voiceBtn) this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());

        // UI controls
        if (this.menuToggle) this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        if (this.sidebarToggle) this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        if (this.themeToggle) this.themeToggle.addEventListener('click', () => this.toggleTheme());
        if (this.settingsBtn) this.settingsBtn.addEventListener('click', () => this.showSettings());
        if (this.settingsClose) this.settingsClose.addEventListener('click', () => this.hideSettings());

        // Quick prompts
        if (this.promptChips) {
            this.promptChips.forEach(chip => {
                chip.addEventListener('click', (e) => {
                    // support clicks on inner text elements
                    const prompt = chip.getAttribute('data-prompt') || (e.target && e.target.getAttribute && e.target.getAttribute('data-prompt'));
                    if (!prompt) return;
                    this.messageInput.value = prompt;
                    this.autoResizeTextarea();
                    this.updateSendButton();
                    this.messageInput.focus();
                });
            });
        }

        if (this.newChatBtn) this.newChatBtn.addEventListener('click', () => this.startNewChat());

        // Close modal when clicking outside
        if (this.settingsModal) {
            this.settingsModal.addEventListener('click', (e) => {
                if (e.target === this.settingsModal) {
                    this.hideSettings();
                }
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                const key = e.key.toLowerCase();
                if (key === 'k') {
                    e.preventDefault();
                    this.messageInput && this.messageInput.focus();
                } else if (key === 'n') {
                    e.preventDefault();
                    this.startNewChat();
                } else if (key === 'l') {
                    e.preventDefault();
                    this.clearCurrentChat();
                } else if (key === '1') {
                    e.preventDefault();
                    this.setMode('ai');
                } else if (key === '2') {
                    e.preventDefault();
                    this.setMode('web');
                } else if (key === '3') {
                    e.preventDefault();
                    this.setMode('auto');
                }
            }
        });
    }

    initializeWelcomeScreen() {
        // Show welcome screen by default
        if (this.welcomeScreen && this.messagesContainer) {
            this.welcomeScreen.style.display = 'flex';
            this.messagesContainer.style.display = 'none';
        }
    }

    autoResizeTextarea() {
        const textarea = this.messageInput;
        if (!textarea) return;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    updateSendButton() {
        if (!this.sendButton || !this.messageInput) return;
        const hasText = this.messageInput.value.trim().length > 0;
        const hasFiles = this.attachedFiles.length > 0;
        this.sendButton.disabled = !(hasText || hasFiles) || this.isThinking;
    }

    setMode(mode) {
        this.currentMode = mode;

        // Update mode buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`[data-mode="${mode}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        // Update mode badge
        this.updateModeBadge();

        // Update mode hint
        this.updateModeHint();

        // Update welcome screen mode cards
        this.updateWelcomeModeCards();

        // Save mode preference
        this.saveModePreference();
    }

    updateModeBadge() {
        const modeConfig = {
            'ai': { icon: 'psychology', text: 'AI', className: '' },
            'web': { icon: 'search', text: 'Web', className: 'web' },
            'auto': { icon: 'auto_awesome', text: 'Auto', className: 'auto' }
        };

        const config = modeConfig[this.currentMode] || modeConfig.ai;
        if (!this.modeBadge) return;
        this.modeBadge.className = `mode-badge ${config.className}`;
        this.modeBadge.innerHTML = `
            <span class="material-symbols-outlined">${config.icon}</span>
            ${config.text}
        `;
    }

    updateModeHint() {
        if (!this.modeHint) return;
        const hints = {
            'ai': 'AI Mode: Creative tasks, coding, general knowledge',
            'web': 'Web Search Mode: Real-time information, news, current events',
            'auto': 'Auto Mode: Smart detection between AI and web search'
        };

        this.modeHint.textContent = hints[this.currentMode] || hints.ai;
    }

    updateWelcomeModeCards() {
        document.querySelectorAll('.mode-card').forEach(card => {
            card.classList.remove('active');
        });
        const selected = document.querySelector(`.mode-card[data-mode="${this.currentMode}"]`);
        if (selected) selected.classList.add('active');
    }

    updateModeIndicator(modeUsed) {
        if (!this.modeIndicator) return;
        const indicators = {
            'ai': '🤖 Using AI Intelligence',
            'web': '🔍 Searching the Web',
            'auto': '⚡ Auto Mode Active'
        };

        this.modeIndicator.textContent = indicators[modeUsed] || '';
    }

    loadModePreference() {
        const savedMode = localStorage.getItem('aeon-mode') || 'ai';
        this.setMode(savedMode);
    }

    saveModePreference() {
        localStorage.setItem('aeon-mode', this.currentMode);
    }

    async sendMessage() {
        const message = this.messageInput ? this.messageInput.value.trim() : '';
        const hasFiles = this.attachedFiles.length > 0;

        if ((!message && !hasFiles) || this.isThinking) return;

        // Hide welcome screen on first message
        if (this.welcomeScreen && this.welcomeScreen.style.display !== 'none' && this.messagesContainer) {
            this.welcomeScreen.style.display = 'none';
            this.messagesContainer.style.display = 'block';
        }

        // Add user message to chat
        this.addMessage(message, 'user', this.attachedFiles);
        if (this.messageInput) {
            this.messageInput.value = '';
            this.autoResizeTextarea();
        }
        this.clearAttachedFiles();
        this.updateSendButton();

        // Show thinking animation with mode indicator
        this.setThinkingState(true);
        this.updateModeIndicator(this.currentMode);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    files: this.attachedFiles,
                    mode: this.currentMode // Send the current mode to backend
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Update current chat in history
                this.updateChatHistory(message, data.response);
                // Add assistant message with fast typewriter effect
                await this.addMessageWithTypewriter(data.response, 'assistant', data.modeUsed || this.currentMode);
            } else {
                throw new Error(data.error || 'Failed to get response from server');
            }
        } catch (error) {
            this.addMessage(`I apologize, but I encountered an error: ${error.message}`, 'assistant');
        } finally {
            this.setThinkingState(false);
        }
    }

    addMessage(content, role, files = [], modeUsed = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const avatar = role === 'user' ?
            `<div class="gemini-avatar user-avatar">You</div>` :
            `<div class="gemini-avatar">∞</div>`;

        let filesHTML = '';
        if (files && files.length > 0) {
            filesHTML = `
                <div class="message-files">
                    ${files.map(file => `
                        <div class="file-preview">
                            <span class="material-symbols-outlined">${file.type && file.type.startsWith('image/') ? 'image' : 'description'}</span>
                            <span>${file.name}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // Add mode indicator for assistant messages
        let modeIndicator = '';
        if (role === 'assistant' && modeUsed) {
            const modeLabels = {
                'ai': 'AI',
                'web': 'Web Search',
                'auto': 'Auto'
            };
            modeIndicator = `<span class="message-mode-indicator">${modeLabels[modeUsed] || ''}</span>`;
        }

        // Process content for code blocks and formatting
        const processedContent = this.processContent(content || '');

        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-avatar">
                    ${avatar}
                </div>
                <div class="message-text">
                    ${filesHTML}
                    ${processedContent}
                    ${modeIndicator}
                    <div class="message-time">${timestamp}</div>
                </div>
            </div>
        `;

        this.messagesContainer && this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Add copy functionality to code blocks
        this.initializeCodeBlocks(messageDiv);

        return messageDiv;
    }

    async addMessageWithTypewriter(content, role, modeUsed = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const avatar = `<div class="gemini-avatar">∞</div>`;

        // Add mode indicator for assistant messages
        let modeIndicator = '';
        if (role === 'assistant' && modeUsed) {
            const modeLabels = {
                'ai': 'AI',
                'web': 'Web Search',
                'auto': 'Auto'
            };
            modeIndicator = `<span class="message-mode-indicator">${modeLabels[modeUsed] || ''}</span>`;
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-avatar">
                    ${avatar}
                </div>
                <div class="message-text">
                    <div class="message-content-text"></div>
                    ${modeIndicator}
                    <div class="message-time">${timestamp}</div>
                </div>
            </div>
        `;

        this.messagesContainer && this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        const contentElement = messageDiv.querySelector('.message-content-text');
        await this.fastTypewriterEffect(contentElement, content || '');

        // Process content for code blocks after typing is complete
        const processedContent = this.processContent(content || '');
        contentElement.innerHTML = processedContent;
        this.initializeCodeBlocks(messageDiv);

        return messageDiv;
    }

    async fastTypewriterEffect(element, text) {
        if (!element) return;
        return new Promise((resolve) => {
            let i = 0;
            const speed = 6; // small delay for readability (ms per chunk)
            const chunkSize = 4;

            function type() {
                if (i < text.length) {
                    const chunk = text.substring(i, i + chunkSize);
                    element.textContent += chunk;
                    i += chunkSize;
                    setTimeout(type, speed);
                } else {
                    resolve();
                }
            }

            // Start typing
            type();
        });
    }

    processContent(content) {
        // Convert markdown-like syntax to HTML
        let processed = String(content || '');

        // Code blocks - preserve indentation and escape
        processed = processed.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            const language = lang || 'text';
            return `
                <div class="code-block">
                    <div class="code-header">
                        <span class="code-language">${language}</span>
                        <button class="copy-code">
                            <span class="material-symbols-outlined">content_copy</span>
                            Copy
                        </button>
                    </div>
                    <pre class="code-content">${this.escapeHtml(code.trim())}</pre>
                </div>
            `;
        });

        // Inline code
        processed = processed.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold (do this before italic)
        processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic - avoid matching the bold syntax by requiring not-surrounded-by another *
        processed = processed.replace(/(^|[^*])\*([^*]+)\*([^*]|$)/g, '$1<em>$2</em>$3');

        // Line breaks
        processed = processed.replace(/\n/g, '<br>');

        return processed;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    initializeCodeBlocks(container) {
        const codeBlocks = container.querySelectorAll('.code-block');
        codeBlocks.forEach(block => {
            const copyBtn = block.querySelector('.copy-code');
            if (!copyBtn) return;
            // Avoid adding duplicate listeners by cloning or using a flag
            if (copyBtn.dataset.listenerAttached) return;
            copyBtn.dataset.listenerAttached = '1';

            copyBtn.addEventListener('click', () => {
                const codeEl = block.querySelector('.code-content');
                const codeContent = codeEl ? codeEl.textContent : '';
                this.copyToClipboard(codeContent);

                // Show copied feedback
                const originalHTML = copyBtn.innerHTML;
                copyBtn.innerHTML = '<span class="material-symbols-outlined">check</span>Copied!';
                setTimeout(() => {
                    copyBtn.innerHTML = originalHTML;
                }, 2000);
            });
        });
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }

    setThinkingState(thinking) {
        this.isThinking = thinking;
        if (!this.thinkingIndicator || !this.sendButton) return;
        if (thinking) {
            this.thinkingIndicator.classList.add('active');
            this.sendButton.disabled = true;
        } else {
            this.thinkingIndicator.classList.remove('active');
            this.updateSendButton();
        }
    }

    scrollToBottom() {
        if (!this.messagesContainer) return;
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    // File handling methods
    handleFileUpload(event) {
        const files = Array.from(event.target.files || []);
        this.attachedFiles.push(...files);
        this.updateFilePreview();
        event.target.value = '';
    }

    handleImageUpload(event) {
        const files = Array.from(event.target.files || []);
        files.forEach(file => {
            if (file.type && file.type.startsWith('image/')) {
                this.attachedFiles.push(file);
            }
        });
        this.updateFilePreview();
        event.target.value = '';
    }

    updateFilePreview() {
        if (!this.uploadPreview || !this.previewItems) return;

        if (this.attachedFiles.length === 0) {
            this.uploadPreview.classList.remove('active');
            this.previewItems.innerHTML = '';
            return;
        }

        this.uploadPreview.classList.add('active');
        this.previewItems.innerHTML = '';

        this.attachedFiles.forEach((file) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';

            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-file-btn';
            removeBtn.innerHTML = `<span class="material-symbols-outlined">close</span>`;

            // Remove listener determines the current index of this file by matching identity (name, size, lastModified)
            removeBtn.addEventListener('click', () => {
                const idx = this.attachedFiles.findIndex(f =>
                    f.name === file.name &&
                    f.size === file.size &&
                    f.lastModified === file.lastModified
                );
                if (idx !== -1) {
                    this.removeFile(idx);
                }
            });

            if (file.type && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewItem.innerHTML = `
                        <img src="${e.target.result}" alt="${this.escapeHtml(file.name)}">
                        <span>${this.escapeHtml(file.name)}</span>
                    `;
                    previewItem.appendChild(removeBtn);
                };
                reader.readAsDataURL(file);
            } else {
                previewItem.innerHTML = `
                    <span class="material-symbols-outlined">description</span>
                    <span>${this.escapeHtml(file.name)}</span>
                `;
                previewItem.appendChild(removeBtn);
            }

            this.previewItems.appendChild(previewItem);
        });

        this.updateSendButton();
    }

    removeFile(index) {
        if (index < 0 || index >= this.attachedFiles.length) return;
        this.attachedFiles.splice(index, 1);
        this.updateFilePreview();
    }

    clearAttachedFiles() {
        this.attachedFiles = [];
        this.updateFilePreview();
    }

    // Voice input methods
    toggleVoiceInput() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Speech recognition is not supported in your browser.');
            return;
        }

        // This would be implemented with Web Speech API
        alert('Voice input would be implemented here with Web Speech API');
    }

    // Chat History Management
    loadChatHistory() {
        const savedHistory = localStorage.getItem('aeon-chat-history');
        if (savedHistory) {
            try {
                this.chatHistory = JSON.parse(savedHistory);
            } catch (e) {
                this.chatHistory = [];
            }
            this.renderChatHistory();
        } else {
            this.chatHistory = [];
        }
    }

    saveChatHistory() {
        localStorage.setItem('aeon-chat-history', JSON.stringify(this.chatHistory));
    }

    renderChatHistory() {
        // Keep current active element (if any)
        const currentChatItem = this.chatHistoryContainer ? this.chatHistoryContainer.querySelector('.history-item.active') : null;

        if (!this.chatHistoryContainer) return;

        this.chatHistoryContainer.innerHTML = '';
        if (currentChatItem) {
            // Re-append the current chat item so the "Current conversation" slot stays
            this.chatHistoryContainer.appendChild(currentChatItem);
        }

        // Add history items (most recent first)
        this.chatHistory.slice().reverse().forEach(chat => {
            if (chat.id !== this.currentChatId) {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.dataset.chatId = chat.id;

                const titleSpan = document.createElement('span');
                titleSpan.className = 'history-title';
                titleSpan.textContent = this.truncateText(chat.title || 'Untitled', 30);

                const icon = document.createElement('span');
                icon.className = 'material-symbols-outlined';
                icon.textContent = 'chat';

                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'delete-chat';
                deleteBtn.setAttribute('aria-label', 'Delete chat');
                deleteBtn.innerHTML = `<span class="material-symbols-outlined">delete</span>`;
                deleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.deleteChat(chat.id);
                });

                historyItem.appendChild(icon);
                historyItem.appendChild(titleSpan);
                historyItem.appendChild(deleteBtn);

                historyItem.addEventListener('click', (e) => {
                    if (!e.target.closest('.delete-chat')) {
                        this.loadChat(chat.id);
                    }
                });

                this.chatHistoryContainer.appendChild(historyItem);
            }
        });

        this.updateActiveChatIndicator();
    }

    updateChatHistory(userMessage, assistantMessage) {
        let currentChat = this.chatHistory.find(chat => chat.id === this.currentChatId);

        if (!currentChat) {
            // Create new chat entry
            currentChat = {
                id: this.currentChatId,
                title: this.generateChatTitle(userMessage || ''),
                messages: [],
                createdAt: new Date().toISOString()
            };
            this.chatHistory.push(currentChat);
        }

        // Add messages to chat
        currentChat.messages.push({
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        });

        currentChat.messages.push({
            role: 'assistant',
            content: assistantMessage,
            timestamp: new Date().toISOString()
        });

        // Update title if it's the first message
        if (currentChat.messages.length === 2) {
            currentChat.title = this.generateChatTitle(userMessage || '');
        }

        // Keep only last 50 chats
        if (this.chatHistory.length > 50) {
            this.chatHistory = this.chatHistory.slice(-50);
        }

        this.saveChatHistory();
        this.renderChatHistory();
    }

    generateChatTitle(message) {
        const safe = String(message || '').trim();
        const words = safe.split(/\s+/).filter(Boolean);
        if (words.length <= 5) {
            return safe || 'New Chat';
        }
        return words.slice(0, 5).join(' ') + '...';
    }

    truncateText(text, maxLength) {
        const str = String(text || '');
        if (str.length <= maxLength) return str;
        return str.substring(0, maxLength) + '...';
    }

    loadChat(chatId) {
        const chat = this.chatHistory.find(c => c.id === chatId);
        if (!chat) return;

        this.currentChatId = chatId;

        // Clear current messages
        if (this.messagesContainer) this.messagesContainer.innerHTML = '';

        // Load chat messages
        chat.messages.forEach(msg => {
            this.addMessage(msg.content, msg.role);
        });

        // Update UI
        if (this.welcomeScreen) this.welcomeScreen.style.display = 'none';
        if (this.messagesContainer) this.messagesContainer.style.display = 'block';
        this.updateActiveChatIndicator();

        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            this.toggleSidebar();
        }
    }

    updateActiveChatIndicator() {
        if (!this.chatHistoryContainer) return;
        const historyItems = this.chatHistoryContainer.querySelectorAll('.history-item');
        historyItems.forEach(item => {
            item.classList.remove('active');
            if (item.dataset.chatId === this.currentChatId) {
                item.classList.add('active');
            }
        });
    }

    deleteChat(chatId) {
        if (!confirm('Are you sure you want to delete this chat?')) return;
        this.chatHistory = this.chatHistory.filter(chat => chat.id !== chatId);
        this.saveChatHistory();
        this.renderChatHistory();

        // If we deleted the current chat, start a new one
        if (chatId === this.currentChatId) {
            this.startNewChat();
        }
    }

    clearCurrentChat() {
        if (!confirm('Clear the current chat?')) return;
        if (this.messagesContainer) this.messagesContainer.innerHTML = '';
        // Remove current chat from history
        this.chatHistory = this.chatHistory.filter(chat => chat.id !== this.currentChatId);
        this.saveChatHistory();
        this.renderChatHistory();
        this.initializeWelcomeScreen();
    }

    // UI control methods
    toggleSidebar() {
        if (!this.sidebar) return;
        this.sidebar.classList.toggle('active');
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.body.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('aeon-theme', this.currentTheme);

        // Update theme icon
        if (this.themeToggle) {
            const themeIcon = this.themeToggle.querySelector('span');
            if (themeIcon) themeIcon.textContent = this.currentTheme === 'light' ? 'dark_mode' : 'light_mode';
        }
    }

    showSettings() {
        if (!this.settingsModal) return;
        this.settingsModal.classList.add('active');
    }

    hideSettings() {
        if (!this.settingsModal) return;
        this.settingsModal.classList.remove('active');
    }

    startNewChat() {
        this.currentChatId = this.generateChatId();
        if (this.messagesContainer) this.messagesContainer.innerHTML = '';
        if (this.welcomeScreen) this.welcomeScreen.style.display = 'flex';
        if (this.messagesContainer) this.messagesContainer.style.display = 'none';
        if (this.messageInput) this.messageInput.value = '';
        this.clearAttachedFiles();
        this.updateSendButton();
        this.updateActiveChatIndicator();

        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            this.toggleSidebar();
        }
    }

    loadTheme() {
        const savedTheme = localStorage.getItem('aeon-theme') || 'light';
        this.currentTheme = savedTheme;
        document.body.setAttribute('data-theme', this.currentTheme);

        // Set correct theme icon
        if (this.themeToggle) {
            const themeIcon = this.themeToggle.querySelector('span');
            if (themeIcon) themeIcon.textContent = this.currentTheme === 'light' ? 'dark_mode' : 'light_mode';
        }
    }
}

// Initialize the application when DOM is loaded
let aeonApp;
document.addEventListener('DOMContentLoaded', () => {
    aeonApp = new GeminiAeon();
    window.aeonApp = aeonApp; // Make it globally available for debugging if needed
});
