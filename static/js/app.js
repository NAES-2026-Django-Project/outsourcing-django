document.querySelectorAll('.toast').forEach((el) => {
  new bootstrap.Toast(el, { delay: 4000 }).show();
});

// Bootbox: confirma a exclusão sem sair da lista. Sem JavaScript, o link abre a página de confirmação.
$(document).on('click', '[data-excluir]', function (event) {
  event.preventDefault();
  const url = this.href;
  const mensagem = $('<p class="mb-0">').text(`Excluir ${this.dataset.excluir}? Esta ação não pode ser desfeita.`);
  bootbox.confirm({
    title: 'Confirmar exclusão',
    message: mensagem,
    buttons: {
      cancel: { label: 'Cancelar', className: 'btn-outline-secondary' },
      confirm: { label: 'Excluir', className: 'btn-danger' },
    },
    callback(confirmado) {
      if (!confirmado) return;
      const token = $('meta[name="csrf-token"]').attr('content');
      $('<form method="post">')
        .attr('action', url)
        .append($('<input type="hidden" name="csrfmiddlewaretoken">').val(token))
        .appendTo('body')
        .trigger('submit');
    },
  });
});
