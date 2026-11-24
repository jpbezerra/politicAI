test_that("tamanhos batem com o artigo", {
  expect_equal(nrow(politicai_dados("unificado")), 769)
  expect_equal(nrow(politicai_dados("fato_ou_boato")), 228)
  expect_equal(nrow(politicai_dados("aos_fatos")), 541)
  expect_equal(sum(politicai_dados()$rotulo_ia == "IA"), 122)
})
test_that("datas sao Date", {
  expect_s3_class(politicai_dados()$data_publicacao, "Date")
  expect_s3_class(politicai_dados("aos_fatos")$data_publicacao, "Date")
  expect_s3_class(politicai_dados("aos_fatos")$data_publicacao_timestamp, "POSIXct")
})
