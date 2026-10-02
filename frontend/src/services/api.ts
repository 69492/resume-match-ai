import type { VerifiedAnalysis } from "../types/analysis";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

async function request<T>(path: string, init: RequestInit): Promise<T> {
  let response: Response;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 120_000);
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, signal: controller.signal });
  } catch {
    window.clearTimeout(timeout);
    if (controller.signal.aborted) throw new Error("The analysis timed out. Please try again.");
    throw new Error("The backend is unavailable. Start the FastAPI server and try again.");
  }
  window.clearTimeout(timeout);
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body && typeof body.detail === "string" ? body.detail : "The analysis could not be completed.";
    throw new Error(detail);
  }
  return body as T;
}

function assertVerifiedAnalysis(value: unknown): asserts value is VerifiedAnalysis {
  if (!value || typeof value !== "object") throw new Error("The backend returned an invalid analysis response.");
  const result = value as Record<string, unknown>;
  const score = result.score as Record<string, unknown> | undefined;
  const arrays = ["strong_matches", "partial_matches", "missing_skills", "relevant_projects", "recommendations"];
  if (!score || typeof score.overall_score !== "number" || typeof score.score_label !== "string" || arrays.some((key) => !Array.isArray(result[key]))) {
    throw new Error("The backend returned an invalid analysis response.");
  }
  const summary = result.validation_summary as Record<string, unknown> | undefined;
  if (!summary || typeof summary.verified_claims !== "number" || typeof summary.corrected_claims !== "number" || typeof summary.rejected_claims !== "number") {
    throw new Error("The backend returned an invalid verification response.");
  }
}

export async function analyzeResume(resumeFile: File, jobDescriptionFile: File): Promise<VerifiedAnalysis> {
  const form = new FormData();
  form.append("resume", resumeFile);
  form.append("job_description", jobDescriptionFile);
  const result = await request<unknown>("/api/analyze", { method: "POST", body: form });
  assertVerifiedAnalysis(result);
  return result;
}
