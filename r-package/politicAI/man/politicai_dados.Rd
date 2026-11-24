\name{politicai_dados}
\alias{politicai_dados}
\title{Carrega um dataset do estudo}
\usage{
politicai_dados(nome = c("unificado", "fato_ou_boato", "aos_fatos"))
}
\arguments{
\item{nome}{\code{"unificado"} (A + B harmonizados, 769 linhas), \code{"fato_ou_boato"} (TSE, 228) ou \code{"aos_fatos"} (541, sem texto completo).}
}
\value{\code{data.frame}; colunas de data como \code{Date}; no \code{"aos_fatos"}, \code{data_publicacao_timestamp} e \code{POSIXct} (data e hora).}
\description{
Le os CSVs distribuidos em \code{inst/extdata}. Formato e alvo sao estimados por
dicionarios de palavras e nao foram validados por codificadores humanos. A tag
"tradicional" do Aos Fatos recorta 2022 e a de IA vai de 2023 a 2026: compare
\code{dias_para_eleicao} so em janelas equivalentes.
}
\examples{
d <- politicai_dados()
table(d$rotulo_ia, d$veredito_binario)
}
