import { z } from "zod";

/**
 * Validação de variáveis de ambiente usadas pelo `/web`, feita uma vez no
 * import deste módulo (falha cedo e com uma mensagem clara, em vez de um
 * erro genérico de `fetch` mais tarde se `MODELS_API_URL` estiver mal
 * configurada). Ver docs/PRD.md, backlog de melhorias, item "validação de
 * variáveis de ambiente".
 *
 * `MODELS_API_URL` é opcional (tem um default para desenvolvimento local),
 * mas quando definida precisa ser uma URL válida — um valor como
 * "localhost:8000" (sem esquema) ou uma string com espaço/typo falha aqui,
 * de forma explícita, em vez de gerar um erro de rede confuso no Sensor de IA.
 */
const envSchema = z.object({
  MODELS_API_URL: z
    .url({ message: "MODELS_API_URL precisa ser uma URL completa, ex.: http://localhost:8000" })
    .optional(),
});

function loadEnv() {
  const resultado = envSchema.safeParse({
    MODELS_API_URL: process.env.MODELS_API_URL,
  });

  if (!resultado.success) {
    const mensagens = resultado.error.issues
      .map((i) => `${i.path.join(".") || "MODELS_API_URL"}: ${i.message}`)
      .join("; ");
    throw new Error(
      `Configuração de ambiente inválida em web/.env.local — ${mensagens}. ` +
        "Ver web/README.md e web/.env.example.",
    );
  }

  return resultado.data;
}

export const env = loadEnv();
