import React from "react";

type Props = {
  kind?: "error" | "success" | "info";
  title?: string;
  children?: React.ReactNode;
};

const styles: Record<NonNullable<Props["kind"]>, string> = {
  error: "border-red-300 bg-red-50 text-red-900",
  success: "border-green-300 bg-green-50 text-green-900",
  info: "border-blue-300 bg-blue-50 text-blue-900",
};

export default function Alert({ kind = "error", title, children }: Props) {
  return (
    <div className={`rounded-md border p-3 ${styles[kind]}`}> 
      {title && <div className="font-semibold mb-1">{title}</div>}
      <div className="text-sm">{children}</div>
    </div>
  );
}

