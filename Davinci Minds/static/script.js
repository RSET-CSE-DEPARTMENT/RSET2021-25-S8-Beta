// Event listeners for menu buttons
document.getElementById('generate-notes').addEventListener('click', () => {
  toggleContent('notes-content');
  adjustLayout(3, 2);
});

document.getElementById('generate-flowchart').addEventListener('click', () => {
  toggleContent('flowchart-content');
  adjustLayout(3, 2);
});

document.getElementById('generate-summary').addEventListener('click', () => {
  toggleContent('summary-content');
  adjustLayout(3, 2);
});

// Function to show selected content
function toggleContent(contentId) {
  const allContents = document.querySelectorAll('.content-item');
  allContents.forEach(content => content.classList.remove('active')); // Hide all content

  document.getElementById(contentId).classList.add('active'); // Show selected content
}

// Function to adjust layout
function adjustLayout(videoRatio, contentRatio) {
  document.getElementById('video-section').style.flex = videoRatio;
  document.getElementById('content-section').style.flex = contentRatio;
}

// Close content and return to full video view
function closeContent() {
  document.querySelectorAll('.content-item').forEach(content => content.classList.remove('active'));

  document.getElementById('video-section').style.flex = "1"; // Full width
  document.getElementById('content-section').style.flex = "0"; // Hide content section
}

// Ensure default layout on page load
document.addEventListener("DOMContentLoaded", closeContent);
