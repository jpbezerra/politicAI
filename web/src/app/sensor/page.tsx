import Link from "next/link";
import { SensorForm } from "@/components/sensor-form";
import { DisclaimerBanner } from "@/components/disclaimer-banner";

export const metadata = {
  title: "Sensor de IA | Lentes contra a Desinformação",
};

export default function SensorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Sensor de IA</h1>
        <p className="mt-2 max-w-2xl text-black/70 dark:text-white/70">
          Cole um texto político-eleitoral (notícia, post, transcrição) e
          veja a estimativa do modelo.
        </p>
      </div>

      <DisclaimerBanner>
        <strong>Importante:</strong> a versão atual (v0) é um classificador
        de <em>temática</em> — treinado para reconhecer textos que{" "}
        <em>tratam de</em> desinformação envolvendo IA (deepfakes, áudio
        clonado, texto sintético), não um detector geral de{" "}
        <em>autoria</em> por IA. Um texto escrito inteiramente por um
        modelo de linguagem sobre um tema comum (ex.: economia) pode não
        ser identificado por esta versão. Ver{" "}
        <Link href="/metodologia" className="underline">
          metodologia
        </Link>{" "}
        para o roadmap do detector de autoria (v1).
      </DisclaimerBanner>

      <SensorForm />
    </div>
  );
}
