// Quadro kanban: arrastar e soltar um cartão em outra coluna move a tarefa de estágio.
// Usa o mesmo POST das setas (TaskMoveView), então a validação e a mensagem de confirmação são as mesmas.
(function () {
  const listas = document.querySelectorAll('.board-lista');
  if (!listas.length || typeof Sortable === 'undefined') return;
  const token = document.querySelector('meta[name="csrf-token"]').content;

  function mover(cartao, estagio) {
    const form = document.createElement('form');
    form.method = 'post';
    form.action = cartao.dataset.mover;
    [['csrfmiddlewaretoken', token], ['stage', estagio]].forEach(([nome, valor]) => {
      const campo = document.createElement('input');
      campo.type = 'hidden';
      campo.name = nome;
      campo.value = valor;
      form.appendChild(campo);
    });
    document.body.appendChild(form);
    form.submit();
  }

  listas.forEach((lista) => {
    Sortable.create(lista, {
      group: 'quadro',
      draggable: '.task-card',
      filter: '.board-empty',
      animation: 150,
      ghostClass: 'arrastando-sombra',
      chosenClass: 'arrastando',
      delay: 200,
      delayOnTouchOnly: true,
      onStart: () => document.querySelector('.board').classList.add('em-arraste'),
      onEnd: (evento) => {
        document.querySelector('.board').classList.remove('em-arraste');
        if (evento.from === evento.to) return;
        evento.item.classList.add('salvando');
        mover(evento.item, evento.to.dataset.estagio);
      },
    });
  });
})();
