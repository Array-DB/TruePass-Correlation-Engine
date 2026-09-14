export type DoDStatus = "pass" | "fail" | "blocked";

export interface DoDCheck {
  id: string;
  area: string;
  status: DoDStatus;
  detail: string;
  required: boolean;
}

export interface DoDAudit {
  implementation_complete: boolean;
  environment_verified: boolean;
  overall_pass: boolean;
  checks: DoDCheck[];
}

export function summarizeAudit(audit: DoDAudit): string {
  const passed = audit.checks.filter((check) => check.status === "pass").length;
  return `${passed}/${audit.checks.length} checks passed`;
}
