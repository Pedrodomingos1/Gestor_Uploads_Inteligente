# Manual de Propriedade de Código e Limpeza de Histórico

Este guia foi elaborado para garantir que todo o código deste repositório seja atribuído exclusivamente ao seu usuário (`[Seu Usuário]`), removendo quaisquer vestígios de commits realizados por "Jules" (IA) ou outros colaboradores automáticos.

---

## 🛑 Passo 1: Limpeza de Webhooks e Integrações (GitHub)

Se este repositório estiver conectado a serviços externos (como n8n Cloud ou bots):

1.  Acesse seu repositório no GitHub.
2.  Vá em **Settings** > **Webhooks**.
3.  **Remova** qualquer webhook que você não tenha configurado manualmente (ex: bots de IA que abrem PRs).
4.  Vá em **Settings** > **Integrations** / **GitHub Apps**.
5.  Desinstale apps que prometem "Code Review Automático" ou "Auto-Merge", pois eles deixam rastros nos PRs.

---

## 🧹 Passo 2: Unificar Histórico (Squash Merge)

A maneira mais eficaz de assumir a autoria de todo o trabalho feito até agora é criar um **novo commit único** que contenha todo o estado atual do projeto, assinado por você.

### Opção A: Se você ainda não fez push para a `main` (Local)

1.  Crie uma nova branch "limpa":
    ```bash
    git checkout --orchestrator # Ou a branch atual onde está o código
    git checkout -b feature/minha-implementacao-limpa
    ```
2.  Resete o histórico, mantendo os arquivos (Soft Reset):
    ```bash
    # Volta N commits (substitua N pelo número de commits da IA)
    # Ou, para garantir, volte para o commit inicial (se for seguro)
    git reset --soft HEAD~5
    ```
3.  Faça o commit em seu nome:
    ```bash
    git add .
    git commit -m "Implementação inicial do sistema de automação de vídeo"
    ```
    *Agora o histórico tem apenas 1 commit, e o autor é VOCÊ.*

### Opção B: Se já existem PRs abertos pela IA

1.  Não use o botão "Merge" do GitHub (ele cria um commit de merge que pode citar a IA).
2.  Faça o merge localmente:
    ```bash
    git fetch origin
    git checkout main
    git merge --squash origin/feature-da-ia
    ```
3.  O `--squash` pega todas as mudanças e as deixa no "stage", sem comitar.
4.  Comite manualmente:
    ```bash
    git commit -m "Adiciona funcionalidade de validação de vídeo (Ported)"
    ```
5.  Faça o push:
    ```bash
    git push origin main
    ```

---

## 🛠️ Passo 3: Reescrever Autor (Avançado)

Se você já tem muitos commits e quer manter o histórico detalhado, mas mudar o nome do autor de todos eles para o seu:

1.  Execute este comando (Cuidado: Reescreve histórico!):
    ```bash
    git filter-branch --env-filter '
    export GIT_AUTHOR_NAME="Seu Nome"
    export GIT_AUTHOR_EMAIL="seu@email.com"
    export GIT_COMMITTER_NAME="Seu Nome"
    export GIT_COMMITTER_EMAIL="seu@email.com"
    ' --tag-name-filter cat -- --branches --tags
    ```
2.  Force o push:
    ```bash
    git push --force
    ```

---

## ✅ Checklist Final

- [ ] O arquivo `README.md` tem meu nome na seção de Autoria?
- [ ] O `git log` mostra apenas meu usuário?
- [ ] Não há webhooks desconhecidos em Settings > Webhooks?
- [ ] PRs antigos de automação foram fechados sem merge (ou mergeados via squash)?

**Lembrete:** Como Engenheiro de Software, a integridade do histórico do Git é sua responsabilidade. Use essas ferramentas com sabedoria.
