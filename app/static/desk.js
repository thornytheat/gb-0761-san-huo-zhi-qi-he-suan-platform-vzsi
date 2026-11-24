const picker = document.querySelector('#harbor-sample');
const originals = document.querySelector('#sources');
const form = document.querySelector('.toolbar');
picker.addEventListener('change', () => {
  if (picker.value === 'custom') {
    originals.open = true;
    originals.querySelector('textarea')?.focus();
  }
});
form.addEventListener('submit', () => {
  document.querySelector('#work-feedback').textContent = '正在核算…';
});
