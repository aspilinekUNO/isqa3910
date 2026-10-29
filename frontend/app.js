document.addEventListener('DOMContentLoaded', () => {
  const topicDropdown = document.querySelector('.topic-dropdown');
  const topicSummary = document.getElementById('topic-selected');
  const topicItems = document.querySelectorAll('.topic-dropdown .menu-item');
  const topicValue = () => document.querySelector('.topic-dropdown .menu-item.active')?.dataset.topic || 'Students';
  const schoolDropdown = document.querySelector('.school-dropdown');
  const schoolSummary = document.getElementById('school-selected');
  const schoolItems = document.querySelectorAll('.school-dropdown .menu-item');
  const questionForm = document.getElementById('question-form');
  const questionInput = document.querySelector('.composer input');
  const resetFiltersButton = document.getElementById('reset-filters');
  const chatWindow = document.getElementById('chat-window');

  const createTimeStamp = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  };

  const getSelectedSchool = () => {
    const activeItem = document.querySelector('.school-dropdown .menu-item.active');
    return activeItem ? activeItem.dataset.school : 'Andersen Middle School';
  };

  const buildAssistantReply = (question) => {
    const topic = topicValue();
    const school = getSelectedSchool();
    const lowerQuestion = question.toLowerCase();

    if (lowerQuestion.includes('form') || lowerQuestion.includes('clearance') || lowerQuestion.includes('application')) {
      return {
        text: `I found the relevant ${topic.toLowerCase()} information for ${school}.`,
        table: {
          rows: [
            { label: 'School', value: school },
            { label: 'Topic', value: topic },
            { label: 'Resource', value: 'Athletic Pre-Participation Clearance Form' },
          ],
        },
      };
    }

    if (lowerQuestion.includes('deadline') || lowerQuestion.includes('due') || lowerQuestion.includes('when')) {
      return {
        text: `For ${school}, the most relevant ${topic.toLowerCase()} deadline depends on the specific item. Here’s the current guidance:`,
        table: {
          rows: [
            { label: 'School', value: school },
            { label: 'Topic', value: topic },
            { label: 'Status', value: 'Updated for the current school year' },
          ],
        },
      };
    }

    return {
      text: `I checked the ${topic.toLowerCase()} guidance for ${school}. Here is the most relevant summary:`,
      table: {
        rows: [
          { label: 'School', value: school },
          { label: 'Topic', value: topic },
          { label: 'Answer', value: 'Please review the official school page for the most current details.' },
        ],
      },
    };
  };

  const renderMessage = (role, content, table) => {
    if (!chatWindow) {
      return;
    }

    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${role === 'user' ? 'user-row' : 'assistant-row'}`;

    if (role === 'assistant') {
      const avatar = document.createElement('div');
      avatar.className = 'assistant-avatar';
      avatar.setAttribute('aria-label', 'Assistant message');

      const logo = document.createElement('img');
      logo.src = '/static/assets/logo.jpg';
      logo.alt = 'Assistant logo';
      logo.className = 'assistant-avatar-image';
      avatar.appendChild(logo);

      messageRow.appendChild(avatar);
    }

    const bubble = document.createElement(role === 'user' ? 'div' : 'div');
    bubble.className = role === 'user' ? 'user-bubble' : 'assistant-card';
    bubble.textContent = content;

    if (role === 'assistant' && table) {
      const tableWrap = document.createElement('div');
      tableWrap.className = 'result-table';
      tableWrap.setAttribute('role', 'table');

      const header = document.createElement('div');
      header.className = 'table-header';
      header.setAttribute('role', 'row');
      header.innerHTML = '<div role="columnheader">Field</div><div role="columnheader">Value</div>';

      const rows = document.createElement('div');
      rows.className = 'table-rows';

      table.rows.forEach((row) => {
        const tableRow = document.createElement('div');
        tableRow.className = 'table-row';
        tableRow.setAttribute('role', 'row');
        tableRow.innerHTML = `
          <div role="cell">${row.label}</div>
          <div role="cell">${row.value}</div>
        `;
        rows.appendChild(tableRow);
      });

      tableWrap.appendChild(header);
      tableWrap.appendChild(rows);
      bubble.appendChild(tableWrap);
    }

    const time = document.createElement('div');
    time.className = 'timestamp';
    time.textContent = createTimeStamp();

    if (role === 'user') {
      messageRow.appendChild(bubble);
      messageRow.appendChild(time);
    } else {
      const contentWrap = document.createElement('div');
      contentWrap.className = 'assistant-content';
      const intro = document.createElement('p');
      intro.textContent = content;
      contentWrap.appendChild(intro);
      if (table) {
        const tableWrap = document.createElement('div');
        tableWrap.className = 'result-table';
        tableWrap.setAttribute('role', 'table');
        const header = document.createElement('div');
        header.className = 'table-header';
        header.setAttribute('role', 'row');
        header.innerHTML = '<div role="columnheader">Field</div><div role="columnheader">Value</div>';
        const rows = document.createElement('div');
        rows.className = 'table-rows';

        table.rows.forEach((row) => {
          const tableRow = document.createElement('div');
          tableRow.className = 'table-row';
          tableRow.setAttribute('role', 'row');
          tableRow.innerHTML = `
            <div role="cell">${row.label}</div>
            <div role="cell">${row.value}</div>
          `;
          rows.appendChild(tableRow);
        });

        tableWrap.appendChild(header);
        tableWrap.appendChild(rows);
        contentWrap.appendChild(tableWrap);
      }
      bubble.innerHTML = '';
      bubble.appendChild(contentWrap);
      messageRow.appendChild(bubble);
    }

    chatWindow.appendChild(messageRow);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  };

  const addAssistantReply = (question) => {
    const reply = buildAssistantReply(question);
    renderMessage('assistant', reply.text, reply.table);
  };

  const seedWelcomeMessage = () => {
    if (!chatWindow || chatWindow.children.length > 0) {
      return;
    }

    renderMessage('assistant', 'Hi! Ask me about the selected topic and school, and I’ll summarize the most relevant information.', null);
  };

  const syncTopicSummary = () => {
    if (topicSummary) {
      topicSummary.textContent = topicValue();
    }
    topicItems.forEach((item) => item.classList.toggle('active', item.dataset.topic === topicValue()));
  };

  const syncSchoolSummary = () => {
    const selectedSchool = getSelectedSchool();
    if (schoolSummary) {
      schoolSummary.textContent = selectedSchool;
    }
    schoolItems.forEach((item) => item.classList.toggle('active', item.dataset.school === selectedSchool));
  };

  topicItems.forEach((item) => {
    item.addEventListener('click', () => {
      topicItems.forEach((menuItem) => menuItem.classList.toggle('active', menuItem === item));
      syncTopicSummary();
      if (topicDropdown) {
        topicDropdown.removeAttribute('open');
      }
    });
  });

  schoolItems.forEach((item) => {
    item.addEventListener('click', () => {
      schoolItems.forEach((menuItem) => menuItem.classList.toggle('active', menuItem === item));
      syncSchoolSummary();
      if (schoolDropdown) {
        schoolDropdown.removeAttribute('open');
      }
    });
  });

  if (resetFiltersButton) {
    resetFiltersButton.addEventListener('click', () => {
      const defaultTopic = 'Students';
      const defaultSchool = 'Andersen Middle School';

      topicItems.forEach((item) => item.classList.toggle('active', item.dataset.topic === defaultTopic));
      schoolItems.forEach((item) => item.classList.toggle('active', item.dataset.school === defaultSchool));
      syncTopicSummary();
      syncSchoolSummary();
      if (topicDropdown) {
        topicDropdown.removeAttribute('open');
      }
      if (schoolDropdown) {
        schoolDropdown.removeAttribute('open');
      }
    });
  }

  syncTopicSummary();
  syncSchoolSummary();

  if (questionForm && questionInput) {
    questionForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const value = questionInput.value.trim();
      if (!value) {
        questionInput.focus();
        return;
      }

      renderMessage('user', value, null);
      questionInput.value = '';
      questionInput.placeholder = 'Ask a question...';

      window.setTimeout(() => {
        addAssistantReply(value);
      }, 250);
    });
  }

  seedWelcomeMessage();
});
