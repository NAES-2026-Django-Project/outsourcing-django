// Toasts das mensagens do Django.
document.querySelectorAll('.toast').forEach((el) => {
  new bootstrap.Toast(el, { delay: 4000 }).show();
});

// Tema claro/escuro, guardado no navegador (DESIGN.md §6).
$('#alternar-tema').on('click', () => {
  const tema = document.documentElement.dataset.bsTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.bsTheme = tema;
  try { localStorage.setItem('tema', tema); } catch (e) { /* navegador sem armazenamento */ }
});

// Menu: no desktop recolhe a barra lateral; abaixo de 992px abre a gaveta (offcanvas do Bootstrap).
$('#alternar-menu').on('click', () => {
  if (window.matchMedia('(min-width: 992px)').matches) {
    const recolhido = document.documentElement.classList.toggle('menu-recolhido');
    try { localStorage.setItem('menu-recolhido', recolhido ? '1' : '0'); } catch (e) { /* idem */ }
  } else {
    bootstrap.Offcanvas.getOrCreateInstance('#sidebar').toggle();
  }
});

// Filtros recolhidos no celular.
$(document).on('click', '[data-alternar-filtros]', function () {
  $(`#${this.dataset.alternarFiltros}`).toggleClass('aberto');
});

// Bootbox: confirma a exclusão sem sair da tela. Sem JavaScript, o link abre a página de confirmação.
$(document).on('click', '[data-excluir]', function (event) {
  event.preventDefault();
  const url = this.href;
  const mensagem = $('<p class="mb-0">').text(`Excluir ${this.dataset.excluir}? Esta ação não pode ser desfeita.`);
  bootbox.confirm({
    title: '<span class="modal-ico"><i class="bi bi-exclamation-triangle" aria-hidden="true"></i></span><span>Confirmar exclusão</span>',
    message: mensagem,
    centerVertical: true,
    buttons: {
      cancel: { label: 'Cancelar', className: 'btn-outline-secondary' },
      confirm: { label: '<i class="bi bi-trash3" aria-hidden="true"></i> Excluir', className: 'btn-danger' },
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

// jQuery Mask: telefone com 8 ou 9 dígitos e CEP.
const mascaraTelefone = (valor) => (valor.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009');
$('#id_phone').mask(mascaraTelefone, {
  onKeyPress(valor, evento, campo, opcoes) {
    campo.mask(mascaraTelefone.apply({}, arguments), opcoes);
  },
});
$('#id_cep').mask('00000-000');
