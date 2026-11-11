// Assistente: envia a pergunta por AJAX com o token CSRF e mostra a resposta (HTML já sanitizado no servidor).
$(function () {
  const $form = $('#form-assistente');
  if (!$form.length) return;

  const $mensagens = $('#mensagens');
  const $campo = $('#pergunta');
  const $botao = $form.find('button[type="submit"]');
  const token = $form.find('input[name="csrfmiddlewaretoken"]').val();
  const numero = (valor) => Number(valor).toLocaleString('pt-BR');

  const rolar = () => $mensagens.scrollTop($mensagens[0].scrollHeight);

  function adicionar(classe, conteudo, comoHtml) {
    const $mensagem = $('<div>').addClass(`msg ${classe}`);
    if (comoHtml) $mensagem.html(conteudo);
    else $mensagem.text(conteudo);
    $mensagens.append($mensagem);
    rolar();
    return $mensagem;
  }

  function atualizarCota(dados) {
    if (dados.percentual === undefined) return;
    $('#cota-barra')
      .css('width', `${dados.percentual}%`)
      .toggleClass('bg-danger', dados.percentual >= 90)
      .parent().attr('aria-valuenow', dados.percentual);
    $('#cota-texto').text(`${numero(dados.consumo)} de ${numero(dados.limite)} tokens este mês`);
  }

  function enviar(texto) {
    texto = texto.trim();
    if (!texto || $botao.prop('disabled')) return;
    $mensagens.find('.msg.erro').remove();
    const $pergunta = adicionar('eu', texto, false);
    $campo.val('');
    $botao.prop('disabled', true);
    const $digitando = $('<div class="digitando">O assistente está escrevendo…</div>').appendTo($mensagens);
    rolar();

    $.ajax({
      url: $form.attr('action'),
      method: 'POST',
      data: { pergunta: texto },
      headers: { 'X-CSRFToken': token },
      dataType: 'json',
    })
      .done((dados) => {
        adicionar('bot markdown', dados.resposta_html, true);
        atualizarCota(dados);
      })
      .fail((xhr) => {
        const dados = xhr.responseJSON || {};
        // A pergunta não foi gravada: devolve o texto ao campo para nova tentativa.
        $pergunta.remove();
        $campo.val(texto);
        adicionar('erro', dados.erro || 'Não foi possível enviar a pergunta. Tente novamente.', false).attr('role', 'alert');
        atualizarCota(dados);
      })
      .always(() => {
        $digitando.remove();
        $botao.prop('disabled', false);
        $campo.trigger('focus');
      });
  }

  $form.on('submit', (evento) => {
    evento.preventDefault();
    enviar($campo.val());
  });
  $campo.on('keydown', (evento) => {
    if (evento.key === 'Enter' && !evento.shiftKey) {
      evento.preventDefault();
      enviar($campo.val());
    }
  });
  $('[data-sugestao]').on('click', function () {
    enviar(this.dataset.sugestao);
  });
  rolar();
});
