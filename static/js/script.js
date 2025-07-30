function criarAcesso() {
    // ... (validações iguais)

    fetch('https://projeto-web-fmx8.onrender.com/api/criar-acesso', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome: nome.value,
                email: email1.value,
                cargo: cargo.value,
                senha: senha1.value
            })
        })
        .then(async response => {
            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                alert(data.mensagem || data.erro);
            } else {
                const texto = await response.text();
                alert("Erro inesperado do servidor: " + texto);
            }
        })
        .catch(error => alert("Erro ao criar acesso: " + error.message))
        .finally(() => {
            botao.disabled = false;
            botao.innerText = 'Criar Acesso';
        });
}

function enviarLink() {
    const email = document.getElementById("email").value.trim();
    const mensagemDiv = document.getElementById("mensagem"); // ou 'mensagemErro', se mudar o HTML

    mensagemDiv.textContent = ""; // limpa mensagem anterior

    if (!email) {
        mensagemDiv.textContent = "Informe o e-mail.";
        mensagemDiv.style.color = "red";
        return;
    }

    fetch("https://projeto-web-fmx8.onrender.com/api/esqueci-senha", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        })
        .then(async response => {
            const resultado = await response.json();
            return { status: response.ok, dados: resultado };
        })
        .then(({ status, dados }) => {
            if (status) {
                mensagemDiv.style.color = "green";
                mensagemDiv.textContent = dados.mensagem;
                alert("Sua nova senha foi enviada para o e-mail informado.");
                setTimeout(() => { window.location.href = "/login"; }, 2000);
            } else {
                mensagemDiv.style.color = "red";
                mensagemDiv.textContent = dados.erro || "Erro desconhecido.";
            }
        })
        .catch(() => {
            mensagemDiv.style.color = "red";
            mensagemDiv.textContent = "Erro ao enviar requisição. Verifique sua conexão.";
        });
}

function fazerLogin() {
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value.trim();
    const mensagemErro = document.getElementById("mensagemErro");

    mensagemErro.textContent = "";

    if (!email || !senha) {
        mensagemErro.textContent = "Por favor, preencha email e senha.";
        return;
    }

    fetch("https://projeto-web-fmx8.onrender.com/api/login", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, senha }),
        })
        .then(async res => {
            const data = await res.json();
            if (res.ok) {
                // Login bem-sucedido
                return fetch("https://projeto-web-fmx8.onrender.com/api/colaborador", {
                        credentials: "include",
                    })
                    .then(res => res.json())
                    .then(usuario => {
                        if (usuario.nome && usuario.email) {
                            localStorage.setItem("nomeColaborador", usuario.nome);
                            localStorage.setItem("emailColaborador", usuario.email);
                            window.location.href = "/intro";
                        } else {
                            mensagemErro.textContent = "Sessão inválida. Tente novamente.";
                        }
                    });
            } else {
                mensagemErro.textContent = data.erro || "Email ou senha inválidos.";
            }
        })
        .catch(err => {
            mensagemErro.textContent = "Erro ao fazer login. Verifique sua conexão.";
            console.error(err);
        });
}