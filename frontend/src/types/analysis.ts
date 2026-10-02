export type ValidationStatus = "verified" | "corrected" | "rejected";

export interface MatchScore {
  overall_score: number;
  score_label: string;
  required_score: number;
  preferred_score: number;
  required_weight?: number;
  preferred_weight?: number;
}

export interface Evidence {
  text: string | null;
  source_type: string | null;
  page_number: number | null;
  verified: boolean;
  confidence: number;
  status: ValidationStatus;
}

export interface SkillMatch {
  skill: string;
  similarity: number;
  evidence: Evidence;
  status: ValidationStatus;
}

export interface MissingSkill {
  skill: string;
  verified: boolean;
  status: ValidationStatus;
}

export interface Project {
  project: string;
  evidence: Evidence;
  status: ValidationStatus;
}

export interface Recommendation {
  text: string;
  grounded_in: string;
  status: ValidationStatus;
}

export interface ValidationSummary {
  total_claims: number;
  verified_claims: number;
  corrected_claims: number;
  rejected_claims: number;
}

export interface VerifiedAnalysis {
  score: MatchScore;
  strong_matches: SkillMatch[];
  partial_matches: SkillMatch[];
  missing_skills: MissingSkill[];
  relevant_projects: Project[];
  recommendations: Recommendation[];
  summary: string;
  summary_status: ValidationStatus;
  validation_summary: ValidationSummary;
}
