// src/ui/Select.tsx
import React from "react";

const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => (
    <select
      ref={ref}
      className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm ${className ?? ""}`}
      {...props}
    >
      {children}
    </select>
  )
);

Select.displayName = "Select";

export { Select };