"use client";

import { useState } from "react";
import Link from "next/link";
import type { SensorPredictionResponse } from "@/lib/types";
import { DisclaimerBanner } from "@/components/disclaimer-banner";

const TAMANHO_MINIMO = 20;
const TAMANHO_MAXIMO = 20000;

export function SensorForm() {
  const [texto, setTexto] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState<SensorPredictionResponse | null>(
    null,
  );

  async function analisar() {
    setCarregando(true);
    setResultado(null);
    try {
      const res = await fetch("/api/sensor-ia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto }),
      });
      const data: SensorPredictionResponse = await res.json();
      setResultado(data);
    } finally {
      setCarregando(false);
    }
  }

  const tamanho = texto.length;
  const abaixoDoMinimo = texto.trim().length < TAMANHO_MINIMO;
  const acimaDoMaximo = tamanho > TAMANHO_MAXIMO;

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="sensor-textarea" className="sr-only">
          Texto a analisar
        </label>
        <textarea
          id="sensor-textarea"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Cole aqui o texto de uma notícia, post ou transcrição do âmbito político-eleitoral..."
          rows={8}
          maxLength={TAMANHO_MAXIMO}
          aria-describedby="sensor-contador"
          className="w-full rounded-lg border border-black/15 bg-white p-3 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:bg-white/5 dark:focus:border-white/40"
        />
        <p
          id="sensor-contador"
          className={`mt-1 text-right text-xs ${
            acimaDoMaximo
              ? "text-red-600 dark:text-red-400"
              : "text-black/40 dark:text-white/40"
          }`}
        >
          {tamanho.toLocaleString("pt-BR")} / {TAMANHO_MAXIMO.toLocaleString("pt-BR")} caracteres
          {abaixoDoMinimo && tamanho > 0 ? ` · mínimo de ${TAMANHO_MINIMO} caracteres` : ""}
        </p>
      </div>

      <button
        onClick={analisar}
        disabled={carregando || abaixoDoMinimo || acimaDoMaximo}
        className="rounded-full bg-foreground px-5 py-2 text-sm font-medium text-background disabled:cursor-not-allowed disabled:opacity-40"
      >
        {carregando ? "Analisando..." : "Analisar texto"}
      </button>

      {resultado && !resultado.ok && (
        <DisclaimerBanner>{resultado.erro}</DisclaimerBanner>
      )}

      {resultado && resultado.ok && (
        <div className="space-y-3 rounded-xl border border-black/10 p-4 dark:border-white/10">
          <div className="flex items-center justify-between">
            <span className="text-sm text-black/60 dark:text-white/60">
              Resultado do modelo (v0 — classificador de temática)
            </span>
            <span className="text-xs text-black/40 dark:text-white/40">
              modelo {resultado.modelo_versao}
            </span>
          </div>

          <p className="text-lg font-semibold">
            {resultado.rotulo === "IA"
              ? "Provavelmente sobre conteúdo de IA"
              : "Sem indício de temática de IA"}
          </p>

          <div className="h-2 w-full overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
            <div
              className="h-full bg-amber-500"
              style={{ width: `${Math.round(resultado.probabilidade * 100)}%` }}
            />
          </div>
          <p className="text-xs text-black/50 dark:text-white/50">
            Probabilidade estimada: {Math.round(resultado.probabilidade * 100)}%
            {" · "}confiança {resultado.confianca}
          </p>

          {resultado.termos_influentes && resultado.termos_influentes.length > 0 && (
            <p className="text-xs text-black/50 dark:text-white/50">
              Termos mais influentes: {resultado.termos_influentes.join(", ")}
            </p>
          )}

          <DisclaimerBanner>
            Este modelo (v0) identifica se o texto é sobre desinformação
            envolvendo IA — não se o texto em si foi escrito por IA. Não é
            prova de veracidade nem de autoria. Ver{" "}
            <Link href="/metodologia" className="underline">
              metodologia
            </Link>
            .
          </DisclaimerBanner>
        </div>
      )}
    </div>
  );
}
