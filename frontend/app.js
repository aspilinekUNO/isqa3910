document.addEventListener('DOMContentLoaded', async () => {
  const topicDropdown = document.querySelector('.topic-dropdown');
  const topicSummary = document.getElementById('topic-selected');
  const topicItems = document.querySelectorAll('.topic-dropdown .menu-item');
  const topicValue = () => document.querySelector('.topic-dropdown .menu-item.active')?.dataset.topic || 'Students';
  const schoolDropdown = document.querySelector('.school-dropdown');
  const schoolSummary = document.getElementById('school-selected');
  const schoolMenu = document.getElementById('school-menu');
  const questionForm = document.getElementById('question-form');
  const questionInput = document.querySelector('.composer input');
  const resetFiltersButton = document.getElementById('reset-filters');
  const visitSchoolButton = document.getElementById('visit-school-site');
  const chatWindow = document.getElementById('chat-window');
  const defaultSchoolName = 'Andersen Middle School';
  let schoolOptions = [];

  const getSchoolItems = () => document.querySelectorAll('.school-dropdown .menu-item');

  const createTimeStamp = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  };

  const getSelectedSchool = () => {
    const activeItem = document.querySelector('.school-dropdown .menu-item.active');
    return activeItem ? activeItem.dataset.school : defaultSchoolName;
  };

  const getSelectedSchoolUrl = () => {
    const selectedSchool = getSelectedSchool();
    const school = schoolOptions.find((option) => option.name === selectedSchool);
    return school ? school.url : '';
  };

  const renderSchoolMenu = (schools) => {
    if (!schoolMenu) {
      return;
    }

    schoolMenu.innerHTML = '';

    schools.forEach((school) => {
      const menuItem = document.createElement('button');
      menuItem.type = 'button';
      menuItem.className = 'menu-item';
      menuItem.dataset.school = school.name;
      menuItem.dataset.url = school.url;
      menuItem.textContent = school.name;

      if (school.name === defaultSchoolName) {
        menuItem.classList.add('active');
      }

      menuItem.addEventListener('click', () => {
        getSchoolItems().forEach((item) => item.classList.toggle('active', item === menuItem));
        syncSchoolSummary();
        if (schoolDropdown) {
          schoolDropdown.removeAttribute('open');
        }
      });

      schoolMenu.appendChild(menuItem);
    });
  };

  const loadSchoolOptions = async () => {
    try {
      const response = await fetch('/api/schools');
      if (!response.ok) {
        throw new Error(`School list request failed with status ${response.status}`);
      }
      schoolOptions = await response.json();
    } catch (error) {
      console.error('Unable to load school list from CSV:', error);
      schoolOptions = [];
    }

    if (!schoolOptions.length) {
      schoolOptions = [{ name: defaultSchoolName, url: 'https://www.mpsomaha.org/' }];
    }

    renderSchoolMenu(schoolOptions);
    syncSchoolSummary();
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

  const renderResourceResults = (results) => {
    if (!chatWindow) {
      return;
    }

    const messageRow = document.createElement('div');
    messageRow.className = 'message-row assistant-row';

    // Assistant avatar
    const avatar = document.createElement('div');
    avatar.className = 'assistant-avatar';
    avatar.setAttribute('aria-label', 'Assistant message');

    const logo = document.createElement('img');
    logo.src = '/static/assets/logo.jpg';
    logo.alt = 'Assistant logo';
    logo.className = 'assistant-avatar-image';

    avatar.appendChild(logo);
    messageRow.appendChild(avatar);

    // Main response container
    const contentWrap = document.createElement('div');
    contentWrap.className = 'assistant-content';

    const bubble = document.createElement('div');
    bubble.className = 'assistant-card';

    const intro = document.createElement('p');
    intro.textContent = 'I found these resources that may help:';

    bubble.appendChild(intro);

    // Container for all resource cards
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'resource-results';

    results.forEach((result) => {
      const card = document.createElement('div');
      card.className = 'resource-card';

      const title = document.createElement('h3');
      title.className = 'resource-title';
      title.textContent = result.resource_name;

      const category = document.createElement('div');
      category.className = 'resource-category';
      category.textContent =
        `${result.category} › ${result.subcategory}`;

      const description = document.createElement('p');
      description.className = 'resource-description';
      description.textContent = result.description;

      const link = document.createElement('a');
      link.className = 'resource-link';
      link.href = result.source_url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Open Resource ↗';

      card.appendChild(title);
      card.appendChild(category);
      card.appendChild(description);
      card.appendChild(link);

      resultsContainer.appendChild(card);
    });

    bubble.appendChild(resultsContainer);
    contentWrap.appendChild(bubble);

    const time = document.createElement('div');
    time.className = 'timestamp';
    time.textContent = createTimeStamp();

    contentWrap.appendChild(time);
    messageRow.appendChild(contentWrap);

    chatWindow.appendChild(messageRow);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  };

  const addAssistantReply = async (question) => {
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: question
        })
      });

      if (!response.ok) {
        throw new Error('Search request failed');
      }

      const data = await response.json();

      if (data.blocked) {
        renderMessage(
          'assistant',
          'I cannot provide student images or private student information.',
          null
        );
        return;
      }

      if (!data.results || data.results.length === 0) {
        renderMessage(
          'assistant',
          'I could not find a matching MPS resource.',
          null
        );
        return;
      }

      renderResourceResults(data.results);

    } catch (error) {
      console.error(error);

      renderMessage(
        'assistant',
        'I was unable to search MPS resources.',
        null
      );
    }
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
    getSchoolItems().forEach((item) => item.classList.toggle('active', item.dataset.school === selectedSchool));
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

  if (resetFiltersButton) {
    resetFiltersButton.addEventListener('click', () => {
      const defaultTopic = 'Students';

      topicItems.forEach((item) => item.classList.toggle('active', item.dataset.topic === defaultTopic));
      getSchoolItems().forEach((item) => item.classList.toggle('active', item.dataset.school === defaultSchoolName));
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

  if (visitSchoolButton) {
    visitSchoolButton.addEventListener('click', () => {
      const schoolUrl = getSelectedSchoolUrl();
      if (schoolUrl) {
        window.open(schoolUrl, '_blank', 'noopener,noreferrer');
      }
    });
  }

  syncTopicSummary();
  await loadSchoolOptions();

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

      addAssistantReply(value);
    });
  }

  seedWelcomeMessage();
});
