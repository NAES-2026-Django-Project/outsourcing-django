document.querySelectorAll('.toast').forEach((el) => {
  new bootstrap.Toast(el, { delay: 4000 }).show();
});
