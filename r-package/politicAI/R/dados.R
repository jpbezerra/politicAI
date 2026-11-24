#' Carrega um dataset do estudo
#'
#' @param nome `"unificado"` (Dataset C, A + B harmonizados, 769 linhas),
#'   `"fato_ou_boato"` (Dataset A, TSE, 228 linhas) ou `"aos_fatos"`
#'   (Dataset B, 541 linhas, sem o texto completo das checagens).
#' @return `data.frame`. Colunas de data viram `Date`; no `"aos_fatos"`, `data_publicacao_timestamp` e `POSIXct` (data e hora).
#' @details
#' **Colunas do `"unificado"`:**
#' * `fonte_dataset`: `"A"` (Fato ou Boato) ou `"B"` (Aos Fatos).
#' * `rotulo_ia`: `"IA"` ou `"Tradicional"`. No Aos Fatos vem da tag editorial;
#'   no Fato ou Boato vem de regex no titulo (`fonte_rotulo_ia`) e nenhum item e IA.
#' * `veredito_original`, `veredito_binario` (`falso`, `parcialmente_falso`,
#'   `nao_falso`) e `fonte_veredito`.
#' * `categoria_tema` e `fonte_categoria_tema`.
#' * `vetor_midia`, `alvo_ataque`: estimados por dicionario sobre o titulo.
#'   `vetor_midia_texto_corrigido`, `alvo_ataque_texto_corrigido`: idem sobre o texto
#'   completo. **Heuristicas, ainda sem validacao humana.**
#' * `ciclo_eleitoral_estimado` e `dias_para_eleicao` (negativo = antes do 1o turno).
#' * `par_duplicado_provavel` e `par_duplicado_similaridade`: mesma alegacao nas duas fontes.
#'
#' Atencao: a tag "tradicional" do Aos Fatos recorta o ano eleitoral de 2022,
#' enquanto a tag de IA e tematica (2023-2026). Compare `dias_para_eleicao`
#' entre grupos so dentro de janelas equivalentes.
#' @examples
#' d <- politicai_dados()
#' table(d$rotulo_ia, d$veredito_binario)
#' @export
politicai_dados <- function(nome = c("unificado", "fato_ou_boato", "aos_fatos")) {
  nome <- match.arg(nome)
  arq <- c(unificado = "dataset_c_unificado.csv",
           fato_ou_boato = "dataset_a_fato_ou_boato.csv",
           aos_fatos = "dataset_b_aosfatos.csv")[[nome]]
  caminho <- system.file("extdata", arq, package = "politicAI", mustWork = TRUE)
  d <- utils::read.csv(caminho, encoding = "UTF-8", stringsAsFactors = FALSE)
  for (col in intersect(c("data_publicacao", "data_publicacao_checagem"), names(d)))
    d[[col]] <- as.Date(substr(d[[col]], 1, 10))
  if ("data_publicacao_timestamp" %in% names(d))
    d$data_publicacao_timestamp <- as.POSIXct(d$data_publicacao_timestamp, tz = "America/Sao_Paulo")
  d
}

#' Resultados dos testes de robustez da revisao
#'
#' Lista com qui-quadrado, V de Cramer, permutacao, Fisher e Holm por hipotese.
#' Requer o pacote `jsonlite`.
#' @return lista nomeada (uma entrada por teste).
#' @examples
#' \dontrun{names(politicai_robustez())}
#' @export
politicai_robustez <- function() {
  if (!requireNamespace("jsonlite", quietly = TRUE))
    stop("Instale o pacote 'jsonlite' para usar politicai_robustez().")
  jsonlite::read_json(system.file("extdata", "robustez_revisao.json",
                                  package = "politicAI", mustWork = TRUE),
                      simplifyVector = TRUE)
}
