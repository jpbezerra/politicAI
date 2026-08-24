import { NextRequest, NextResponse } from "next/server";
import { predizerTematicaIA } from "@/lib/models-client";

/**
 * Proxy fino entre o front-end do Sensor de IA e o serviço `/models`
 * (FastAPI). Não implementa nenhuma lógica de predição aqui — só
 * encaminha e repassa erros de forma honesta (ver docs/PRD.md, RF4.1/RF4.3).
 */
export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  const texto = typeof body?.texto === "string" ? body.texto : "";

  const resultado = await predizerTematicaIA(texto);
  return NextResponse.json(resultado, { status: resultado.ok ? 200 : 422 });
}
