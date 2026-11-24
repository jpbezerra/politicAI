# politicAI (pacote R)

Dados reais do estudo *Fake news geradas por IA no contexto eleitoral brasileiro* (DataPol 2026 / SBTI).

```r
# install.packages("remotes")
remotes::install_github("jpbezerra/politicAI", subdir = "r-package/politicAI")
library(politicAI)
d <- politicai_dados()               # 769 checagens (A + B)
table(d$rotulo_ia, d$veredito_binario)
politicai_dados("aos_fatos")         # 541, sem texto completo
politicai_robustez()                 # testes de robustez (precisa de jsonlite)
```

Os CSVs vêm de `data/processed/` via `scripts/export_r_package_data.py`; rode-o de novo após regerar os dados.
**Limitação:** formato e alvo são heurísticas lexicais sem validação humana (ver artigo).
