export function DisclaimerBanner({ children }: { children: React.ReactNode }) {
  return (
    <div
      role="note"
      className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-200"
    >
      {children}
    </div>
  );
}
