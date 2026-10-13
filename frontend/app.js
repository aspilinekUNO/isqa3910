const statusBox = document.getElementById('status-box');
const healthButton = document.getElementById('health-button');

const renderStatus = (message, isError = false) => {
  statusBox.textContent = message;
  statusBox.style.color = isError ? '#fca5a5' : '#e2e8f0';
};

healthButton.addEventListener('click', async () => {
  renderStatus('Checking backend...');

  try {
    const response = await fetch('/api/health');
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Request failed');
    }

    renderStatus(JSON.stringify(data, null, 2));
  } catch (error) {
    renderStatus(`Error: ${error.message}`, true);
  }
});
