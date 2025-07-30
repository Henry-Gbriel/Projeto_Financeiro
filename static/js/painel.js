document.addEventListener("DOMContentLoaded", function() {
    //Espera um curto tempo para garantir que o localStorage foi preenchido após login
    setTimeout(() => {
        const nomeColaborador = localStorage.getItem("nomeColaborador");
        const emailColaborador = localStorage.getItem("emailColaborador");

        if (!nomeColaborador || !emailColaborador) {
            console.warn("Redirecionando para /login: nome ou email não encontrados no localStorage");
            window.location.href = "/login";
            return;
        }

        //Exibe o nome do colaborador na tela
        const welcomeSpan = document.querySelector(".welcome span");
        if (welcomeSpan) {
            welcomeSpan.textContent = nomeColaborador;
        }

        //Navegação do menu lateral
        document.querySelectorAll(".menu li").forEach((item) => {
            item.addEventListener("click", () => {
                const destino = item.getAttribute("data-link");
                if (destino) {
                    let rota = destino;

                    switch (destino) {
                        case "intro.html":
                            rota = "/intro";
                            break;
                        case "login.html":
                            rota = "/login";
                            localStorage.removeItem("nomeColaborador");
                            localStorage.removeItem("emailColaborador");
                            break;
                        case "dashboard.html":
                            rota = "/dashboard";
                            break;
                        case "his.html":
                            rota = "/historico";
                            break;
                        case "envio.html":
                            rota = "/envio";
                            break;
                    }

                    window.location.href = rota;
                }
            });
        });

        //Botão de upload de arquivos
        const btnUpload = document.querySelector(".btn-upload");
        if (btnUpload) {
            btnUpload.addEventListener("click", () => {
                const inputFile = document.createElement("input");
                inputFile.type = "file";
                inputFile.accept = ".csv,.xlsx";
                inputFile.onchange = (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        alert(`Arquivo selecionado: ${file.name}`);
                    }
                };
                inputFile.click();
            });
        }

        //Botão para reportar erro (chamado)
        const btnError = document.querySelector(".btn-error");
        if (btnError) {
            btnError.addEventListener("click", () => {
                fetch("https://projeto-web-fmx8.onrender.com/api/chamado", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        credentials: "include",
                        body: JSON.stringify({
                            nome: nomeColaborador,
                            email: emailColaborador,
                        }),
                    })
                    .then((res) => {
                        if (!res.ok) throw new Error(`Status ${res.status}`);
                        return res.json();
                    })
                    .then((data) => {
                        if (data.status === "ok") {
                            alert("Seu chamado foi enviado. A equipe entrará em contato.");
                        } else {
                            alert("Erro ao enviar chamado: " + (data.mensagem || "Erro desconhecido"));
                        }
                    })
                    .catch((err) => {
                        alert("Erro na requisição do chamado: " + err.message);
                    });
            });
        }
    }, 100); // Aguarda 100 milissegundos
});