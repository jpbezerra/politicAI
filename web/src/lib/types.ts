/**
 * Tipos compartilhados pelo dashboard e pelo Sensor de IA.
 *
 * Distinção importante mantida em todo o app (ver docs/PRD.md, Seção 4.1):
 * - `RotuloIA` = rótulo de TEMÁTICA ("esta checagem é sobre conteúdo de IA?"),
 *   vindo de dados reais/editoriais do Dataset B/C.
 * - A predição do Sensor de IA (`SensorPrediction`) também é, na v0, um
 *   classificador de TEMÁTICA — não um detector de autoria. Isso é
 *   comunicado explicitamente na UI (`SENSOR_DISCLAIMER_V0`).
 */

export type RotuloIA = "IA" | "Tradicional";

export type FonteDataset = "A" | "B";

export interface SerieMensalPonto {
  mes: string; // "YYYY-MM"
  total: number;
  ia: number;
  tradicional: number;
}

export interface DistribuicaoFonte {
  fonte: string;
  n: number;
}

export interface DistribuicaoTema {
  tema: string;
  n: number;
  n_ia: number;
}

export interface DistribuicaoVeredito {
  veredito: string;
  n: number;
}

export interface DatasetCSummary {
  gerado_em: string;
  gerado_por: string;
  fonte_dados: string;
  aviso: string;
  datas_turno_1: Record<string, string>;
  resumo_geral: {
    n_total: number;
    n_ia: number;
    n_tradicional: number;
    pct_ia: number | null;
    n_rotulo_editorial_confiavel: number;
  };
  serie_mensal: SerieMensalPonto[];
  distribuicao_por_fonte: DistribuicaoFonte[];
  distribuicao_por_tema: DistribuicaoTema[];
  distribuicao_veredito: DistribuicaoVeredito[];
}

/** Status de uma "lente" do dashboard — usado para nunca exibir dado mockado como se fosse real. */
export type StatusLente = "real" | "em_construcao";

export interface LenteInfo {
  id: string;
  titulo: string;
  descricao: string;
  status: StatusLente;
  fonte: string;
}

/** Resposta da API de predição do Sensor de IA (`/api/sensor-ia`). */
export interface SensorPredictionSuccess {
  ok: true;
  rotulo: RotuloIA;
  probabilidade: number; // 0-1, probabilidade da classe "IA"
  confianca: "baixa" | "media" | "alta";
  termos_influentes?: string[];
  modelo_versao: string;
}

export interface SensorPredictionError {
  ok: false;
  erro: string;
}

export type SensorPredictionResponse =
  | SensorPredictionSuccess
  | SensorPredictionError;

/**
 * Índice de tendência de desinformação por IA (`GET /forecast/index`,
 * ver docs/PRD.md Seção 5.2). RF2.4 (contextualização com calendário
 * eleitoral) é representado por `mes_de_1_turno`/
 * `dias_para_1_turno_mais_proximo` por ponto e por `marcos_eleitorais` no
 * nível do índice — nunca uma data inventada quando
 * `calendario_disponivel` é `false` (ver models/README.md e
 * trend_index.py).
 */
export interface PontoIndiceTendencia {
  mes: string; // "YYYY-MM"
  volume_ia: number | null; // observado; null nos meses projetados
  volume_ia_projetado: number | null; // projetado; null nos meses observados
  limite_inferior: number | null;
  limite_superior: number | null;
  mes_de_1_turno: boolean;
  dias_para_1_turno_mais_proximo: number | null;
}

export interface MarcoEleitoral {
  ano: number;
  data_1_turno: string; // "YYYY-MM-DD"
  mes: string; // "YYYY-MM"
}

export interface IndiceTendenciaSuccess {
  ok: true;
  aviso: string;
  n_observacoes: number;
  metodo: "binomial_negativa" | "poisson" | "regressao_linear";
  calendario_disponivel: boolean;
  marcos_eleitorais: MarcoEleitoral[];
  pontos: PontoIndiceTendencia[];
}

export interface IndiceTendenciaError {
  ok: false;
  erro: string;
}

export type IndiceTendenciaResponse =
  | IndiceTendenciaSuccess
  | IndiceTendenciaError;
