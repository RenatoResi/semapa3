// main.js - scripts principais do SEMAPA3

document.addEventListener('DOMContentLoaded', function () {
  console.log('SEMAPA3 main.js carregado com sucesso!');

  // Exemplo: fechar alertas automaticamente após 5 segundos
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function(alert) {
    setTimeout(() => {
      alert.classList.remove('show');
      alert.classList.add('fade');
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // Exemplo: ativar tooltips Bootstrap se estiver usando
  if (typeof bootstrap !== 'undefined') {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"], [data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
      new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }

  // Exemplo: máscara simples para campos de telefone (pode ser melhor com plugin)
  var telInputs = document.querySelectorAll('input[type="tel"]');
  telInputs.forEach(function(input) {
    input.addEventListener('input', function(e) {
      let val = e.target.value.replace(/\D/g, '');
      val = val.substring(0, 11); // limitar
      if (val.length > 6) val = val.replace(/^(\d{2})(\d{5})(\d{0,4}).*/, '($1) $2-$3');
      else if (val.length > 2) val = val.replace(/^(\d{2})(\d{0,5}).*/, '($1) $2');
      else val = val.replace(/^(\d*)/, '($1');
      e.target.value = val;
    });
  });

  // Você pode adicionar seus scripts personalizados abaixo...

  function formatarTelefone(campo) {
      let valor = campo.value.replace(/\D/g, ''); // Remove caracteres não numéricos
      let formato = '';

      if (valor.length <= 10) { // Formato para telefone fixo (XX XXXX-XXXX)
          formato = valor.replace(/^(\d{2})(\d{4})(\d{0,4})$/, '($1) $2-$3');
      } else { // Formato para celular (XX XXXXX-XXXX)
          formato = valor.replace(/^(\d{2})(\d{5})(\d{0,4})$/, '($1) $2-$3');
      }

      campo.value = formato;
  }

  // Verificar se o requerente já existe
  document.addEventListener('DOMContentLoaded', function() {
      const nomeInput = document.getElementById('nome');
      const erroDiv = document.getElementById('nome-erro');

      nomeInput.addEventListener('blur', function() {
          const nome = nomeInput.value.trim();
          if (nome.length < 3) {
              nomeInput.classList.remove('erro');
              erroDiv.style.display = 'none';
              return;
          }
          fetch(`/api/requerente/existe?nome=${encodeURIComponent(nome)}`)
              .then(response => response.json())
              .then(data => {
                  if (data.exists) {
                      nomeInput.classList.add('erro');
                      erroDiv.textContent = `Esse requerente já existe (id=${data.id})`;
                      erroDiv.style.display = 'block';
                  } else {
                      nomeInput.classList.remove('erro');
                      erroDiv.style.display = 'none';
                  }
              })
              .catch(() => {
                  nomeInput.classList.remove('erro');
                  erroDiv.style.display = 'none';
              });
      });
  });
  
});
