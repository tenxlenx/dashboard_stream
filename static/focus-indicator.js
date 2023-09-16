const iframes = document.querySelectorAll('iframe');

iframes.forEach((iframe) => {
    iframe.addEventListener('focus', function() {
        this.style.outline = '4px solid blue';
    });

    iframe.addEventListener('blur', function() {
        this.style.outline = 'none';
    });
});

function toggleFullScreen(containerId) {
  let container = document.getElementById(containerId);
  if (container) {
    container.classList.toggle('fullscreen');
  } else {
    console.error(`No element with id ${containerId}`);
  }
}
