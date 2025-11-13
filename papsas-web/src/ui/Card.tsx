// src/ui/Card.tsx
export const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={`rounded-lg border bg-white p-5 shadow-sm ${className}`}>{children}</div>
);